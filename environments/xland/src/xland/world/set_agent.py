"""Functions for setting the agent in the world."""

import numpy as np

from simenv import SimpleRlAgent

from ..game.predicates import add_collect_all_rewards, add_random_collectables_rewards, add_timeout_rewards


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
        agent = SimpleRlAgent(
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
