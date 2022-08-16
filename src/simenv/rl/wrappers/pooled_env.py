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
"""RL scene wrapper that handles pooling multiple maps"""

from collections import OrderedDict
from copy import deepcopy
from queue import Queue

import numpy as np
from gym import spaces
from stable_baselines3.common.vec_env.base_vec_env import VecEnv, VecEnvObs
from stable_baselines3.common.vec_env.util import copy_obs_dict, dict_to_obs, obs_space_info

from ...assets.light import LightSun
from ...scene import Scene
from ..rl_agents import RlComponent


class Map:
    def __init__(self, scene, root):
        self.scene = scene
        self.root = root

        agents = root.tree_filtered_descendants(lambda node: isinstance(node.rl_component, RlComponent))
        if len(agents) == 0:
            print("No agents found. At least one agent expected per map")
            return
        # TODO: Multiple agents per map?
        elif len(agents) > 1:
            print("Multiple agents found. Defaulting to first")

        self.agent = agents[0]
        self.active = True

    def show(self):
        self._set_active(True)

    def hide(self):
        self._set_active(False)

    def _set_active(self, active):
        self.scene.engine.run_command("SetNodeActive", node=self.root.name, active=active)
        self.active = active


class MapPool:
    def __init__(
        self,
        map_fn,
        n_maps=None,
        n_show=None,
        map_width=None,
        map_height=None,
        padding=None,
        frame_rate=None,
        frame_skip=None,
        **engine_kwargs,
    ):
        if n_maps is None:
            n_maps = 1
        if n_show is None:
            n_show = max(1, n_maps)
        if not n_maps % n_show == 0:
            desired = max(n_show, n_maps - (n_maps % n_show))
            print(f"Number of maps isn't a multiple of {n_show}. Setting n_maps to {desired}")
            n_maps = desired
        if map_width is None:
            map_width = 20
        if map_height is None:
            map_height = 20
        if padding is None:
            padding = 2
        self.n_maps = n_maps
        self.n_show = n_show

        self.scene = Scene(engine="Unity", **engine_kwargs)
        self.scene += LightSun()

        self.maps = []
        n_show_sqrt = int(np.ceil(np.sqrt(n_show)))
        for i in range(n_maps):
            root = map_fn(i)
            map_idx = i % n_show
            root.position += [
                (map_width + padding) * (map_idx % n_show_sqrt),
                0,
                (map_height + padding) * (map_idx // n_show_sqrt),
            ]
            self.scene += root
            map = Map(self.scene, root)
            self.maps.append(map)

        show_kwargs = {}
        if frame_rate is not None:
            show_kwargs["frame_rate"] = frame_rate
        if frame_skip is not None:
            show_kwargs["frame_skip"] = frame_skip
        self.scene.show(**show_kwargs)

        self.active_maps = Queue()
        self.inactive_maps = Queue()
        for i, map in enumerate(self.maps):
            if i < n_show:
                map.show()
                self.active_maps.put(map)
            else:
                map.hide()
                self.inactive_maps.put(map)

    def reset(self):
        for _ in range(self.n_show):
            prev = self.active_maps.get()
            prev.hide()
            self.inactive_maps.put(prev)

            next = self.inactive_maps.get()
            next.show()
            self.active_maps.put(next)

        self.scene.reset()

    @property
    def agents(self):
        agents = []
        for _ in range(self.n_show):
            map = self.active_maps.get()
            agents.append(map.agent)
            self.active_maps.put(map)
        return agents


class PooledEnvironment(VecEnv):
    def __init__(self, pool_fns):
        self.pools = [pool_fn() for pool_fn in pool_fns]
        agents = self.pools[0].agents
        agent = agents[0]
        self.action_space = None
        if agent.rl_component.discrete_actions is not None:
            self.action_space = agent.rl_component.discrete_actions
        elif agent.rl_component.box_actions is not None:
            self.action_space = agent.rl_component.box_actions
        if self.action_space is None:
            print("Action space not found. Does the environment contain an agent with an action space?")

        camera = agent.rl_component.camera_sensors[0].camera
        self.observation_space = spaces.Dict(
            {"camera": spaces.Box(low=0, high=255, shape=[3, camera.height, camera.width], dtype=np.uint8)}
        )

        VecEnv.__init__(self, len(self.pools) * len(agents), self.observation_space, self.action_space)

        self.keys, shapes, dtypes = obs_space_info(self.observation_space)
        self.buf_obs = OrderedDict(
            [(k, np.zeros((self.num_envs,) + tuple(shapes[k]), dtype=dtypes[k])) for k in self.keys]
        )
        self.buf_rews = np.zeros((self.num_envs,), dtype=np.float32)
        self.buf_dones = np.zeros((self.num_envs,), dtype=bool)
        self.buf_infos = [{} for _ in range(self.num_envs)]
        self.actions = None

    def step_async(self, actions: np.ndarray):
        self.actions = actions
        scene_offset = 0
        for pool in self.pools:
            agents = pool.agents
            action_dict = {}
            for i, action in enumerate(self.actions[scene_offset : scene_offset + len(agents)]):
                action_dict[agents[i].name] = int(action)
            pool.scene.engine.run_command_async("Step", action=action_dict)
            scene_offset += len(agents)

    def step_wait(self):
        scene_offset = 0
        for pool in self.pools:
            pool_done = True
            agents = pool.agents
            event = pool.scene.engine.get_response_async()
            for i, agent in enumerate(agents):
                agent_data = event["agents"][agent.name]
                self.buf_rews[scene_offset + i] = agent_data["reward"]
                self.buf_dones[scene_offset + i] = agent_data["done"]
                self.buf_infos[scene_offset + i] = {}
                pool_done = pool_done and agent_data["done"]
                camera = agent.rl_component.camera_sensors[0].camera
                obs = {"camera": np.array(agent_data["frames"][camera.name], dtype=np.uint8)}
                self._save_obs(scene_offset + i, obs)
            if pool_done:
                pool.reset()
            scene_offset += len(agents)
        return (self._obs_from_buf(), np.copy(self.buf_rews), np.copy(self.buf_dones), deepcopy(self.buf_infos))

    def reset(self):
        scene_offset = 0
        for pool in self.pools:
            pool.reset()
            agents = pool.agents
            event = pool.scene.step(return_frames=True, frame_skip=0)
            for i, agent in enumerate(agents):
                camera = agent.rl_component.camera_sensors[0].camera
                obs = {"camera": np.array(event["frames"][camera.name], dtype=np.uint8)}
                self._save_obs(scene_offset + i, obs)
            scene_offset += len(agents)
        return self._obs_from_buf()

    def close(self):
        self.scene.close()

    def _save_obs(self, index: int, obs: VecEnvObs):
        for key in self.keys:
            if key is None:
                self.buf_obs[key][index] = obs
            else:
                self.buf_obs[key][index] = obs[key]

    def _obs_from_buf(self) -> VecEnvObs:
        return dict_to_obs(self.observation_space, copy_obs_dict(self.buf_obs))

    def env_is_wrapped(self):
        return False

    def seed(self, seed):
        raise NotImplementedError()

    def env_method(self):
        raise NotImplementedError()

    def set_attr(self):
        raise NotImplementedError()

    def get_attr(self):
        raise NotImplementedError()
