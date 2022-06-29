"""RL env generation."""

from .xland_env import XLandEnv


def create_env(executable, width, height, sample_from, tiles, neighbors, seed, port=None, headless=None, **kwargs):
    """
    Create Xland RL env.
    """
    env = XLandEnv(
        executable=executable,
        width=width,
        height=height,
        sample_map=sample_from,
        tiles=tiles,
        neighbors=neighbors,
        seed=seed,
        port=port,
        headless=headless,
        **kwargs,
    )
    return env


def make_env(
    executable, width=9, height=9, sample_from=None, tiles=None, neighbors=None, seed=0, headless=None, **kwargs
):
    """
    Generate XLand RL env with certain width and height.
    """

    def _make_env(port):
        env = create_env(
            executable=executable,
            width=width,
            height=height,
            sample_from=sample_from,
            tiles=tiles,
            neighbors=neighbors,
            seed=seed,
            port=port,
            headless=headless,
            **kwargs,
        )
        return env

    return _make_env
