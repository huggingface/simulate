import argparse

import simenv as sm
from simenv.assets.action_mapping import ActionMapping


def create_scene(build_exe=None, gltf_path=None):
    try:
        scene = sm.Scene.create_from("simenv-tests/MountainCar/MountainCar.gltf")
    except Exception as e:
        print(e)
        print("Failed to load from hub, loading from path: " + gltf_path)
        scene = sm.Scene.create_from(gltf_path, engine="Unity", engine_exe=build_exe)

    return scene


def add_rl_components_to_scene(scene):
    actor = scene.Cart

    # Add action mappings, moving left and right
    mapping = [
        ActionMapping("add_force", axis=[1, 0, 0], amplitude=300),
        ActionMapping("add_force", axis=[-1, 0, 0], amplitude=300),
    ]
    actor.controller = sm.Controller(mapping=mapping, n=2)

    # Add rewards, reaching the top of the right hill
    reward_entity = sm.Asset(name="reward_entity", position=[-40, 21, 0])
    scene += reward_entity
    reward = sm.RewardFunction(entity_a=reward_entity, entity_b=actor)
    actor += reward

    # Add state sensor, for position of agent
    actor += sm.StateSensor(target_entity=actor, properties=["position"])


if __name__ == "__main__":
    DYLAN_GLTF_PATH = "C:\\Users\\dylan\\Documents\\huggingface\\simenv\\integrations\\Unity\\simenv-unity\\Assets\\GLTF\\mountaincar\\Exported\\MountainCar.gltf"

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--build_exe", help="path to unity engine build executable", required=False, type=str, default=None
    )
    parser.add_argument("--gltf_path", help="path to the gltf file", required=False, type=str, default=DYLAN_GLTF_PATH)

    parser.add_argument("-n", "--n_frames", help="number of frames to simulate", required=False, type=int, default=30)
    args = parser.parse_args()

    scene = create_scene(args.build_exe, args.gltf_path)
    add_rl_components_to_scene(scene)

    env = sm.RLEnv(scene)

    for i in range(10000):
        obs, reward, done, info = env.step()
        print(obs)

    input("Press enter to continue...")
