import argparse

import simenv as sm


def create_scene(build_exe=None):
    scene = sm.Scene(engine="Unity")
    scene.load("simenv-tests/Box/glTF-Embedded/Box.gltf")

    scene.show()

    return scene


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--build_exe", help="path to unity engine build executable", required=False, type=str, default=None
    )
    parser.add_argument("-n", "--n_frames", help="number of frames to simulate", required=False, type=int, default=30)
    args = parser.parse_args()

    scene = create_scene(args.build_exe)

    input("Press any key to continue...")
