<!--Copyright 2022 The HuggingFace Team. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
-->

# Intermediate examples in Simulate

These examples are intended to showcase advanced individual features, building visually appealing scenes, and some interactive elements (like rewards and actuators).

* [`playground.py`](https://github.com/huggingface/simulate/examples/intermediate/playground.py): showcases how to build a small world, add objects, and add actors to interact with the world. The actor must find a randomly colored box labelled `target`.
* [`procgren_grid.py`](https://github.com/huggingface/simulate/examples/intermediate/procgren_grid.py) (coming soon): shows how we can create procgen grids from numpy arrays.
* [`reward_example`](https://github.com/huggingface/simulate/examples/intermediate/reward_example.py): showcases different varieties of reward functions that can be added to one scene.
* [`tmaze.py`](https://github.com/huggingface/simulate/examples/intermediate/tmaze.py): showcases building a small detailed maze for an agent to explore.