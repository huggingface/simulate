"""RL env generation."""

import simenv as sm

from .gen_map import create_map


def create_env_pool(
    executable,
    width,
    height,
    sample_from,
    tiles,
    neighbors,
    seed,
    n_maps=64,
    n_show=9,
    port=None,
    headless=None,
    frame_rate=None,
    frame_skip=None,
    **kwargs,
):
    """
    Create Xland RL env.
    """
    counter = 0
    max_iterations = 100000

    def _map_fn(rank):
        root = None
        nonlocal max_iterations
        while root is None and max_iterations > 0:
            root = create_map(
                rank=rank,
                width=width,
                height=height,
                sample_map=sample_from,
                tiles=tiles,
                neighbors=neighbors,
                seed=seed,
                headless=headless,
                root=counter,
                frame_skip=frame_skip,
                **kwargs,
            )
            max_iterations -= 1
            if root is not None:
                return root
        return None

    map_pool = sm.RLEnv(
        _map_fn,
        n_maps=n_maps,
        n_show=n_show,
        engine_exe=executable,
        engine_port=port,
        engine_headless=headless,
        frame_rate=frame_rate,
        frame_skip=frame_skip,
    )

    if max_iterations == 0:
        raise Exception("Could not generate enough maps.")

    return map_pool


# TODO: bug with seed
def make_env_fn(
    executable,
    width=9,
    height=9,
    n_maps=8,
    n_show=4,
    sample_from=None,
    tiles=None,
    neighbors=None,
    seed=0,
    headless=False,
    frame_rate=30,
    frame_skip=4,
    **kwargs,
):
    """
    Generate XLand RL env with certain width and height.
    """

    def _env_fn(port):
        env = create_env_pool(
            executable=executable,
            width=width,
            height=height,
            sample_from=sample_from,
            tiles=tiles,
            neighbors=neighbors,
            seed=seed,
            port=port,
            headless=headless,
            n_maps=n_maps,
            n_show=n_show,
            frame_rate=frame_rate,
            frame_skip=frame_skip,
            **kwargs,
        )
        return env

    return _env_fn
