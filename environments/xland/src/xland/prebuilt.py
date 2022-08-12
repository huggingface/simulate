"""Defines pre-built environments for benchmarking."""

import numpy as np
from xland.utils import generate_tiles

from .rl_env import make_env


def make_collect_all_environment(executable, n_maps, n_show, seed=None, object_type=None, specific_color=None):
    """
    XLand Toy environment.

    Two different levels with multiple objects (4) and one agent. The goal of the agent is to collect the maximum
    number of objects before timeout.

    Args:
        multi_color: to use different colors for the objects.
        multi_object: to use different formats of objects.

    Returns:
        env_fn: environment function
    """
    tiles, symmetries, weights, neighbors = generate_tiles(2)

    return make_env(
        executable=executable,
        engine="Unity",
        tiles=tiles,
        symmetries=symmetries,
        weights=weights,
        neighbors=neighbors,
        seed=seed,
        n_agents=1,
        n_objects=4,
        width=6,
        height=6,
        frame_skip=4,
        physics_update_rate=20,
        n_maps=n_maps,
        n_show=n_show,
        predicate="collect_all",
        object_type=object_type,
        specific_color=specific_color,
    )


def make_toy_environment(executable, n_maps, n_show, seed=None, object_type=None, specific_color=None):
    """
    XLand Toy environment.

    One single level with one single object and one agent. The goal of the agent is to
    find the object and get close to it.

    Args:
        executable: unity executable
        n_maps: number of maps to generate.
        n_show: number of maps to show at once.
        seed: seed to generate maps.
        mono_color: to use a single color for the objects.
        mono_object: to use a single format for all objects.

    Returns:
        env_fn: environment function
    """
    plain_map = np.zeros((2, 2, 2, 2))

    return make_env(
        executable=executable,
        sample_from=plain_map,
        engine="Unity",
        seed=seed,
        n_agents=1,
        n_objects=1,
        width=4,
        height=4,
        frame_skip=4,
        physics_update_rate=20,
        n_maps=n_maps,
        n_show=n_show,
        predicate="near",
        object_type=object_type,
        specific_color=specific_color,
    )


def make_easy_environment(executable, n_maps, n_show, seed=None, object_type=None, specific_color=None):
    """
    XLand easy environment.

    Two different levels with two objects and one agent. The goal of the agent can be vary.

    Args:
        executable: unity executable
        n_maps: number of maps to generate.
        n_show: number of maps to show at once.
        seed: seed to generate maps.
        mono_color: to use a single color for the objects.
        mono_object: to use a single format for all objects.

    Returns:
        env_fn: environment function
    """
    map_01 = np.load("map_01.npy")

    return make_env(
        executable=executable,
        sample_from=map_01,
        engine="Unity",
        seed=seed,
        n_agents=1,
        n_objects=2,
        width=6,
        height=6,
        frame_skip=4,
        physics_update_rate=20,
        n_maps=n_maps,
        n_show=n_show,
        predicate="random",
        n_options=1,
        n_conjunctions=2,
        object_type=object_type,
        specific_color=specific_color,
    )


def make_medium_environment(executable, n_maps, n_show, seed=None, object_type=None, specific_color=None):
    """
    XLand medium environment.

    One single level with one single object and one agent. The goal of the agent is to
    find the object and get close to it.

    Args:
        executable: unity executable
        n_maps: number of maps to generate.
        n_show: number of maps to show at once.
        seed: seed to generate maps.
        mono_color: to use a single color for the objects.
        mono_object: to use a single format for all objects.

    Returns:
        env_fn: environment function
    """
    map_02 = np.load("map_02.npy")

    return make_env(
        executable=executable,
        sample_from=map_02,
        engine="Unity",
        seed=seed,
        n_agents=1,
        n_objects=2,
        width=9,
        height=9,
        frame_skip=4,
        physics_update_rate=20,
        n_maps=n_maps,
        n_show=n_show,
        predicate="random",
        n_options=2,
        n_conjunctions=2,
        object_type=object_type,
        specific_color=specific_color,
    )


def make_hard_environment(executable, n_maps, n_show, seed=None, object_type=None, specific_color=None):
    """
    XLand hard environment.

    One single level with one single object and one agent. The goal of the agent is to
    find the object and get close to it.

    Args:
        executable: unity executable
        n_maps: number of maps to generate.
        n_show: number of maps to show at once.
        seed: seed to generate maps.
        mono_color: to use a single color for the objects.
        mono_object: to use a single format for all objects.

    Returns:
        env_fn: environment function
    """
    map_03 = np.load("map_03.npy")

    return make_env(
        executable=executable,
        sample_from=map_03,
        engine="Unity",
        seed=seed,
        n_agents=1,
        n_objects=2,
        width=6,
        height=6,
        frame_skip=4,
        physics_update_rate=20,
        n_maps=n_maps,
        n_show=n_show,
        predicate="random",
        n_options=3,
        n_conjunctions=2,
        object_type=object_type,
        specific_color=specific_color,
    )
