"""Functions for setting the agent in the world."""

import numpy as np

import simenv as sm


def add_random_collectables_rewards(agents, objects, verbose):
    """
    First default task when no predicate is given.

    Each agent has to collect a specific object. First agent to collect it
    wins.
    """
    # For now the default task will be to collect an object
    # Sample n_agents objects with replacement, so that we associate each
    # agent with an object
    object_idxs = np.random.choice(np.arange(len(objects)), size=len(agents), replace=True)

    # Create Reward function
    for obj_idx, agent in zip(object_idxs, agents):
        reward_function = sm.RewardFunction(
            type="sparse",
            entity_a=agent,
            entity_b=objects[obj_idx],
            distance_metric="euclidean",
            threshold=1.0,
            is_terminal=True,
            is_collectable=True,
        )

        agent.add_reward_function(reward_function)

        if verbose:
            print("Agent {} will collect object {}".format(agent.name, objects[obj_idx].name))


def add_collect_all_rewards(agents, objects, verbose):
    """
    Second default task when no predicate is given.

    All agents have to collect all objects.
    """
    for agent in agents:
        for obj in objects:
            reward_function = sm.RewardFunction(
                type="sparse",
                entity_a=agent,
                entity_b=obj,
                distance_metric="euclidean",
                threshold=1.0,
                is_terminal=False,
                is_collectable=True,
            )

            agent.add_reward_function(reward_function)


def add_timeout_rewards(agents):
    for agent in agents:
        timeout_reward_function = sm.RewardFunction(
            type="timeout",
            entity_a=agent,
            entity_b=agent,
            distance_metric="euclidean",
            threshold=1500,
            is_terminal=True,
            scalar=-1.0,
        )

        agent.add_reward_function(timeout_reward_function)


def add_random_collectables_rewards(agents, objects, verbose):
    """
    First default task when no predicate is given.

    Each agent has to collect a specific object. First agent to collect it
    wins.
    """
    # For now the default task will be to collect an object
    # Sample n_agents objects with replacement, so that we associate each
    # agent with an object
    object_idxs = np.random.choice(np.arange(len(objects)), size=len(agents), replace=True)

    # Create Reward function
    for obj_idx, agent in zip(object_idxs, agents):
        reward_function = sm.RewardFunction(
            type="sparse",
            entity_a=agent,
            entity_b=objects[obj_idx],
            distance_metric="euclidean",
            threshold=1.0,
            is_terminal=True,
            is_collectable=True,
        )

        agent.add_reward_function(reward_function)

        if verbose:
            print("Agent {} will collect object {}".format(agent.name, objects[obj_idx].name))


def add_collect_all_rewards(agents, objects, verbose):
    """
    Second default task when no predicate is given.

    All agents have to collect all objects.
    """
    for agent in agents:
        for obj in objects:
            reward_function = sm.RewardFunction(
                type="sparse",
                entity_a=agent,
                entity_b=obj,
                distance_metric="euclidean",
                threshold=1.0,
                is_terminal=False,
                is_collectable=True,
            )

            agent.add_reward_function(reward_function)


def add_timeout_rewards(agents):
    for agent in agents:
        timeout_reward_function = sm.RewardFunction(
            type="timeout",
            entity_a=agent,
            entity_b=agent,
            distance_metric="euclidean",
            threshold=1500,
            is_terminal=True,
            scalar=-1.0,
        )

        agent.add_reward_function(timeout_reward_function)


def create_agents(agent_pos, objects, predicate=None, camera_width=96, camera_height=72, verbose=True):
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
        agent = sm.SimpleRlAgent(
            name="agent_" + str(i),
            camera_width=camera_width,
            camera_height=camera_height,
            position=pos,
            scaling=0.9,
        )
        agents.append(agent)

    if predicate is None:
        # Defaults to task on collection of all objects.
        add_collect_all_rewards(agents, objects, verbose)
        add_timeout_rewards(agents)

    return agents
