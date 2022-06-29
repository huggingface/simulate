"""
XLand environment wrapper to RLEnv so that we can make a custom reset.
"""

from simenv import RLEnv

from .gen_scene import create_scene


class XLandEnv(RLEnv):
    def __init__(self, port=None, engine="Unity", **kwargs):
        self.kwargs = kwargs
        self.port = port

        scene = self.get_scene(engine=engine, port=port)
        super().__init__(scene)

    def reset(self):
        # This function is not called when using ParallelSimEnv
        # TODO: implement replacing of objects / agents
        new_scene = self.get_scene()

        self.scene.map_root.remove(self.scene.map_root.tree_children)
        self.scene.map_root += new_scene.map_root
        self.scene.show()

        return super().reset()

    def get_scene(self, engine=None, **port_args):
        success, scene = create_scene(engine=engine, **port_args, **self.kwargs)

        if not success:
            raise Exception("Could not generate env.")

        return scene
