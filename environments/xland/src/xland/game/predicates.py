"""Possible predicates for XLand."""

import numpy as np

from simenv import RewardFunction


""" When selecting randomly predicates """


def near(entity_a, entity_b):
    return RewardFunction(
        type="sparse",
        entity_a=entity_a,
        entity_b=entity_b,
        distance_metric="euclidean",
        threshold=1.0,
        is_terminal=False,
        is_collectable=False,
        scalar=1.0,
        trigger_once=False,
    )


def collect(entity_a, entity_b):
    return RewardFunction(
        type="sparse",
        entity_a=entity_a,
        entity_b=entity_b,
        distance_metric="euclidean",
        threshold=1.0,
        is_terminal=False,
        is_collectable=True,
        scalar=1.0,
    )


def and_reward(reward_function_a, reward_function_b, agent):
    return RewardFunction(
        type="and",
        entity_a=agent,
        entity_b=agent,
        distance_metric="euclidean",
        reward_function_a=reward_function_a,
        reward_function_b=reward_function_b,
    )


def or_reward(reward_function_a, reward_function_b, agent):
    return RewardFunction(
        type="or",
        entity_a=agent,
        entity_b=agent,
        distance_metric="euclidean",
        reward_function_a=reward_function_a,
        reward_function_b=reward_function_b,
    )


def not_reward(reward_function_a, agent):
    return RewardFunction(
        type="not",
        entity_a=agent,
        entity_b=agent,
        distance_metric="euclidean",
        reward_function_a=reward_function_a,
    )


def hold():
    raise NotImplementedError


def on():
    raise NotImplementedError


def see():
    raise NotImplementedError


""" Default behaviours """


def add_random_collectables_rewards(agents, objects, verbose=False):
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
        reward_function = RewardFunction(
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


def add_collect_all_rewards(agents, objects, verbose=False):
    """
    Second default task when no predicate is given.

    All agents have to collect all objects.
    """
    for agent in agents:
        for obj in objects:
            reward_function = RewardFunction(
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
        timeout_reward_function = RewardFunction(
            type="timeout",
            entity_a=agent,
            entity_b=agent,
            distance_metric="euclidean",
            threshold=1000,
            is_terminal=True,
            scalar=0.0,
        )

        agent.add_reward_function(timeout_reward_function)
