# Copyright 2022 The HuggingFace Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from simulate import Scene


# this example showcases the local and remote save and load capabilities of Simulate

if __name__ == "__main__":
    # create an initial scene locally
    scene = Scene.create_from("simulate-tests/Box/glTF/Box.gltf", auto_update=False)

    print("===== BEFORE ====")
    print(scene)
    print(scene._created_from_file)
    scene.show()

    # Save in the gitgnored output
    from pathlib import Path

    save_path = Path(__file__).parent.parent.absolute() / "output" / "scene" / "scene.gltf"
    save_path_returned = scene.save(save_path)

    # load saved file
    scene.load(save_path_returned[0])

    print("===== AFTER SAVING LOCALLY ====")
    print(scene)
    print(scene._created_from_file)
    # the two printed scenes should be the same!

    scene.show()

    # Push to scene to the hub
    path_on_hub = "simulate-tests/Debug-2/glTF/Box.gltf"
    hub_token = os.environ.get(
        "HUB_TOKEN"
    )  # Set your Hub token for simulate-tests in this env variable (see https://huggingface.co/settings/tokens)
    print(f"Hub token: {hub_token}")
    url_path_returned = scene.push_to_hub(path_on_hub, token=hub_token)

    print("===== URLs ====")
    print(url_path_returned)

    # re-load the scene from the hub!
    scene.load(path_on_hub)

    print("===== AFTER LOADING FROM HUB====")
    print(scene)
    print(scene._created_from_file)
    # the three printed scenes should be the same!

    scene.show()
