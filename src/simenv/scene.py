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
from typing import List, Optional, Tuple, Union

from .assets import Asset, Camera, Light, Object3D, RaycastSensor, RewardFunction, StateSensor
from .assets.anytree import RenderTree
from .config import Config
from .engine import BlenderEngine, GodotEngine, PyVistaEngine, UnityEngine


try:
    from gym import spaces
except ImportError:
    pass


class Scene(Asset):
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
        config: Optional[Config] = None,
        name: Optional[str] = None,
        created_from_file: Optional[str] = None,
        position: Optional[List[float]] = None,
        rotation: Optional[List[float]] = None,
        scaling: Optional[Union[float, List[float]]] = None,
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
            created_from_file=created_from_file,
        )
        self.config = config if config is not None else Config()

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

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        spacer = "\n" if len(self) else ""
        return f"Scene(engine='{self.engine}'){spacer}{RenderTree(self).print_tree()}"

    def show(self, **engine_kwargs):
        """Render the Scene using the engine."""
        self.engine.show(**engine_kwargs)

    def step(self, **engine_kwargs):
        """Step the Scene"""
        return self.engine.step(**engine_kwargs)

    def reset(self, **engine_kwargs):
        """Reset the Scene"""
        return self.engine.reset(**engine_kwargs)

    @property
    def action_space(self):
        actors = self.actors
        if len(actors) > 0:
            return actors[0].action_space
        return None

    @property
    def observation_space(self):
        actors = self.actors
        if len(actors) > 0:
            actor = actors[0]
            sensors = actor.tree_filtered_descendants(
                lambda node: isinstance(node, (Camera, StateSensor, RaycastSensor))
            )
            if len(sensors) == 1:
                return sensors[0].observation_space
            elif sensors:
                return spaces.Dict({sensor.SENSOR_NAME: sensor.observation_space for sensor in sensors})
        return None

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

    @property
    def reward_functions(self):
        """Tuple with all Reward functions in the Scene"""
        return self.tree_filtered_descendants(lambda node: isinstance(node, RewardFunction))

    @property
    def sensors(self):
        """Tuple with all sensors in the Scene"""
        return self.tree_filtered_descendants(lambda node: isinstance(node, (Camera, StateSensor, RaycastSensor)))

    @property
    def unique_sensors(self):
        """Tuple with all sensors in the Scene"""
        return set(self.tree_filtered_descendants(lambda node: isinstance(node, (Camera, StateSensor, RaycastSensor))))

    @property
    def actors(self) -> Tuple[Asset]:
        return self.tree_filtered_descendants(lambda node: node.actuator is not None)
