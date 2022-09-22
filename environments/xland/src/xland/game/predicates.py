"""Possible predicates for XLand.

When selecting randomly predicates:

The pseudo-algorithm on XLand supposes a multi-agent setting which
is not the case yet. So we implement the random selection of predicates
in a simpler way by just randomly choosing pairs of two objects (one of which might
be the agent), and applying the `be near` task to them. We randomly choose to negate
this predicate, and in the end we combine different predicates the same
way as in XLand - in the disjunctive normal form, which is a canonical
representation of boolean formula.
Example: [(obj1 near obj2) and (agent near obj1)] or [!(obj3 near obj4) and (agent near obj1)]
            or [(obj2 near obj3) and !(agent near obj2)].
        In this particular example, we have 3 options and 2 conjunctions on each option.

The original possible predicates on Xland were: being
near, on, seeing, and holding, as well as their negations,
with the entities being objects, players, and floors of the
topology. However, due to limitations on the library, we will only consider
the predicates near, and seeing, and the negations of these. We also don't
take the floor into consideration to simplify things.
"""

import numpy as np

from simulate import RewardFunction


def near(entity_a, entity_b, reward_type="sparse"):
    return RewardFunction(
        type=reward_type,
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


def see(agent, entity_b):
    return RewardFunction(
        type="see",
        entity_a=agent,
        entity_b=entity_b,
        distance_metric="euclidean",
        threshold=30.0,
        is_terminal=False,
        is_collectable=False,
        scalar=1.0,
        trigger_once=False,
    )


def and_reward(reward_function_a, reward_function_b, agent, is_terminal=False):
    return RewardFunction(
        type="and",
        entity_a=agent,
        entity_b=agent,
        distance_metric="euclidean",
        reward_function_a=reward_function_a,
        reward_function_b=reward_function_b,
        is_terminal=is_terminal,
    )


def or_reward(reward_function_a, reward_function_b, agent, is_terminal=False):
    return RewardFunction(
        type="or",
        entity_a=agent,
        entity_b=agent,
        distance_metric="euclidean",
        reward_function_a=reward_function_a,
        reward_function_b=reward_function_b,
        is_terminal=is_terminal,
    )


def not_reward(reward_function_a, agent, is_terminal=False):
    return RewardFunction(
        type="not",
        entity_a=agent,
        entity_b=agent,
        distance_metric="euclidean",
        reward_function_a=reward_function_a,
        is_terminal=is_terminal,
    )


def hold():
    raise NotImplementedError


def on():
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
    # TODO: print what the agent will collect if verbose parameter is True
    """
    terminal = False
    if len(objects) == 1:
        terminal = True

    for agent in agents:
        for obj in objects:
            reward_function = RewardFunction(
                type="sparse",
                entity_a=agent,
                entity_b=obj,
                distance_metric="euclidean",
                threshold=1.0,
                is_terminal=terminal,
                is_collectable=True,
            )

            agent.add_reward_function(reward_function)


def add_near_reward(agents, objects, verbose=False):
    """
    Agents have to be near one of the objects.

    TODO: print task if verbose is True
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
                is_collectable=False,
            )

            agent.add_reward_function(reward_function)


def add_timeout_rewards(agents, scalar=0.0, frame_skip=None):
    frame_skip = 1 if frame_skip is None else frame_skip
    for agent in agents:
        timeout_reward_function = RewardFunction(
            type="timeout",
            entity_a=agent,
            entity_b=agent,
            distance_metric="euclidean",
            threshold=1000 // frame_skip,
            is_terminal=True,
            scalar=scalar,
        )

        agent.add_reward_function(timeout_reward_function)
