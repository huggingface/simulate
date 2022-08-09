"""RL env generation."""

import simenv as sm

from .gen_map import create_map


def create_env(
    executable,
    width,
    height,
    sample_from,
    tiles,
    neighbors,
    seed,
    n_maps=64,
    port=None,
    headless=None,
    **kwargs,
):
    """
    Create Xland RL env.
    """
    scene = sm.Scene(
        engine="Unity",
        engine_exe=executable,
        engine_port=port,
        engine_headless=headless,
    )
    scene += sm.LightSun()

    counter = 0
    max_iterations = 100000
    while counter < n_maps and max_iterations > 0:
        success, root = create_map(
            executable=executable,
            rank=counter,
            width=width,
            height=height,
            sample_map=sample_from,
            tiles=tiles,
            neighbors=neighbors,
            seed=seed,
            port=port,
            headless=headless,
            root=counter,
            **kwargs,
        )

        max_iterations -= 1
        if success:
            root.position += [width * counter, 0, 0]
            counter += 1
            scene += root

    if max_iterations == 0:
        raise Exception("Could not generate enough maps.")

    return sm.RLEnvironment(scene)


# TODO: bug with seed
def make_env(
    executable,
    rank,
    width=9,
    height=9,
    n_maps=8,
    n_show=4,
    sample_from=None,
    tiles=None,
    neighbors=None,
    seed=0,
    headless=None,
    **kwargs,
):
    """
    Generate XLand RL env with certain width and height.
    """

    def _make_env():
        env = create_env(
            executable=executable,
            width=width,
            height=height,
            sample_from=sample_from,
            tiles=tiles,
            neighbors=neighbors,
            seed=seed,
            port=55000 + rank,
            headless=headless,
            n_maps=n_maps,
            n_show=n_show,
            **kwargs,
        )
        return env

    return _make_env
