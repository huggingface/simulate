import json

import matplotlib.pyplot as plt
import numpy as np

import simulate as sm


# Loading our scene with doors from the hub
scene = sm.Scene.create_from("simulate-tests/Doors/Room.gltf", engine="Unity", engine_exe=None)
print(scene)

# Add our custom door extension to each door
scene.LeftDoor.extensions = [json.dumps({"type": "Door", "open_angle": -70, "animation_time": 1})]
scene.RightDoor.extensions = [json.dumps({"type": "Door", "open_angle": 70, "animation_time": 0.5})]

# Show the scene and initialize plot for us to visualize in matplotlib
scene.show()
plt.ion()
_, ax = plt.subplots(1, 1)


# Function to advance the scene forward and display in matplotlib
def advance(count):
    for _ in range(count):
        event = scene.step()
        im = np.array(event["frames"]["Camera"], dtype=np.uint8).transpose(1, 2, 0)
        ax.clear()
        ax.imshow(im)
        plt.pause(0.1)


# Using commands to open/close doors
scene.engine.run_command("OpenDoor", door="LeftDoor")
advance(10)

scene.engine.run_command("OpenDoor", door="RightDoor")
advance(50)

scene.engine.run_command("CloseDoor", door="LeftDoor")
scene.engine.run_command("CloseDoor", door="RightDoor")
advance(60)

input("Press enter to continue...")
