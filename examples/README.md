## Examples for SimEnv

Here we can track the high level status of the examples

| File                              | Desciption                                 | Status | Comments                                   | P.O.C. |
|-----------------------------------|--------------------------------------------|--------|--------------------------------------------| ----------|
| `benchmark.py`                    | Build and run Unity example                | TBD    | Requires Unity / Requires pre-built env    | Ed? |
| `blender_example.py`              | Build simple blender example               | TBD    | Requires Blender                           | TODO |
| `collectables.py`                 | Collectable objects and associated rewards | TBD    |                                            |      | 
| `duplicate_envs.py`               |                                            | Bug    | Requires Unity, Has an error in `step()`, `self.client.sendall(bytes) OSError: [Errno 9] Bad file descriptor` |      | 
| `four_boxes_example.py`           | Create boxes & different reward functions  | TBD    | Requires Unity                             |      | 
| `gltf_loading_test.py`            | Create simple box and render from          | TBD    | Requires acces to hf org `simenv-tests`    |      | 
| `helloworld.py`                   | Creates a basic scene and saves as gltf    | TBD    |                                            |      | 
| `parralel_envs.py`                |                                            | TBD    | Requires Unity                             |      | 
| `playground.py`                   |                                            | TBD    | To-do                                      |      | 
| `procgen_grid.py`                 |                                            | TBD    | To-do                                      |      | 
| `procgen_prims.py`                |                                            | TBD    | To-do                                      |      | 
| `reward_examples.py`              |                                            | TBD    | To-do                                      |      | 
| `reward_see.py`                   |                                            | TBD    | To-do                                      |      | 
| `sb3_training_parallel_simenv.py` |                                            | TBD    | To-do                                      |      | 
| `structured_grid_test.py`         |                                            | TBD    | To-do                                      |      | 
| `tmaze.py`                        |                                            | TBD    | To-do                                      |      | 

## Backend Integrations
For more information on the backend integrations, see the relevant folders:
1. [Blender](../integrations/Blender)
2. [Godot](../integrations/Godot)
3. [Unity](../integrations/Unity)

The final backend, `pyvista` is installed via `setup.py`.