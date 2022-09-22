"""Functions for setting the agent in the world."""

from simulate import SimpleRlAgent

from ..game.generation import add_dummy_generated_reward_fn
from ..game.predicates import (
    add_collect_all_rewards,
    add_near_reward,
    add_random_collectables_rewards,
    add_timeout_rewards,
)


def create_agents(
    agent_pos,
    objects,
    predicate=None,
    verbose=True,
    rank=0,
    camera_width=96,
    camera_height=72,
    n_options=1,
    n_conjunctions=2,
    frame_skip=None,
):
    """
    Create agents in simulate.

    Args:
        agent_pos: list of positions of the agents
        objects: list of objects in the world
        predicate: goal of the agent
            If None, then we use a default task
        camera_width: width of the agent camera
        camera_height: height of the agent camera
        verbose: verbose for debugging
        rank: which map we are working with
        n_options: number of options to be used if generating random tasks
        n_conjunctions: number of conjunctios to be used if generating random tasks
    """

    agents = []

    for i, pos in enumerate(agent_pos):
        agent = SimpleRlAgent(
            name="agent_" + str(rank) + "_" + str(i),
            position=pos,
            camera_height=camera_height,
            camera_width=camera_width,
            scaling=[0.8, 0.8, 0.8],
        )
        agents.append(agent)

    if predicate == "random":
        add_dummy_generated_reward_fn(
            agents, objects, n_conjunctions=n_conjunctions, n_options=n_options, verbose=verbose
        )

    elif predicate == "near":
        add_near_reward(agents, objects, verbose=verbose)

    elif predicate == "collect_all":
        add_collect_all_rewards(agents, objects, verbose=verbose)

    elif predicate == "collect_random_collectables":
        add_random_collectables_rewards(agents, objects, verbose=verbose)

    else:
        raise ValueError("Only `random`, `near`, `collect_all`, `collect_random_collectables` are supported.")

    add_timeout_rewards(agents, frame_skip=frame_skip)

    return agents
