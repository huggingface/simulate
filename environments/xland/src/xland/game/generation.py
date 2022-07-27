"""
Predicate selection for the game.
"""

import numpy as np

from .predicates import and_reward, near, not_reward, or_reward


def add_dummy_generated_reward_fn(objects, agents, n_conj=2, n_options=1, verbose=True, strictly_agent_object=False):
    """
    Generate the game.
    """

    predicates = [near]
    instances = objects + agents
    # String that contains human readable description of the game
    predicate = ""

    # For each option, select n_conj predicates.
    # With 50% of probability, use not
    # We will choose a single object for each predicate.
    for option in range(n_options):
        # Select objects and conjunctions:
        done = False
        while not done:
            if strictly_agent_object:
                objs1 = np.full(n_conj, fill_value=len(objects))
            else:
                # 50 % of chance of having the agent on the predicate
                objs1 = np.random.choice(2 * len(objects), size=n_conj, replace=False)
            objs2 = np.random.choice(len(objects), size=n_conj, replace=False)
            if np.all(objs1 != objs2):
                done = True

        objs1[objs1 >= len(objects)] = len(objects)
        conjs = np.random.choice(predicates, size=n_conj, replace=True)
        not_conjs = np.random.choice([0, 1], size=n_conj, replace=True)

        for i, (obj1, obj2, conj, not_conj) in enumerate(zip(objs1, objs2, conjs, not_conjs)):
            predicate_reward = conj(instances[obj1], instances[obj2])
            if not_conj:
                predicate_reward = not_reward(predicate_reward, agents[0])

            not_keyword = "not " if not_conj else ""

            if i == 0:
                option_reward = predicate_reward
                predicate += (
                    not_keyword + instances[obj1].name + " " + conj.__name__ + " " + instances[obj2].name + " "
                )
            else:
                option_reward = and_reward(option_reward, predicate_reward, agents[0])
                predicate += (
                    "and "
                    + not_keyword
                    + instances[obj1].name
                    + " "
                    + conj.__name__
                    + " "
                    + instances[obj2].name
                    + " "
                )

        if option == 0:
            reward_function = option_reward
        else:
            reward_function = or_reward(reward_function, option_reward, agents[0])

        if option < n_options - 1:
            predicate += "or "

    # For now we are dealing with a single agent
    if verbose:
        print(predicate)

    agents[0].add_reward_function(reward_function)
