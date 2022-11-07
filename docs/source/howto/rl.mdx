<!--Copyright 2022 The HuggingFace Team. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
-->

# Using 🤗 Simulate to learn Agent behaviors with Stable-Baselines3


We provide several example RL integrations with the Stable-Baselines3 (LINK) library. To install this dependancy use `pip install simulate[sb3]`.

Including:
* Learning to navigate in a simple T-Maze
* Collecting objects
* Navigating in procedurally generated mazes
* Physical interaction with movable objects
* Reward functions based on line of sight observation of objects.


## Learning to navigate in a simple T-Maze
<img class="!m-0 !border-0 !dark:border-0 !shadow-none !max-w-lg w-[600px]" src="https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/simulate/simulate_sb3_basic_maze.png"/>


Example: [`sb3_basic_maze.py`](https://github.com/huggingface/simulate/examples/rl/sb3_basic_maze.py)

Objective: Navigate to a spherical object in a simple T-Maze. Upon object collection, the environment resets.

Actors: An EgoCentric Camera Actor (LINK) equipped with a monocular camera.

Observation space: 
- An RGB camera of shape (3, 40, 40)  (C, H, W) in uint8 format.
  
Action space:
- A discrete action space with 3 possible actions
- Turn left 10 degrees
- Turn right 10 degrees
- Move forward

Reward function:
- A dense reward based on improvement in best euclidean distance to the object
- A sparse reward of +1 when the object is collected
- A timeout penaly of -1 if the agent does not reach the object in 200 time-steps

Parallel: 4 independent instances of the same environment configuration. 


## Collecting objects
<img class="!m-0 !border-0 !dark:border-0 !shadow-none !max-w-lg w-[600px]" src="https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/simulate/simulate_sb3_collectables.png"/>


Example: [`sb3_collectables.py`](https://github.com/huggingface/simulate/examples/rl/sb3_collectables.py)

Objective: Collect all 20 objects in a large square room.

Actors: An EgoCentric Camera Actor (LINK) equipped with a monocular camera.

Observation space: 
- An RGB camera of shape (3, 40, 40)  (C, H, W) in uint8 format.
  
Action space:
- A discrete action space with 3 possible actions
- Turn left 10 degrees
- Turn right 10 degrees
- Move forward

Reward function:
- A sparse reward of +1 when an object is collected
- A timeout penaly of -1 if the agent does not reach the object in 500 time-steps

Parallel: 4 independent instances of the same environment configuration. 

## Navigating in procedurally generated mazes
<img class="!m-0 !border-0 !dark:border-0 !shadow-none !max-w-lg w-[600px]" src="https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/simulate/simulate_sb3_procgen.png"/>


Example: [`sb3_procgen.py`](https://github.com/huggingface/simulate/examples/rl/sb3_procgen.py)

Objective: Navigate to an object in a 3D maze, when the object is collected the environment resets.

Actors: An EgoCentric Camera Actor (LINK) equipped with a monocular camera

Observation space: 
- An RGB camera of shape (3, 40, 40)  (C, H, W) in uint8 format.

Action space:
- A discrete action space with 3 possible actions
- Turn left 10 degrees
- Turn right 10 degrees
- Move forward

Reward function:
- A sparse reward of +1 when the object is reached
- A timeout penaly of -1 if the agent does not reach the object in 500 time-steps

Parallel: 4 independent instances of randomly generated environment configurations.


## Physical interaction with movable objects
<img class="!m-0 !border-0 !dark:border-0 !shadow-none !max-w-lg w-[600px]" src="https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/simulate/simulate_sb3_move_boxes.png"/>


Example: [`sb3_move_boxes.py`](https://github.com/huggingface/simulate/examples/rl/sb3_move_boxes.py)

Objective: Push boxes in a room near to each other.

Actors: An EgoCentric Camera Actor (LINK) equipped with a monocular camera

Observation space: 
- An RGB camera of shape (3, 40, 40)  (C, H, W) in uint8 format.
  
Action space:
- A discrete action space with 3 possible actions
- Turn left 10 degrees
- Turn right 10 degrees
- Move forward

Reward function:
- A reward for moving the red and yellow boxes close to eachother
- A reward for moving the green and white boxes close to eachother
- A timeout penaly of -1 if the agent does not reach the object in 100 time-steps

Parallel: 16 independent instances of the same environment configuration.


## Reward functions based on line of sight observation of objects.
<img class="!m-0 !border-0 !dark:border-0 !shadow-none !max-w-lg w-[600px]" src="https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/simulate/simulate_sb3_see_reward.png"/>


Example: [`sb3_visual_reward.py`](https://github.com/huggingface/simulate/examples/rl/sb3_visual_reward.py)

Objective: Move the agent so the box is within the agents its field of view

Actors: An EgoCentric Camera Actor (LINK) equipped with a monocular camera

Observation space: 
- An RGB camera of shape (3, 40, 40)  (C, H, W) in uint8 format.
  
Action space:
- A discrete action space with 3 possible actions
- Turn left 10 degrees
- Turn right 10 degrees
- Move forward

Reward function:
- A sparse reward for moving the box within a 60 degree fov cone in front of the agent.
- A timeout penaly of -1 if the agent does not reach the object in 100 time-steps

Parallel: 4 independent instances of the same environment configuration.