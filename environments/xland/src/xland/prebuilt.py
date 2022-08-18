"""Defines pre-built environments for benchmarking."""

import os

import numpy as np
from xland.utils import generate_tiles

from .rl_scene import make_pool


def gen_collect_all_args(xland_folder=""):
    """
    XLand Toy environment.

    Two different levels with multiple objects (4) and one agent. The goal of the agent is to collect the maximum
    number of objects before timeout.

    Returns:
        task_args: args specific to the collect_all task
    """
    tiles, symmetries, weights, neighbors = generate_tiles(2)

    return {
        "tiles": tiles,
        "symmetries": symmetries,
        "weights": weights,
        "neighbors": neighbors,
        "n_agents": 1,
        "n_objects": 4,
        "width": 6,
        "height": 6,
        "predicate": "collect_all",
    }


def gen_toy_args(xland_folder=""):
    """
    XLand Toy environment.

    One single level with one single object and one agent. The goal of the agent is to
    find the object and get close to it.

    Returns:
        task_args: args specific to the toy task
    """
    plain_map = np.zeros((2, 2, 2, 2))

    return {
        "sample_from": plain_map,
        "n_agents": 1,
        "n_objects": 1,
        "width": 4,
        "height": 4,
        "predicate": "near",
    }


def gen_easy_args(xland_folder=""):
    """
    XLand easy environment.

    Two different levels with two objects and one agent. The goal of the agent can be vary.

    Returns:
        task_args: args specific to the easy task
    """
    map_01 = np.load(os.path.join(xland_folder, "benchmark/examples/map_01.npy"))

    return {
        "sample_from": map_01,
        "n_agents": 1,
        "n_objects": 2,
        "width": 5,
        "height": 5,
        "predicate": "random",
        "n_options": 1,
        "n_conjunctions": 2,
    }


def gen_medium_args(xland_folder=""):
    """
    XLand medium environment.

    One single level with one single object and one agent. The goal of the agent is to
    find the object and get close to it.

    Returns:
        task_args: args specific to the medium task
    """

    map_02 = np.load(os.path.join(xland_folder, "benchmark/examples/map_02.npy"))

    return {
        "sample_from": map_02,
        "n_agents": 1,
        "n_objects": 2,
        "width": 7,
        "height": 7,
        "predicate": "random",
        "n_options": 2,
        "n_conjunctions": 2,
    }


def gen_hard_args(xland_folder=""):
    """
    XLand hard environment.

    One single level with one single object and one agent. The goal of the agent is to
    find the object and get close to it.

    Returns:
        task_args: args specific to the hard task
    """
    map_03 = np.load(os.path.join(xland_folder, "benchmark/examples/map_03.npy"))

    return {
        "sample_from": map_03,
        "n_agents": 1,
        "n_objects": 6,
        "width": 9,
        "height": 9,
        "predicate": "random",
        "n_options": 3,
        "n_conjunctions": 2,
    }


DEFAULT_ARGS = {
    "engine": "Unity",
    "frame_skip": 4,
    "frame_rate": 20,
}

TASK_ARGS = {
    "toy": gen_toy_args,
    "collect_all": gen_collect_all_args,
    "easy": gen_easy_args,
    "medium": gen_medium_args,
    "hard": gen_hard_args,
}

AVAILABLE_TASKS = TASK_ARGS.keys()


def make_prebuilt_env(
    task,
    executable,
    n_maps,
    n_show,
    headless,
    n_parallel=1,
    starting_port=55000,
    seed=None,
    specific_color=None,
    object_type=None,
    xland_folder="",
    **common_args,
):
    """
    Create prebuilt environments. Arguments are explaind below, and
    common_args might be other args than the ones explicitly shown such as
    frame_skip, physics_update_rate, camera width and height, etc. See make_env
    function for more details.

    Args:
        task: which task to be executed
        executable: unity executable
        n_maps: number of maps to generate.
        n_show: number of maps to show at once.
        headless: if the environment should be run in headless mode.
        n_parallel: number of parallel environments
        starting_port: starting port to create environments
        seed: seed to generate maps.
        mono_color: to use a single color for the objects.
        mono_object: to use a single format for all objects.
        common_args: extra args to be passed to make_env like camera width and height
        xland_folder: folder where xland is placed, so that we can read the maps there
    """
    default_args = DEFAULT_ARGS
    if task not in AVAILABLE_TASKS:
        raise ValueError("Task {task} not defined.")

    task_args = TASK_ARGS[task](xland_folder)
    env_args = {**default_args, **common_args, **task_args}
    pool_fns = []

    for i in range(n_parallel):
        pool_fn = make_pool(
            executable=executable,
            port=starting_port + i,
            headless=headless,
            seed=seed,  # TODO: seed needs to be changed every map
            n_maps=n_maps,
            n_show=n_show,
            object_type=object_type,
            specific_color=specific_color,
            **env_args,
        )
        pool_fns.append(pool_fn)

    return pool_fns
