import argparse
import base64

import simenv as sm


def create_scene(build_exe=None):
    scene = sm.Scene(engine="Unity")
    scene.load("simenv-tests/Box/glTF-Embedded/Box.gltf")

    scene.show()

    return scene


def echo_gltf(scene):
    bytes = scene.as_glb_bytes()
    b64_bytes = base64.b64encode(bytes).decode("ascii")
    result = scene.engine.run_command("TestEchoGLTF", b64bytes=b64_bytes)
    print(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--build_exe", help="path to unity engine build executable", required=False, type=str, default=None
    )
    parser.add_argument("-n", "--n_frames", help="number of frames to simulate", required=False, type=int, default=30)
    args = parser.parse_args()

    scene = create_scene(args.build_exe)
    echo_gltf(scene)

    input("Press any key to continue...")
