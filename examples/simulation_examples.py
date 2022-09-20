import argparse

import simenv as sm


def create_scene(build_exe=None):
    scene = sm.Scene(engine="Unity", engine_exe=build_exe)
    scene += sm.LightSun()

    # Add a floor
    scene += sm.Box(
        name="floor",
        position=[0, 0, 0],
        bounds=[-10, 10, -0.1, 0, -10, 10],
        material=sm.Material.GRAY75,
        with_collider=True,
    )

    # Add a cube that will fall
    cube = sm.Box(name="cube", position=[0, 3, 0], scaling=[1, 1, 1], material=sm.Material.GRAY50, with_collider=True)
    scene += cube

    # Add a RigidBodyComponent to the cube
    # This will enable physics simulation, and cause the cube to fall
    cube.physics_component = sm.RigidBodyComponent()

    # Add a camera to record the scene
    scene += sm.Camera(name="camera", position=[0, 2, -10])

    # Calling show() is required for the scene to be initialized
    # show() allows several engine keyword arguments, which are passed to the Unity backend
    # You can find all available keyword arguments TODO: here
    scene.show()

    return scene


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--build_exe", help="path to unity engine build executable", required=False, type=str, default=None
    )
    parser.add_argument("-n", "--n_frames", help="number of frames to simulate", required=False, type=int, default=30)
    args = parser.parse_args()

    scene = create_scene(args.build_exe)

    input("Press any key to continue...")
