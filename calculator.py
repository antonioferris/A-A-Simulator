"""
    This file contains the calculator for A&A battles.

    TODO: Allow custom removal order
"""
from scipy.stats import binom, norm
import itertools
from functools import reduce, lru_cache
from time import time

import numpy as np
from troop import Army, Troop, ATTACK_HIT_DIE, DEFENSE_HIT_DIE

def timer(func):
    # This function shows the execution time of
    # the function object passed
    def wrap_func(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        print(f'Function {func.__name__!r} executed in {(t2-t1):.4f}s')
        return result
    return wrap_func

def combine_dist(dist1, dist2):
    """
        Combines two distributions of hits.
        For example, combing two 50/50 distributions creates a 25 / 50 / 25 distribution.
    """
    new_len = len(dist1) + len(dist2) - 1
    total_dist = [0.0] * new_len
    for (hit1, prob1), (hit2, prob2) in itertools.product(enumerate(dist1), enumerate(dist2)):
        total_dist[hit1 + hit2] += prob1 * prob2

    if not abs(1 - sum(total_dist)) <= 1e-5:
        print(dist1, dist2)
    assert(abs(1 - sum(total_dist)) <= 1e-5)

    return tuple(total_dist)


def hit_dist(hitters, die):
    """
        Computes the binomial hit distribution of hitters given the die.

        Cached for speeding up computation since this will be called a TON.
    """
    b = binom(hitters, die / 6)
    dist = [b.pmf(j) for j in range(0, hitters + 1)]
    return tuple(dist)

def pure_hits(hit_counts):
    """
        Perfectly computes the probability of different total numbers of hits.

        hit_counts is a list of the number of hitters on 1, 2, 3, 4.
    """
    if len(hit_counts) == 5:
        hit_counts = hit_counts[1:] # remove AA guns (hit 0) from consideration

    n = sum(hit_counts)
    if n == 0:
        return (1.0,)

    sub_dists = [] # list of distribution for each hit count

    for i in range(1, 5): # compute the distribution of hits for each bernoulli
        m = hit_counts[i-1]
        if m  == 0:
            continue
        sub_dist = hit_dist(m, i)
        sub_dists.append(sub_dist)

    # we iteratively combine the distributions of hits to move from 4 small distributions to 1 large distribution
    total_dist = list(reduce(combine_dist, sub_dists))

    # make sure our probability sums to 1!
    assert(abs(1 - sum(total_dist)) <= 1e-5)

    return tuple(total_dist)



def calculate_full_battle(attacking_army, attack_casualty_ball, defending_army, defense_casualty_ball):
    """
        Simulates a given battle
        and then returns a tuple (win_chance, tie_chance, loss_chance, avg_attack_loss, avg_defense_loss)

        We simulate the battle using markov chains with a state being (h1, h2, a), the number of offense hits,
        defense hits, and aa gun hits
    Args:
        attacking_army (troop.Army):
        defending_army (troop.Army):

    Returns:
        a dictionary of states
    """
    n, m = attack_casualty_ball.combatants, defense_casualty_ball.combatants

    # first, compute AA gun hits. Sadly, this can't be part of our markov chain because the hits are out of order.
    aa_dice = min(defending_army[Troop.aa] * 3, attacking_army[Troop.fighter] + attacking_army[Troop.bomber])
    aa = hit_dist(aa_dice, 1) # AA hit on a 1 only during AA step

    # next, compute the shore bombardment for the attacker.
    land_units = attacking_army[Troop.inf] + attacking_army[Troop.art] + attacking_army[Troop.tank]
    num_bombard = min(attacking_army[Troop.cruiser] + attacking_army[Troop.battleship], land_units)

    battleship_bombard = 0
    cruiser_bombard = 0
    if num_bombard > attacking_army[Troop.battleship]: # if we have bombard for battleships and cruisers
        battleship_bombard = attacking_army[Troop.battleship]
        num_bombard -= battleship_bombard
        cruiser_bombard = min(attacking_army[Troop.cruiser], num_bombard)
    else:
        battleship_bombard = min(attacking_army[Troop.battleship], num_bombard)

    bombard = combine_dist(hit_dist(cruiser_bombard, ATTACK_HIT_DIE[Troop.cruiser]), hit_dist(battleship_bombard, ATTACK_HIT_DIE[Troop.battleship]))

    states = {(i, j, k) : 0.0 for i in range(n + 1) for j in range(m + 1) for k in range(aa_dice + 1)}

    # initial states are based on aa hits
    for (aa_hit, state_prob) in enumerate(aa):
        hits_by_1 = pure_hits(attack_casualty_ball.remaining_hits(0, aa_hit))
        hits_by_1 = combine_dist(hits_by_1, bombard) # add bombard damage to initial damage by attackers.
        hits_by_2 = pure_hits(defense_casualty_ball.remaining_hits(0))

        # basically the same as regular transition, except we don't normalize out the self-transition
        # because we are applying bombard here. Self-transition is the probability of no bombard hits.
        for (hit_by_1, prob1), (hit_by_2, prob2) in itertools.product(enumerate(hits_by_1), enumerate(hits_by_2)):
            hit_on_2 = min(m, hit_by_1) # can't be hit more times than you have units
            hit_on_1 = min(n - aa_hit, hit_by_2)
            states[(hit_on_1, hit_on_2, aa_hit)] += state_prob * prob1 * prob2

    # we loop over "state classes" here, which is casualties.
    # 2 states with the same total can never transition to each other, so they are unconnected in our markov chain!
    # i..e doesn't matter what hits you get, (1, 1) can't transition to (2, 0). Can't undo a hit.
    # TODO increase efficiency by exploiting the point where states might transpose if air units are taken as casualties
    # for regular hits. Then, an AA hit is the same as a regular hit
    for state_class in range(0, n + m):
        for k in range(aa_dice + 1):
            for q in range(state_class + 1):
                # we are in state (state_class - q, q) here
                curr_state = (state_class - q, q, k)

                if curr_state not in states:
                    continue
                if curr_state[0] + k >= n or curr_state[1] >= m: # skip states where one side is dead
                    continue

                # how many attackers / defenders are hitting in this state?
                hitters_1 = attack_casualty_ball.remaining_hits(curr_state[0], curr_state[2])
                hitters_2 = defense_casualty_ball.remaining_hits(curr_state[1])

                hits_by_1 = pure_hits(hitters_1) # what hits will the remaining 1 army have?
                hits_by_2 = pure_hits(hitters_2) # what hits will the remaining 2 army have?

                # normalize away the self-transition of no one hitting anything
                p1, p2 = hits_by_1[0], hits_by_2[0]
                normalizer = (1 / (1 - p1 * p2))

                # now, we add the corresponding transitions to other states
                transitions = itertools.product(enumerate(hits_by_1), enumerate(hits_by_2))
                next(transitions) # skip the initial self-transition

                psum = 0
                for (hit_by_1, prob1), (hit_by_2, prob2) in transitions:
                    hit_on_2 = min(m, hit_by_1 + curr_state[1]) # can't be hit more times than you have units
                    hit_on_1 = min(n - k, hit_by_2 + curr_state[0])
                    psum += prob1 * prob2 * normalizer
                    states[(hit_on_1, hit_on_2, k)] += states[curr_state] * prob1 * prob2 * normalizer


                if abs(psum - 1) >= 1e-5:
                    print("ERROR: State probabilities don't add up.", psum, k, state_class, q, curr_state)

    return states