# Copyright 2022 The HuggingFace Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import simulate as sm


scene = sm.Scene(engine="unity")
scene += sm.LightSun(name="sun", position=[0, 20, 0], intensity=0.9)

wood_mat = sm.Material(base_color=[0.28, 0.2, 0.14])
grass_mat = sm.Material(base_color=[0, 0.21, 0.09])
road_mat = sm.Material(base_color=[0.1, 0.1, 0.1])

scene += sm.Box(name="road", position=[0, 0.3, 12.5], bounds=[30, 0.1, 5], material=road_mat, with_collider=True)
scene += sm.Box(name="grass", position=[0, 0, 0], bounds=[30, 0.5, 30], material=grass_mat, with_collider=True)
scene += sm.Box(name="floor", position=[0, 0.5, -6.925], bounds=[15, 0.5, 15], material=wood_mat, with_collider=True)
scene += sm.Box(
    name="wall1",
    position=[0, 2.25, -13.87],
    rotation=[90, 0, 0],
    bounds=[14, 0.5, 3],
    material=wood_mat,
    with_collider=True,
)
scene += sm.Box(
    name="wall2",
    position=[0, 2.25, 0],
    rotation=[90, 0, 0],
    bounds=[14, 0.5, 3],
    material=wood_mat,
    with_collider=True,
)
scene += sm.Box(
    name="wall3",
    position=[6.75, 2.25, -6.925],
    rotation=[90, 90, 0],
    bounds=[13.5, 0.5, 3],
    material=wood_mat,
    with_collider=True,
)
scene += sm.Box(
    name="wall4",
    position=[-6.75, 2.25, -6.925],
    rotation=[90, 90, 0],
    bounds=[13.5, 0.5, 3],
    material=wood_mat,
    with_collider=True,
)

scene += sm.Asset.create_from(
    "simulate-explorer/public-test/bag/1b9ef45fefefa35ed13f430b2941481.glb",
    name="bag1",
    position=[-6.36, 1.17, -6.4],
    rotation=[-17, 77, 4],
)
scene += sm.Asset.create_from(
    "simulate-explorer/public-test/bag/1b84dededd445058e44a5473032f38f.glb",
    name="bag2",
    position=[-6.36, 1.23, -6.13],
    rotation=[-40, 121, 15],
)
scene += sm.Asset.create_from(
    "simulate-explorer/public-test/camera/1ab3abb5c090d9b68e940c4e64a94e1e.glb",
    name="camera_asset",
    position=[-5.83, 0.94, -13.23],
    rotation=[0, -103, 0],
)
scene += sm.Asset.create_from(
    "simulate-explorer/public-test/display/1a9e1fb2a51ffd065b07a27512172330.glb",
    name="display",
    position=[-5.73, 1.94, -9.08],
    rotation=[0, -101, 0],
)
scene += sm.Asset.create_from(
    "simulate-explorer/public-test/table/1a00aa6b75362cc5b324368d54a7416f.glb",
    name="table1",
    position=[4.42, 0.93, -11.56],
    rotation=[-0, 171, 0],
    scaling=[3, 3, 3],
)
scene += sm.Asset.create_from(
    "simulate-explorer/public-test/table/1a1fb603583ce36fc3bd24f986301745.glb",
    name="table2",
    position=[-5.63, 1.3, -8.9],
    rotation=[0, 90, 0],
    scaling=[3, 3, 3],
)
scene += sm.Asset.create_from(
    "simulate-explorer/public-test/table/1a2abbc9712e2fffc3bd24f986301745.glb",
    name="table3",
    position=[-0.09, 1.12, -6.37],
    rotation=[0, 2, 0],
    scaling=[3, 3, 3],
)
scene += sm.Asset.create_from(
    "simulate-explorer/public-test/sofa/1a4a8592046253ab5ff61a3a2a0e2484.glb",
    name="sofa1",
    position=[4.03, 1.3, -9.09],
    rotation=[0, -6, 0],
    scaling=[3, 3, 3],
)
scene += sm.Asset.create_from(
    "simulate-explorer/public-test/sofa/1a4a8592046253ab5ff61a3a2a0e2484.glb",
    name="sofa2",
    position=[1.71, 1.3, -11.54],
    rotation=[0, -99, 0],
    scaling=[3, 3, 3],
)
scene += sm.Asset.create_from(
    "simulate-explorer/public-test/pot/1a1a0794670a2114d6bef0ac9b3a5962.glb", name="pot1", position=[0, 1.93, -5.97]
)
scene += sm.Asset.create_from(
    "simulate-explorer/public-test/pot/1a03376343b2e4f0c27d3c9a6f742a5e.glb",
    name="pot2",
    position=[-5.11, 1.65, -1.35],
    scaling=[2, 2, 2],
)
scene += sm.Asset.create_from(
    "simulate-explorer/public-test/pot/1a03376343b2e4f0c27d3c9a6f742a5e.glb",
    name="pot3",
    position=[5.29, 1.65, -1.3],
    scaling=[2, 2, 2],
)
scene += sm.Asset.create_from(
    "simulate-explorer/public-test/lamp/1a5ebc8575a4e5edcc901650bbbbb0b5.glb",
    name="lamp",
    position=[-6.13, 2, -7.77],
    rotation=[0, -68, 0],
)
scene += sm.Asset.create_from(
    "simulate-explorer/public-test/airplane/1a04e3eab45ca15dd86060f189eb133.glb",
    name="airplane",
    position=[5.57, 1.45, 12.35],
    rotation=[0, 97, 0],
    scaling=[5, 5, 5],
)

actor = sm.Asset.create_from(
    "simulate-explorer/public-test/pot/1a03376343b2e4f0c27d3c9a6f742a5e.glb",
    name="actor",
    is_actor=True,
    position=[0, 1.65, -1.35],
    scaling=[2, 2, 2],
)
actor += sm.Collider(
    name="actor_collider",
    type="box",
    bounding_box=[0.25, 1, 0.25],
)
actor.physics_component = sm.RigidBodyComponent(
    mass=1, constraints=["freeze_rotation_x", "freeze_rotation_z", "freeze_position_y"]
)
actor.actuator = sm.Actuator(
    n=3,
    mapping=[
        sm.ActionMapping("change_rotation", axis=[0, 1, 0], amplitude=-10),
        sm.ActionMapping("change_rotation", axis=[0, 1, 0], amplitude=10),
        sm.ActionMapping("change_position", axis=[1, 0, 0], amplitude=0.1),
    ],
)
scene += actor
env = sm.RLEnv(scene, frame_skip=1)

scene.show()
scene.reset()
for i in range(1000):
    action = scene.actors[0].action_space.sample()
    # obs, reward, done = scene.step()
    print(i, action)
    env.step([action])

scene.close()
