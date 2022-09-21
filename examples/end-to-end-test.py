import argparse

import simenv as sm


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build_exe", default=None, type=str, required=False, help="Pre-built unity app for simenv")
    args = parser.parse_args()

    CAMERA_HEIGHT = 40
    CAMERA_WIDTH = 64

    print("before creating scene")
    scene = sm.Scene(engine="unity", engine_exe=args.build_exe, engine_headless=True)
    print("after creating scene")

    scene += sm.LightSun(name="sun", position=[0, 20, 0], intensity=0.9)
    scene += sm.Box(name="floor", position=[0, -0.05, 0], scaling=[100, 0.1, 100])
    scene += sm.Box(name="wall1", position=[-1, 0.5, 0], scaling=[0.1, 1, 5.1])
    scene += sm.Box(name="wall2", position=[1, 0.5, 0], scaling=[0.1, 1, 5.1])
    scene += sm.Box(name="wall3", position=[0, 0.5, 4.5], scaling=[5.9, 1, 0.1])
    scene += sm.Box(name="wall4", position=[-2, 0.5, 2.5], scaling=[1.9, 1, 0.1])
    scene += sm.Box(name="wall5", position=[2, 0.5, 2.5], scaling=[1.9, 1, 0.1])
    scene += sm.Box(name="wall6", position=[-3, 0.5, 3.5], scaling=[0.1, 1, 2.1])
    scene += sm.Box(name="wall7", position=[3, 0.5, 3.5], scaling=[0.1, 1, 2.1])
    scene += sm.Box(name="wall8", position=[0, 0.5, -2.5], scaling=[1.9, 1, 0.1])

    actor = sm.EgocentricCameraActor(
        name="actor",
        camera_width=CAMERA_WIDTH,
        camera_height=CAMERA_HEIGHT,
        position=[0.0, 0.0, 0.0],
    )

    scene += actor

    print(scene.actors)

    env = sm.RLEnv(scene)

    print(env.actors)

    obs, reward, done, info = env.step([0])

    scene.close()
