import numpy as np

import simenv as sm


FPS = 50
SCALE = 30.0  # affects how fast-paced the game is, forces should be adjusted as well

MAIN_ENGINE_POWER = 13.0
SIDE_ENGINE_POWER = 0.6

INITIAL_RANDOM = 1000.0  # Set 1500 to make game harder

LANDER_POLY = [(-14, +17), (-17, 0), (-17, -10), (+17, -10), (+17, 0), (+14, +17)]
LEG_AWAY = 20
LEG_DOWN = 18
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
height = np.random.Generator.uniform(0, H / 2, size=(CHUNKS + 1,))
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
        angle=(i * 0.05),
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
