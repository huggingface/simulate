from matplotlib import scale
import simenv as sm
import numpy as np
from simenv.assets.object import ProcGenPrimsMaze3D
from simenv.assets.procgen.prims import generate_prims_maze
import random
scene = sm.Scene(engine="Unity")

blue_material = sm.Material(base_color=(0, 0, 0.8))
yellow_material = sm.Material(base_color=(0.95, 0.83, 0.28))
green_material = sm.Material(base_color=(0.2, 0.8, 0.2))

maze_width = 10
maze_depth = 10
n_objects = 10

for i in range(4):
    for j in range(2):
        maze = ProcGenPrimsMaze3D(10, 10, wall_material=yellow_material)
        maze += sm.Box(position=[0, 0, 0], bounds=[0.0,maze_width, 0, 0.1, 0.0, maze_depth], material=blue_material)
        agent = sm.SimpleRlAgent(camera_width=64, camera_height=40, position=[maze_width/2.0 +0.5, 0.0, maze_depth/2.0 +0.5])
        maze += agent

        for r in range(n_objects):
            collectable = sm.Sphere(position=[random.randint(0,maze_width-1)+0.5, 0.5, random.randint(0,maze_depth-1)+0.5], radius=0.2, material=green_material)
            maze += collectable
            reward_function = sm.RewardFunction(
                type="sparse",
                entity_a=agent,
                entity_b=collectable,
                distance_metric="euclidean",
                threshold=1.0,
                is_terminal=False,
                is_collectable=True
            )
            agent.add_reward_function(reward_function)

        timeout_reward_function = sm.RewardFunction(
            type="timeout",
            entity_a=agent,
            entity_b=agent,
            distance_metric="euclidean",
            threshold=200,
            is_terminal=True,
            scalar=-1.0,
        )
        
        agent.add_reward_function(timeout_reward_function)
        maze = maze.translate_x(i*11.0).translate_z(j*11.0)
        scene.engine.add_to_pool(maze)

scene.show(n_maps=4)
#scene.activate(16)

input("Press enter to continue")
scene.close()