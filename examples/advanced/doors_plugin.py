import argparse
import json

import matplotlib.pyplot as plt
import numpy as np

import simulate as sm


def add_door_extensions(scene):
    # Here we add our custom Door extension to the doors
    # Extensions are json encodings of arbitrary IGLTFExtension implementations in the backend
    # In this example, these properties reflect the `Door` class in the backend Doors plugin
    scene.LeftDoor.extensions = [json.dumps({"type": "Door", "open_angle": -70, "animation_time": 1})]
    scene.RightDoor.extensions = [json.dumps({"type": "Door", "open_angle": 70, "animation_time": 0.5})]


def simulate(scene):
    scene.show()
    plt.ion()
    _, ax = plt.subplots(1, 1)

    # We define a function to advance the scene forward and display in matplotlib
    def advance(count):
        for _ in range(count):
            event = scene.step()
            im = np.array(event["frames"]["Camera"], dtype=np.uint8).transpose(1, 2, 0)
            ax.clear()
            ax.imshow(im)
            plt.pause(0.1)

    # Use commands to open/close doors
    scene.engine.run_command("OpenDoor", door="LeftDoor")
    advance(10)

    scene.engine.run_command("OpenDoor", door="RightDoor")
    advance(50)

    scene.engine.run_command("CloseDoor", door="LeftDoor")
    scene.engine.run_command("CloseDoor", door="RightDoor")
    advance(60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--build_exe", help="path to unity engine build executable", required=False, type=str, default=""
    )
    args = parser.parse_args()

    build_exe = args.build_exe if args.build_exe != "None" else None
    scene = sm.Scene.create_from("simulate-tests/Doors/Doors.gltf", engine="Unity", engine_exe=build_exe)
    add_door_extensions(scene)
    simulate(scene)

    input("Press enter to continue...")
