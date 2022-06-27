"""Functions for setting the agent in the world."""

import numpy as np

import simenv as sm


def create_agents(agent_pos, objects, predicate=None, camera_width=72, camera_height=96, verbose=True):
    """
    Create agents in simenv.

    Args:
        agent_pos: list of positions of the agents
        objects: list of objects in the world
        predicate: goal of the agent
            If None, then we use a default task
        camera_width: width of the agent camera
        camera_height: height of the agent camera
        verbose: verbose for debugging
    """

    agents = []

    for i, pos in enumerate(agent_pos):
        agent = sm.RL_Agent(
            name=f"agent_{i}",
            camera_width=camera_width,
            camera_height=camera_height,
            position=pos,
            height=1.0,
        )
        agents.append(agent)

    if predicate is None:
        # For now the default task will be to collect an object
        # Sample n_agents objects with replacement, so that we associate each
        # agent with an object
        object_idxs = np.random.choice(np.arange(len(objects)), size=len(agent_pos), replace=True)
        timeout_reward_function = sm.RLAgentRewardFunction(
            function="timeout",
            entity1=agent,
            entity2=agent,
            distance_metric="euclidean",
            threshold=200,
            is_terminal=True,
            scalar=-1.0,
        )

        # Create Reward function
        for obj_idx, agent in zip(object_idxs, agents):
            reward_function = sm.RLAgentRewardFunction(
                function="sparse",
                entity1=agent,
                entity2=objects[obj_idx],
                distance_metric="euclidean",
                threshold=0.2,
                is_terminal=True,
            )

            agent.add_reward_function(reward_function)
            agent.add_reward_function(timeout_reward_function)

            if verbose:
                print("Agent {} will collect object {}".format(agent.name, objects[obj_idx].name))

    return agents
