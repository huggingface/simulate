from typing import Any, Dict, Optional

import dm_env
import gym
import numpy as np
import tree
from gym import spaces


class CameraWrapper(gym.ObservationWrapper):
    """Wrapper for extracting camera observations from agent."""

    def __init__(self, env, swap_dims=True, name="pixels", n_maps=1):
        super().__init__(env)
        self.n_maps = n_maps

        if swap_dims:
            obs_shape = env.observation_space["CameraSensor"].shape
            if n_maps == 1:
                self.observation_space = spaces.Box(
                    low=0, high=255, shape=(obs_shape[1], obs_shape[2], obs_shape[0]), dtype="uint8"
                )
            else:
                self.observation_space = spaces.Box(
                    low=0, high=255, shape=(n_maps, obs_shape[1], obs_shape[2], obs_shape[0]), dtype="uint8"
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


class GymWrapper(dm_env.Environment):
    """Environment wrapper for OpenAI Gym environments."""

    # GymWrapper is from ACME repository which can be found at:
    # https://github.com/deepmind/acme/blob/master/acme/wrappers/gym_wrapper.py
    # The license is http://www.apache.org/licenses/LICENSE-2.0

    # Note: we don't inherit from base.EnvironmentWrapper because that class
    # assumes that the wrapped environment is a dm_env.Environment.

    def __init__(self, environment: gym.Env):

        self._environment = environment
        self._reset_next_step = True
        self._last_info = None

        # Convert action and observation specs.
        obs_space = self._environment.observation_space
        act_space = self._environment.action_space
        self._observation_spec = _convert_to_spec(obs_space, name="observation")
        self._action_spec = _convert_to_spec(act_space, name="action")

    def reset(self) -> dm_env.TimeStep:
        """Resets the episode."""
        self._reset_next_step = False
        observation = self._environment.reset()
        # Reset the diagnostic information.
        self._last_info = None
        return dm_env.restart(observation)

    def step(self, action) -> dm_env.TimeStep:
        """Steps the environment."""
        if self._reset_next_step:
            return self.reset()

        observation, reward, done, info = self._environment.step(action)
        self._reset_next_step = done
        self._last_info = info

        # Convert the type of the reward based on the spec, respecting the scalar or
        # array property.
        reward = tree.map_structure(
            lambda x, t: (  # pylint: disable=g-long-lambda
                t.dtype.type(x) if np.isscalar(x) else np.asarray(x, dtype=t.dtype)
            ),
            reward,
            self.reward_spec(),
        )

        if done:
            truncated = info.get("TimeLimit.truncated", False)
            if truncated:
                return dm_env.truncation(reward, observation)
            return dm_env.termination(reward, observation)
        return dm_env.transition(reward, observation)

    def observation_spec(self):
        return self._observation_spec

    def action_spec(self):
        return self._action_spec

    def get_info(self) -> Optional[Dict[str, Any]]:
        """Returns the last info returned from env.step(action).
        Returns:
          info: dictionary of diagnostic information from the last environment step
        """
        return self._last_info

    @property
    def environment(self) -> gym.Env:
        """Returns the wrapped environment."""
        return self._environment

    def __getattr__(self, name: str):
        if name.startswith("__"):
            raise AttributeError("attempted to get missing private attribute '{}'".format(name))
        return getattr(self._environment, name)

    def close(self):
        self._environment.close()


def _convert_to_spec(space: gym.Space, name: Optional[str] = None):
    """Converts an OpenAI Gym space to a dm_env spec or nested structure of specs.
    Box, MultiBinary and MultiDiscrete Gym spaces are converted to BoundedArray
    specs. Discrete OpenAI spaces are converted to DiscreteArray specs. Tuple and
    Dict spaces are recursively converted to tuples and dictionaries of specs.
    Args:
      space: The Gym space to convert.
      name: Optional name to apply to all return spec(s).
    Returns:
      A dm_env spec or nested structure of specs, corresponding to the input
      space.
    """
    if isinstance(space, spaces.Discrete):
        return dm_env.specs.DiscreteArray(num_values=space.n, dtype=space.dtype, name=name)

    elif isinstance(space, spaces.Box):
        return dm_env.specs.BoundedArray(
            shape=space.shape, dtype=space.dtype, minimum=space.low, maximum=space.high, name=name
        )

    elif isinstance(space, spaces.MultiBinary):
        return dm_env.specs.BoundedArray(shape=space.shape, dtype=space.dtype, minimum=0.0, maximum=1.0, name=name)

    elif isinstance(space, spaces.MultiDiscrete):
        return dm_env.specs.BoundedArray(
            shape=space.shape, dtype=space.dtype, minimum=np.zeros(space.shape), maximum=space.nvec - 1, name=name
        )

    elif isinstance(space, spaces.Tuple):
        return tuple(_convert_to_spec(s, name) for s in space.spaces)

    elif isinstance(space, spaces.Dict):
        return {key: _convert_to_spec(value, key) for key, value in space.spaces.items()}

    else:
        raise ValueError("Unexpected gym space: {}".format(space))
