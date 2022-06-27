"""
XLand environment wrapper to RLEnv so that we can make a custom reset.
"""

from .gen_env import generate_env
from simenv import RLEnv

class XLandEnv(RLEnv):
    def __init__(self, port=None, **kwargs):
        self.kwargs = kwargs

        success, scene = generate_env(engine="Unity", port=port, **kwargs)
        scene.show()
        
        if not success:
            raise Exception("Could not generate env.")
        
        super().__init__(scene)
    
    def reset(self):
        # TODO: Not working due to Unity backend
        success, new_scene = generate_env(engine=None, **self.kwargs)

        if not success:
            raise Exception("Could not generate env.")

        self.scene.map_root.remove(self.scene.map_root.tree_children)
        self.scene.map_root += new_scene.map_root
        # self.scene.reset()
        obs = super().reset()

        # print(self.scene)
        # obs = self.scene.get_observation()
        # obs = self._reshape_obs(obs)

        return obs