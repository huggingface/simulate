## Examples for Simulate

The examples are organized by level of complexity or application. 
Currently, Simulate has the following examples running:

### Basic
* `create_and_save.py`: showcases basic scene assembly and saving as a gltf.
* `objects.py`: showcases the different objects we have in HuggingFace Simulate.
* `simple_physics.py`: showcases a basic falling object physics experiment.
* `structured_grid_test.py`: tests the StructuredGrid object in Simulate.

### Intermediate
* `playground.py`: showcases how to build a small world, add objects, and add actors to interact with the world. The actor must find a randomly colored box labelled `target`.
* `procgren_grid.py`: shows how we can create procgen grids from numpy arrays.
* `reward_example`: showcases different varieties of reward functions that can be added to one scene.
* `tmaze.py`: showcases building a small detailed maze for an agent to explore.

### Advanced
* `cartpole.py`: reimplements the famous cartpole example, with parallel execution and rendering.
* `lunarlander.py`: reimplements the famous lunar lander reinforcement learning environment.
* `mountaincar.py`: adds an impressive recreation of the mountain car Gym environment.

### Reinforcement Learning (RL)
There are multiple environments implemented with Stable Baselines 3 PPO:
* `sb3_basic_maze.py`:
* `sb3_collectables.py`:
* `sb3_move_boxes.py`:
* `sb3_procgen.py`:
* `sb3_visual_reward.py`:

## Backend Integrations
For more information on the backend integrations, see the relevant folders:
1. [Blender](../integrations/Blender)
2. [Godot](../integrations/Godot)
3. [Unity](../integrations/Unity)

The final backend, `pyvista` is installed via `setup.py`.
