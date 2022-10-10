import simulate as sm
import json
import time


scene = sm.Scene(engine="Unity", engine_exe=None)

door = sm.Box(name="my_door")
door.extensions = [json.dumps({"type": "Door"})]
scene += door

scene.show()

for i in range(10):
    print(i)
    scene.step()

scene.engine.run_command("OpenDoor", door="my_door")
for i in range(100):
    print((i + 10))
    scene.step()
    time.sleep(0.1)

input("Press enter to continue...")
