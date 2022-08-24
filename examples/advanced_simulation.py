import argparse

import matplotlib.pyplot as plt
import numpy as np

import simenv as sm


def create_scene(build_exe=None):
    scene = sm.Scene(engine="Unity", engine_exe=build_exe)
    scene.load("C:\\Users\\dylan\\Documents\\huggingface\\simenv\\integrations\\Unity\\simenv-unity\\Assets\\GLTF\\mountaincar\\Exported\\scene.gltf")

    """ scene += sm.Box(name="floor", position=[0, 0, 0], bounds=[-10, 10, -0.1, 0, -10, 10], material=sm.Material.GRAY75)

    cube = sm.Box(name="cube", position=[0, 3, 0], scaling=[1, 1, 1], material=sm.Material.GRAY50)
    cube.physics_component = sm.RigidBodyComponent()
    scene += cube

    scene += sm.Camera(name="camera", position=[0, 2, -10]) """
    scene.show()

    return scene


def simulate(scene, n_frames=30):
    plt.ion()
    _, ax = plt.subplots()
    for _ in range(n_frames):
        event = scene.step()
        im = np.array(event["frames"]["camera"], dtype=np.uint8).transpose(1, 2, 0)
        ax.clear()
        ax.imshow(im)
        plt.pause(0.1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--build_exe", help="path to unity engine build executable", required=False, type=str, default=None
    )
    parser.add_argument("-n", "--n_frames", help="number of frames to simulate", required=False, type=int, default=30)
    args = parser.parse_args()

    scene = create_scene(args.build_exe)
    simulate(scene, args.n_frames)

    input("Press enter to continue...")
