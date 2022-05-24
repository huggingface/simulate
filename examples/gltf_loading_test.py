from simenv import Scene

scene = Scene.load('simenv-tests/Box/glTF/Box.gltf')

print("===== BEFORE ====")
print(scene)
print(scene._created_from_file)
scene.show(in_background=False)

# Save in the gitgnored output
from pathlib import Path
save_path = Path(__file__).parent.parent.absolute() / 'output' / 'scene' / 'scene.gltf'

save_path_returned = scene.save(save_path)

scene = Scene.load(save_path_returned[0])

print("===== AFTER ====")
print(scene)
print(scene._created_from_file)
scene.show(in_background=False)
