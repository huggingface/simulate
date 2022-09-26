import argparse

import simulate as sm
from simulate.assets.action_mapping import ActionMapping


def add_rl_components_to_scene(scene):
    actor = scene.MountainCar_Cart
    actor.is_actor = True

    # Add action mappings, moving left and right
    mapping = [
        ActionMapping("add_force", axis=[1, 0, 0], amplitude=300),
        ActionMapping("add_force", axis=[-1, 0, 0], amplitude=300),
    ]
    actor.actuator = sm.Actuator(mapping=mapping, n=2)

    # Add rewards, reaching the top of the right hill
    reward_entity = sm.Asset(name="reward_entity", position=[-40, 21, 0])
    scene += reward_entity
    reward = sm.RewardFunction(entity_a=reward_entity, entity_b=actor)
    actor += reward

    # Add state sensor, for position of agent
    actor += sm.StateSensor(target_entity=actor, properties=["position"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build_exe", help="path to unity engine build executable", required=False, type=str, default="")
    parser.add_argument("-n", "--n_frames", help="number of frames to simulate", required=False, type=int, default=30)
    args = parser.parse_args()

    build_exe = args.build_exe if args.build_exe != "None" else None
    scene = sm.Scene.create_from("simulate-tests/MountainCar/MountainCar.gltf", engine="Unity", engine_exe=build_exe)
    add_rl_components_to_scene(scene)

    env = sm.RLEnv(scene)

    for i in range(10000):
        action = [env.action_space.sample()]
        obs, reward, done, info = env.step(action=action)

    input("Press enter to continue...")
