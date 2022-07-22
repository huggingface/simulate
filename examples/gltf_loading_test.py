import os

from simenv import Scene


scene = Scene.create_from("simenv-tests/Box/glTF/Box.gltf", auto_update=False)

print("===== BEFORE ====")
print(scene)
print(scene._created_from_file)
scene.show()

# Save in the gitgnored output
from pathlib import Path


save_path = Path(__file__).parent.parent.absolute() / "output" / "scene" / "scene.gltf"

save_path_returned = scene.save(save_path)

scene.load(save_path_returned[0])

print("===== AFTER SAVING LOCALLY ====")
print(scene)
print(scene._created_from_file)
scene.show()

# Push to hub
path_on_hub = "simenv-tests/Debug-2/glTF/Box.gltf"
hub_token = os.environ.get(
    "HUB_TOKEN"
)  # Set your Hub token for simenv-tests in this env variable (see https://huggingface.co/settings/tokens)
print(f"Hub token: {hub_token}")
url_path_returned = scene.push_to_hub(path_on_hub, token=hub_token)

print("===== URLs ====")
print(url_path_returned)

scene.load(path_on_hub)

print("===== AFTER LOADING FROM HUB====")
print(scene)
print(scene._created_from_file)
scene.show()
