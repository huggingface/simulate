"""Functions for setting the agent in the world."""

from simenv import CameraSensor, SimpleRlAgent

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
    camera_width=96,
    camera_height=72,
    verbose=True,
    n_instance=0,
    n_options=1,
    n_conjunctions=2,
):
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
        n_instance: which map we are working with
        n_options: number of options to be used if generating random tasks
        n_conjunctions: number of conjunctios to be used if generating random tasks
    """

    agents = []

    for i, pos in enumerate(agent_pos):
        agent = SimpleRlAgent(
            name="agent_" + str(n_instance) + "_" + str(i),
            sensors=[CameraSensor(width=camera_width, height=camera_height, position=[0, 0.75, 0])],
            position=pos,
            scaling=[0.8, 0.8, 0.8],
        )
        agents.append(agent)

    if predicate == "random":
        add_dummy_generated_reward_fn(objects, agents, n_conjunctions=n_conjunctions, n_options=n_options)

    elif predicate == "near":
        add_near_reward(objects, agents)

    elif predicate == "collect_all":
        add_collect_all_rewards(agents, objects, verbose)

    elif predicate == "collect_random_collectables":
        add_random_collectables_rewards(agents, objects, verbose)

    else:
        raise ValueError("Only `random`, `near`, `collect_all`, `collect_random_collectables` are supported.")

    add_timeout_rewards(agents)

    return agents
