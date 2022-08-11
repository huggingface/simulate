"""
Predicate selection for the game.
"""

import numpy as np

from .predicates import and_reward, near, not_reward, or_reward, see


def add_dummy_generated_reward_fn(
    objects, agents, predicates=None, n_conjunctions=2, n_options=1, verbose=True, strictly_agent_object=False
):
    """
    Generate the game.
    """

    predicates = [near, see] if predicates is None else predicates
    instances = objects + agents
    # String that contains human readable description of the game
    predicate = ""

    # For each option, select n_conjunctions predicates.
    # With 50% of probability, use not
    # We will choose a single object for each predicate.
    for option in range(n_options):
        # Select objects and conjunctions:
        done = False
        while not done:
            conjs = np.random.choice(predicates, size=n_conjunctions, replace=True)
            near_conjs = np.array([conj.__name__ == "near" for conj in conjs])
            nb_near_conjs = np.sum(near_conjs.astype(int))
            objs1 = np.full(n_conjunctions, fill_value=len(objects))

            if not strictly_agent_object:
                # 50 % of chance of having the agent on the predicate for near predicates
                objs1[near_conjs] = np.random.choice(2 * len(objects), size=nb_near_conjs, replace=False)

            objs2 = np.random.choice(len(objects), size=n_conjunctions, replace=False)
            if np.all(objs1 != objs2):
                done = True

        objs1[objs1 >= len(objects)] = len(objects)
        not_conjs = np.random.choice([0, 1], size=n_conjunctions, replace=True)

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
