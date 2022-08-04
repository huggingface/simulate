import pdb

import numpy as np

import simenv as sm


FPS = 50
SCALE = 30.0  # affects how fast-paced the game is, forces should be adjusted as well

MAIN_ENGINE_POWER = 13.0
SIDE_ENGINE_POWER = 0.6

INITIAL_RANDOM = 1000.0  # Set 1500 to make game harder

LANDER_POLY = np.array([(-14, 0, +17), (-17, 0, 0), (-17,0, -10), (+17,0,-10), (+17,0, 0), (+14,0, +17)])/SCALE
LEG_AWAY = 20
LEG_DOWN = -7
LEG_ANGLE = 0.25 # radions
LEG_W, LEG_H = 2, 8
LEG_SPRING_TORQUE = 40

SIDE_ENGINE_HEIGHT = 14.0
SIDE_ENGINE_AWAY = 12.0

VIEWPORT_W = 600
VIEWPORT_H = 400

W = VIEWPORT_W / SCALE
H = VIEWPORT_H / SCALE

# terrain
CHUNKS = 11
height = np.random.uniform(0, H / 2, size=(CHUNKS + 1,))
chunk_x = [W / (CHUNKS - 1) * i for i in range(CHUNKS)]
helipad_x1 = chunk_x[CHUNKS // 2 - 1]
helipad_x2 = chunk_x[CHUNKS // 2 + 1]
helipad_y = H / 4
height[CHUNKS // 2 - 2] = helipad_y
height[CHUNKS // 2 - 1] = helipad_y
height[CHUNKS // 2 + 0] = helipad_y
height[CHUNKS // 2 + 1] = helipad_y
height[CHUNKS // 2 + 2] = helipad_y
smooth_y = [0.33 * (height[i - 1] + height[i + 0] + height[i + 1]) for i in range(CHUNKS)]

# Add sm scene
sc = sm.Scene()

LEG_RIGHT_POLY =  np.array([(LEG_AWAY, 0,  LEG_DOWN),
                  (LEG_AWAY + LEG_H*np.sin(LEG_ANGLE),      0, LEG_DOWN - LEG_H * np.cos(LEG_ANGLE)),
                  (LEG_AWAY + LEG_H*np.sin(LEG_ANGLE) + LEG_W* np.sin(np.pi/2 - LEG_ANGLE), 0, LEG_DOWN - LEG_H * np.cos(LEG_ANGLE) + LEG_W*np.cos(np.pi/2 - LEG_ANGLE) ),
                  (LEG_AWAY +LEG_W* np.sin(np.pi/2 - LEG_ANGLE), 0, LEG_DOWN + LEG_W * np.cos(np.pi/2 - LEG_ANGLE))]) / SCALE

LEG_LEFT_POLY = [(-x, y,z) for x,y,z in LEG_RIGHT_POLY]

def shift_polygon(polygon, shift):
    shifted_poly = [(x+shift[0], y+shift[1], z+shift[2]) for x,y,z in polygon]
    return shifted_poly

lander_init_pos = (10, 0, 10) + np.random.uniform(0,5,3)
lander_init_pos[1] = 0

lander = sm.Polygon(points=shift_polygon(LANDER_POLY, lander_init_pos))
lander.mesh.extrude((0,1,0), capping=True, inplace=True)


r_leg = sm.Polygon(points=shift_polygon(LEG_RIGHT_POLY, lander_init_pos))
r_leg.mesh.extrude((0,1,0), capping=True, inplace=True)

l_leg = sm.Polygon(points=shift_polygon(LEG_LEFT_POLY, lander_init_pos))
l_leg.mesh.extrude((0,1,0), capping=True, inplace=True)

land_poly = [(chunk_x[0], 0, smooth_y[0]-3)] + [(x, 0, y) for x, y in zip(chunk_x, smooth_y)] + [(chunk_x[-1], 0, smooth_y[0]-3)]

land = sm.Polygon(points=land_poly)
land.mesh.extrude((0,1,0), capping=True, inplace=True)

sc += lander
sc += r_leg
sc += l_leg
sc += land
sc.show()


import ipdb; pdb.set_trace()
moon = world.CreateStaticBody(shapes=edgeShape(vertices=[(0, 0), (W, 0)]))
sky_polys = []
for i in range(CHUNKS - 1):
    p1 = (chunk_x[i], smooth_y[i])
    p2 = (chunk_x[i + 1], smooth_y[i + 1])
    moon.CreateEdgeFixture(vertices=[p1, p2], density=0, friction=0.1)
    sky_polys.append([p1, p2, (p2[0], H), (p1[0], H)])

moon.color1 = (0.0, 0.0, 0.0)
moon.color2 = (0.0, 0.0, 0.0)

initial_y = VIEWPORT_H / SCALE
lander = world.CreateDynamicBody(
    position=(VIEWPORT_W / SCALE / 2, initial_y),
    angle=0.0,
    fixtures=fixtureDef(
        shape=polygonShape(vertices=[(x / SCALE, y / SCALE) for x, y in LANDER_POLY]),
        density=5.0,
        friction=0.1,
        categoryBits=0x0010,
        maskBits=0x001,  # collide only with ground
        restitution=0.0,
    ),  # 0.99 bouncy
)
lander.color1 = (128, 102, 230)
lander.color2 = (77, 77, 128)
lander.ApplyForceToCenter(
    (
        np.random.Generator.uniform(-INITIAL_RANDOM, INITIAL_RANDOM),
        np.random.Generator.uniform(-INITIAL_RANDOM, INITIAL_RANDOM),
    ),
    True,
)

legs = []
for i in [-1, +1]:
    leg = world.CreateDynamicBody(
        position=(VIEWPORT_W / SCALE / 2 - i * LEG_AWAY / SCALE, initial_y),
        angle=(i * LEG_ANGLE),
        fixtures=fixtureDef(
            shape=polygonShape(box=(LEG_W / SCALE, LEG_H / SCALE)),
            density=1.0,
            restitution=0.0,
            categoryBits=0x0020,
            maskBits=0x001,
        ),
    )
    leg.ground_contact = False
    leg.color1 = (128, 102, 230)
    leg.color2 = (77, 77, 128)
    rjd = revoluteJointDef(
        bodyA=lander,
        bodyB=leg,
        localAnchorA=(0, 0),
        localAnchorB=(i * LEG_AWAY / SCALE, LEG_DOWN / SCALE),
        enableMotor=True,
        enableLimit=True,
        maxMotorTorque=LEG_SPRING_TORQUE,
        motorSpeed=+0.3 * i,  # low enough not to jump back into the sky
    )
    if i == -1:
        rjd.lowerAngle = +0.9 - 0.5  # The most esoteric numbers here, angled legs have freedom to travel within
        rjd.upperAngle = +0.9
    else:
        rjd.lowerAngle = -0.9
        rjd.upperAngle = -0.9 + 0.5
    leg.joint = world.CreateJoint(rjd)
    legs.append(leg)

drawlist = [lander] + legs
