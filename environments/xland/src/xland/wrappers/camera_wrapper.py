import gym
from gym import spaces


class CameraWrapper(gym.ObservationWrapper):
    """Wrapper for extracting camera observations from agent."""

    def __init__(self, env, swap_dims=True, name="pixels", n_maps=1):
        super().__init__(env)
        self.n_maps = n_maps

        if swap_dims:
            obs_shape = env.observation_space["CameraSensor"].shape
            self.observation_space = spaces.Box(
                low=0, high=255, shape=(obs_shape[1], obs_shape[2], obs_shape[0]), dtype="uint8"
            )

        else:
            self.observation_space = env.observation_space["CameraSensor"]

        if name is not None:
            self.observation_space = spaces.Dict({name: self.observation_space})

        self.action_space = spaces.Discrete(self.action_space.n)

    def observation(self, obs):
        if self.n_maps > 1:
            return {"pixels": obs["CameraSensor"].transpose((0, 2, 3, 1))}
        return {"pixels": obs["CameraSensor"].transpose((1, 2, 0))}
