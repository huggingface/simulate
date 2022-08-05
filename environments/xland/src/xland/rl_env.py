"""RL env generation."""

from simenv import Scene

from .gen_scene import create_scene


def create_env(
    executable,
    width,
    height,
    sample_from,
    tiles,
    neighbors,
    seed,
    n_maps=64,
    n_show=16,
    port=None,
    headless=None,
    **kwargs,
):
    """
    Create Xland RL env.
    """
    frame_skip = kwargs.get("frame_skip", 4)
    physics_update_rate = kwargs.get("physics_update_rate", 30)

    scene = Scene(
        engine="Unity",
        engine_exe=executable,
        engine_port=port,
        engine_headless=headless,
        frame_skip=frame_skip,
        physics_update_rate=physics_update_rate,
    )

    counter = 0
    max_iterations = 100000
    while counter < n_maps and max_iterations > 0:
        root = create_scene(
            executable=executable,
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
        if scene is not None:
            counter += 1
            scene.engine.add_to_pool(root)

    if max_iterations == 0:
        raise Exception("Could not generate enough maps.")

    scene.show(n_maps=n_show)
    return scene


# TODO: bug with seed
def make_env(
    executable,
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
            n_maps=n_maps,
            n_show=n_show,
            **kwargs,
        )

        wrappers = kwargs.get("wrappers", None)

        if wrappers is not None:
            for wrapper in wrappers:
                env = wrapper(env)

        return env

    return _make_env
