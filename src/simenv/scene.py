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

# Lint as: python3
""" A simenv Scene - Host a level or Scene."""
import itertools
from typing import Any, List, Optional, Tuple, Union

from .assets import Asset, Camera, Light, Object3D
from .assets.anytree import RenderTree
from .engine import BlenderEngine, GodotEngine, PyVistaEngine, UnityEngine
from .rl import RlComponent


try:
    from gym import Env
except ImportError:

    class Env:
        pass  # Dummy class if gym is not here


class Scene(Asset, Env):
    """A Scene is the main place to add objects and object tree.
    In addition to a root node, it has an engine that can be used to diplay and interact with the scene.

    Parameters
    ----------

    Returns
    -------

    Examples
    --------
    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        engine: Optional[str] = "pyvista",
        name: Optional[str] = None,
        created_from_file: Optional[str] = None,
        position: Optional[List[float]] = None,
        rotation: Optional[List[float]] = None,
        scaling: Optional[Union[float, List[float]]] = None,
        parameters: Optional[Any] = None,
        state: Optional[Any] = None,
        transformation_matrix=None,
        children=None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            position=position,
            rotation=rotation,
            scaling=scaling,
            transformation_matrix=transformation_matrix,
            children=children,
        )
        self.engine = None
        if engine is not None:
            engine = engine.lower()
        if engine == "unity":
            self.engine = UnityEngine(self, **kwargs)
        elif engine == "godot":
            self.engine = GodotEngine(self)
        elif engine == "blender":
            self.engine = BlenderEngine(self)
        elif engine == "pyvista" or engine is None:
            self.engine = PyVistaEngine(self, **kwargs)
        elif engine is not None:
            raise ValueError("engine should be selected in the list [None, 'unity', 'godot', 'blender', 'pyvista']")

        self.parameters = None
        self.state = None

        self._built = False
        self._created_from_file = created_from_file
        self._n_agents = None

    def __len__(self):
        return len(self.tree_descendants)

    def __repr__(self):
        spacer = "\n" if len(self) else ""
        return f"Scene(dimensionality={self.dimensionality}, engine='{self.engine}'){spacer}{RenderTree(self).print_tree()}"

    def show(self, **engine_kwargs):
        """Render the Scene using the engine."""
        n_maps = engine_kwargs.get("n_maps", None)
        if n_maps is not None:
            self._n_agents = n_maps
        self.engine.show(**engine_kwargs)

    def clear(self):
        """Remove all assets in the scene."""
        self.tree_children = []
        return self

    def close(self):
        self.engine.close()

    @property
    def lights(self):
        """Tuple with all Light in the Scene"""
        return self.tree_filtered_descendants(lambda node: isinstance(node, Light))

    @property
    def cameras(self):
        """Tuple with all Camera in the Scene"""
        return self.tree_filtered_descendants(lambda node: isinstance(node, Camera))

    @property
    def objects(self):
        """Tuple with all Object3D in the Scene"""
        return self.tree_filtered_descendants(lambda node: isinstance(node, Object3D))

    ###############################
    # RL engines specific methods #
    ###############################

    @property
    def agents(self) -> Tuple[Asset]:
        return self.tree_filtered_descendants(lambda node: isinstance(node.rl_component, RlComponent))


    @property
    def num_agents(self) -> int:
        return self.n_agents

    @property
    def is_multiagent(self) -> bool:
        return self.n_agents > 1

    @property
    def n_agents(self) -> int:
        if self._n_agents is None:
            self._n_agents = len(self.agents)  # potentially expensive operation
        return self._n_agents

    @property
    def observation_space(self):
        if self.engine.action_space is not None:
            return self.engine.observation_space
        agents = self.agents
        if agents:
            return agents[0].observation_space
        return None

    @property
    def action_space(self):
        if self.engine.action_space is not None:
            return self.engine.action_space
        agents = self.agents
        if agents:
            return agents[0].action_space
        return None

    def reset(self):
        """Reset the environment / episode"""
        self.engine.reset()
        obs = self.engine.get_obs()
        if self.n_agents == 1:
            return obs[0]
        return obs

    def step(self, action):
        """Step the Scene"""

        if self.n_agents == 1:
            action = [int(action)]

        self.engine.step(action)

        obs = self.engine.get_obs()
        reward = self.engine.get_reward()
        done = self.engine.get_done()
        info = [{}] * self.n_agents  # TODO: Add info to the backend, if we require it
        if self.n_agents == 1:
            return obs[0], reward[0], done[0], info[0]

        return obs, reward, done, info

    def render(self, path: str):
        return self.engine.render(path=path)
