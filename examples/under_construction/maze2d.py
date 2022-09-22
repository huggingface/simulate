# from .maze2denvs import LARGE_MAZE, LARGE_MAZE_EVAL, MEDIUM_MAZE, MEDIUM_MAZE_EVAL, U_MAZE, U_MAZE_EVAL, OPEN, parse_maze, WALL, GOAL, EMPTY

import simulate as sm


scene = sm.Scene()

scene += sm.Plane(i_size=40, j_size=40, position=[0, 0, -0.1], material=sm.Material())
scene += sm.Sphere(name="particle", position=[1.2, 0, 1.2], radius=0.1, material=sm.Material([0.0, 0.0, 1.0, 0.0]))

OPEN = "#######\\" + "#OOOOO#\\" + "#OOGOO#\\" + "#OOOOO#\\" + "#######"

LARGE_MAZE = (
    "############\\"
    + "#OOOO#OOOOO#\\"
    + "#O##O#O#O#O#\\"
    + "#OOOOOO#OOO#\\"
    + "#O####O###O#\\"
    + "#OO#O#OOOOO#\\"
    + "##O#O#O#O###\\"
    + "#OO#OOO#OGO#\\"
    + "############"
)

maze_str = LARGE_MAZE

lines = maze_str.strip().split("\\")
for h, row in enumerate(lines):
    for w, el in enumerate(row):
        if el == "#":
            scene += sm.Box(bounds=(1, 0.4, 1), position=(w, 0, h), material=sm.Material([0.7, 0.5, 0.3, 1]))

scene.show()
print(scene)

####################


# def point_maze(maze_str):
#     maze_arr = parse_maze(maze_str)

#     mjcmodel = MJCModel('point_maze')
#     mjcmodel.root.compiler(inertiafromgeom="true", angle="radian", coordinate="local")
#     mjcmodel.root.option(timestep="0.01", gravity="0 0 0", iterations="20", integrator="Euler")
#     default = mjcmodel.root.default()
#     default.joint(damping=1, limited='false')
#     default.geom(friction=".5 .1 .1", density="1000", margin="0.002", condim="1", contype="2", conaffinity="1")

#     asset = mjcmodel.root.asset()
#     asset.texture(type="2d",name="groundplane",builtin="checker",rgb1="0.2 0.3 0.4",rgb2="0.1 0.2 0.3",width=100,height=100)
#     asset.texture(name="skybox",type="skybox",builtin="gradient",rgb1=".4 .6 .8",rgb2="0 0 0",
#                width="800",height="800",mark="random",markrgb="1 1 1")
#     asset.material(name="groundplane",texture="groundplane",texrepeat="20 20")
#     asset.material(name="wall",rgba=".7 .5 .3 1")
#     asset.material(name="target",rgba=".6 .3 .3 1")

#     visual = mjcmodel.root.visual()
#     visual.headlight(ambient=".4 .4 .4",diffuse=".8 .8 .8",specular="0.1 0.1 0.1")
#     visual.map(znear=.01)
#     visual.quality(shadowsize=2048)

#     worldbody = mjcmodel.root.worldbody()
#     worldbody.geom(name='ground',size="40 40 0.25",pos="0 0 -0.1",type="plane",contype=1,conaffinity=0,material="groundplane")

#     particle = worldbody.body(name='particle', pos=[1.2,1.2,0])
#     particle.geom(name='particle_geom', type='sphere', size=0.1, rgba='0.0 0.0 1.0 0.0', contype=1)
#     particle.site(name='particle_site', pos=[0.0,0.0,0], size=0.2, rgba='0.3 0.6 0.3 1')
#     particle.joint(name='ball_x', type='slide', pos=[0,0,0], axis=[1,0,0])
#     particle.joint(name='ball_y', type='slide', pos=[0,0,0], axis=[0,1,0])

#     worldbody.site(name='target_site', pos=[0.0,0.0,0], size=0.2, material='target')

#     width, height = maze_arr.shape
#     for w in range(width):
#         for h in range(height):
#             if maze_arr[w,h] == WALL:
#                 worldbody.geom(conaffinity=1,
#                                type='box',
#                                name='wall_%d_%d'%(w,h),
#                                material='wall',
#                                pos=[w+1.0,h+1.0,0],
#                                size=[0.5,0.5,0.2])

#     actuator = mjcmodel.root.actuator()
#     actuator.motor(joint="ball_x", ctrlrange=[-1.0, 1.0], ctrllimited=True, gear=100)
#     actuator.motor(joint="ball_y", ctrlrange=[-1.0, 1.0], ctrllimited=True, gear=100)

#     return mjcmodel

####################
