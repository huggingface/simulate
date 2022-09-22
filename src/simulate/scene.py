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
""" A simulate Scene - Host a level or Scene."""
import itertools
from typing import Dict, List, Optional, Tuple, Union

from .assets import Asset, Camera, Light, Object3D, RaycastSensor, RewardFunction, StateSensor, spaces
from .assets.anytree import RenderTree
from .config import Config
from .engine import BlenderEngine, GodotEngine, PyVistaEngine, UnityEngine


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

        self._is_shown = False

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
        """Send the scene to the engine for rendering or later simulation."""

        # Sanity check that all actuators are part of one and only one actor
        node_with_actuators = self.tree_filtered_descendants(lambda node: node.actuator is not None)
        for node in node_with_actuators:
            number_of_parent_actors = 0
            for parent_node in node.tree_path:
                number_of_parent_actors += 1 if parent_node.is_actor else 0
            if number_of_parent_actors == 0:
                raise ValueError(
                    f"Node {node.name} has an actuator but is not part of an actor. "
                    "Actuators should be part of an actor. "
                    f"Check that at least one parent node of {node.name} {tuple(n.name for n in node.tree_path)} is an actor."
                )
            elif number_of_parent_actors > 1:
                raise ValueError(
                    f"Node {node.name} has an actuator but is part of more than one actor. "
                    "Actuators should be part of one and only one actor. "
                    f"Check that only one parent node of {node.name} {tuple(n.name for n in node.tree_path)} is an actor."
                )

        self.engine.show(**engine_kwargs)
        self._is_shown = True

    def step(
        self,
        action: Dict[str, Union[int, float, List[float]]] = None,
        time_step: Optional[float] = None,
        frame_skip: Optional[int] = None,
        return_nodes: Optional[bool] = None,
        return_frames: Optional[bool] = None,
        **engine_kwargs,
    ):
        """Step the Scene.

        Parameters
        ----------
        action: Dict[str, List[Any]]
            The action to apply to the actors in the scene.
            Keys are actuator_id and values are actions to apply as tensors of shapes (n_maps, n_actors, action_space...)
        time_step: Optional[float]
            The time step to apply to the scene. If None, the time_step of the config is used.
        frame_skip: Optional[int]
            The number of frames to skip. If None, the frame_skip of the config is used.
        return_nodes: Optional[bool]
            If True, the nodes of the scene are returned. If None, the return_nodes of the config is used.
        return_frames: Optional[bool]
            If True, the frames of the scene are returned. If None, the return_frames of the config is used.
        engine_kwargs: Dict
            Additional kwargs to pass to the engine.
        """
        if not self._is_shown:
            raise ValueError("The scene should be shown before stepping it (call scene.show()).")
        if time_step is not None:
            engine_kwargs.update({"time_step": time_step})
        if frame_skip is not None:
            engine_kwargs.update({"frame_skip": frame_skip})
        if return_nodes is not None:
            engine_kwargs.update({"return_nodes": return_nodes})
        if return_frames is not None:
            engine_kwargs.update({"return_frames": return_frames})
        return self.engine.step(action=action, **engine_kwargs)

    def reset(self):
        """Reset the Scene"""
        return self.engine.reset()

    def close(self):
        self.engine.close()

    @property
    def action_space(self) -> Optional[spaces.Space]:
        """The action space of the single actor in the scene.
        Only available is the scene has one and only one actor.
        Otherwise, None is returned.
        If the scene has more than one actor, you should query
            the action_space of the actor directly, e.g. scene.actors[0].action_space
        """
        actors = self.actors
        if len(actors) == 1:
            return actors[0].action_space
        return None

    @property
    def observation_space(self) -> Optional[spaces.Space]:
        """The observation space of the single actor in thescene.
        Only available is the scene has one and only one actor.
        Otherwise, None is returned.
        If the scene has more than one actor, you should query
            the observation_space of the actor directly, e.g. scene.actors[0].observation_space
        """
        actors = self.actors
        if len(actors) == 1:
            return actors[0].observation_space
        return None

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
    def actors(self) -> Tuple[Asset]:
        """Return the actors in the scene, sorted by names."""
        unsorted_actors = self.tree_filtered_descendants(lambda node: node.is_actor)
        sorted_actors = sorted(unsorted_actors, key=lambda actor: actor.name)
        return tuple(sorted_actors)
