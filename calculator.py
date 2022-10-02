"""
    This file contains the calculator for A&A battles.

    TODO: Allow custom removal order
"""
from scipy.stats import binom, norm
import itertools
from functools import reduce, lru_cache
from time import time

import numpy as np
from troop import Army, Troop

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

    assert(abs(1 - sum(total_dist)) <= 1e-5)

    return total_dist


def pure_hits(hit_counts):
    """
        Perfectly computes the probability of different total numbers of hits.

        hit_counts is a list of the number of hitters on 1, 2, 3, 4.
    """
    if len(hit_counts) == 5:
        hit_counts = hit_counts[1:] # remove AA guns (hit 0) from consideration

    n = sum(hit_counts)

    sub_dists = [] # list of distribution for each hit count

    for i in range(1, 5): # compute the distribution of hits for each bernoulli
        m = hit_counts[i-1]
        if m  == 0:
            continue
        b = binom(m, i / 6) # distribution for this set of hitters TODO CACHE
        sub_dist = [b.pmf(j) for j in range(0, m+1)] # store hit count, prob for this class of hitters
        sub_dists.append(sub_dist)

    # we iteratively combine the distributions of hits to move from 4 small distributions to 1 large distribution
    total_dist = list(reduce(combine_dist, sub_dists))

    # make sure our probability sums to 1!
    assert(abs(1 - sum(total_dist)) <= 1e-5)

    return total_dist

def approx_hits(hit_counts):
    """
        Approximately computes the probability of different total numbers of hits.
        Uses normal distributions to approximate.

        hit_counts is a list of the number of hitters on 1, 2, 3, 4.
    """
    if len(hit_counts) == 5:
        hit_counts = hit_counts[1:] # remove AA guns (hit 0) from consideration

    total_mu, total_var = 0, 0
    for i in range(1, 5):
        n, p = hit_counts[i-1], i / 6
        total_mu += n * p # this is the normal approximation of the binomial
        total_var += n * p * (1 - p)

    norm_dist = norm(total_mu, total_var) # this is the normal approximation of the sum of the component parts

    n = sum(hit_counts)

    raw_dist = [0.0] * (n + 1)
    for i in range(n + 1):
        raw_dist[i] += norm_dist.pdf(i)

    normalization_constant = sum(raw_dist)
    total_dist = [raw_dist[i] / normalization_constant for i in range(n + 1)] # need to normalize because the normal extends beyond [0, n]

    return total_dist

def after_hit(hit_count, hits_taken, removal_list=None):
    """
        Calculate the new hit count list after the casualties
    """
    new_hit_count = [hit_count[i] for i in range(5)]
    for i in range(5):
        if new_hit_count[i] >= hits_taken:
            new_hit_count[i] -= hits_taken
            break
        else:
            hits_taken -= new_hit_count[i]
            new_hit_count[i] = 0

    return new_hit_count


@timer
def calculate_battle(hit_counts_1, hit_counts_2, removal_list_1=None, removal_list_2=None, hits=pure_hits):
    """
        This function treats an A&A battle as a markov chain, where each state
        is a tuple (i, j) where i is the casualties side 1 sustained, and j is the casualties side 2 sustained.

        Since we are just doing land battles, we don't need to worry about a situation where there's a tie. We just
        keep transitioning the markov chain according to probabilities until we hit an end state.

        A very simple example: 1 tank v 2 tank.

        start state: (0, 0) - no casualties left.
        There is a 12.5% chance to transition to (0, 1) - attacking tank hit, both defending tanks miss
        There is a 25% chance to transition to (1, 1) - both sides get a hit

        And so on.

        removal_list is an ordered list of what hit is removed as casualty each time.
        hit_counts is a list with five elements, representing the number of troops that hit on 0, 1, 2, 3, and 5 respectively.
        hit_counts[1:] is passed on to a hit calculator to calculate our transition probabilities.
    """
    n, m = sum(hit_counts_1), sum(hit_counts_2)

    states = {(i, j) : 0.0 for i in range(n+1) for j in range(m+1)}
    states[(0, 0)] = 1.0 # starting state is guaranteed

    # we loop over "state classes" here, which is the total casualties.
    # 2 states with the same total can never transition to each other, so they are unconnected in our markov chain!
    # i..e doesn't matter what hits you get, (1, 1) can't transition to (2, 0). Can't undo a hit.
    for state_class in range(0, n + m):
        for k in range(state_class + 1):
            # we are in state (state_class - k, k) here.
            curr_state =  (state_class - k, k)
            if curr_state not in states:
                continue
            if curr_state[0] == n or curr_state[1] == m: # skip states where one side is dead
                continue

            hits_by_1 = hits(after_hit(hit_counts_1, curr_state[0])) # what hits will the remaining 1 army have?
            hits_by_2 = hits(after_hit(hit_counts_2, curr_state[1])) # what hits will the remaining 2 army have?

            # normalize away the self-transition of no one hitting anything
            p1, p2 = hits_by_1[0], hits_by_2[0]
            normalizer = (1 / (1 - p1 * p2))

            # now, we add the corresponding transitions to other states
            transitions = itertools.product(enumerate(hits_by_1), enumerate(hits_by_2))
            next(transitions) # skip the initial self-transition

            for (hit_by_1, prob1), (hit_by_2, prob2) in transitions:
                hit_on_2 = min(m, curr_state[1] + hit_by_1) # can't be hit more times than you have units
                hit_on_1 = min(n, curr_state[0] + hit_by_2)
                states[(hit_on_1, hit_on_2)] += states[curr_state] * prob1 * prob2 * normalizer

    return states

def calculate_full_battle(attacking_army, attack_loss_order, defending_army, defense_loss_order):
    """
        Simulates a given battle
        and then returns a tuple (win_chance, tie_chance, loss_chance, avg_attack_loss, avg_defense_loss)

    Args:
        attacking_army (_type_): _description_
        defending_armies (_type_): _description_

    Returns:

    """
    # first, compute AA gun hits. Sadly, this can't be part of our markov chain because the hits are out of order.
    if defending_army[Troop.aa] > 0:
        aa_dice = min(defending_army[Troop.aa] * 3, attacking_army[Troop.fighter] + attacking_army[Troop.bomber])
        b = binom(aa_dice, 1 / 6) # distribution for this set of hitters
        sub_dist = [b.pmf(j) for j in range(0, m+1)] # store hit count, prob for this class of hitters

    n, m = sum(hit_counts_1), sum(hit_counts_2)

    states = {(i, j) : 0.0 for i in range(n+1) for j in range(m+1)}
    states[(0, 0)] = 1.0 # starting state is guaranteed

    # we loop over "state classes" here, which is the total casualties.
    # 2 states with the same total can never transition to each other, so they are unconnected in our markov chain!
    # i..e doesn't matter what hits you get, (1, 1) can't transition to (2, 0). Can't undo a hit.
    for state_class in range(0, n + m):
        for k in range(state_class + 1):
            # we are in state (state_class - k, k) here.
            curr_state =  (state_class - k, k)
            if curr_state not in states:
                continue
            if curr_state[0] == n or curr_state[1] == m: # skip states where one side is dead
                continue

            hits_by_1 = hits(after_hit(hit_counts_1, curr_state[0])) # what hits will the remaining 1 army have?
            hits_by_2 = hits(after_hit(hit_counts_2, curr_state[1])) # what hits will the remaining 2 army have?

            # normalize away the self-transition of no one hitting anything
            p1, p2 = hits_by_1[0], hits_by_2[0]
            normalizer = (1 / (1 - p1 * p2))

            # now, we add the corresponding transitions to other states
            transitions = itertools.product(enumerate(hits_by_1), enumerate(hits_by_2))
            next(transitions) # skip the initial self-transition

            for (hit_by_1, prob1), (hit_by_2, prob2) in transitions:
                hit_on_2 = min(m, curr_state[1] + hit_by_1) # can't be hit more times than you have units
                hit_on_1 = min(n, curr_state[0] + hit_by_2)
                states[(hit_on_1, hit_on_2)] += states[curr_state] * prob1 * prob2 * normalizer

    return states



def simple_battle(h1, h2):
    states = calculate_battle(h1, h2)
    n, m = sum(h1), sum(h2)
    win_chance = sum(states[(i, m)] for i in range(n))
    tie_chance = states[(n, m)]
    loss_chance = sum(states[(n, i)] for i in range(m))
    return win_chance, tie_chance, loss_chance


def test_calc():
    h1, h2 = [0, 0, 0, 3, 0], [0, 0, 0, 3, 0]
    w, t, l = simple_battle(h1, h2)
    assert(abs(w - l) <= 1e-5)

    h1, h2 = [0, 0, 10, 5, 5], [0, 5, 5, 5, 5]
    w, t, l = simple_battle(h1, h2)
    assert(.58 < w < .59)
    assert(.39 < l < .40)

    h1, h2 = [0, 2, 1, 0, 0], [0, 1, 0, 1, 0]
    w, t, l = simple_battle(h1, h2)
    assert(.62 < w < .63)
    assert(.29 < l < .30)

    # Currently Failing
    # h1, h2 = [25, 30, 10, 5, 4], [0, 0, 60, 3, 10]
    # w, t, l = simple_battle(h1, h2)
    # print(w, t, l)
    # # assert(.32 < w < .33)
    # # assert(.67 < l < .68)

def test_approx():
    h = [0, 3, 0, 0]
    d1 = np.array(pure_hits(h))
    d2 = np.array(approx_hits(h))

    print(np.allclose(d1, d2))
    print(np.max(np.abs(d1 - d2)))

    h = [0, 3, 2, 1]
    d1 = np.array(pure_hits(h))
    d2 = np.array(approx_hits(h))

    print(np.allclose(d1, d2))
    print(np.max(np.abs(d1 - d2)))

    h = [30, 30, 70, 30]
    d1 = np.array(pure_hits(h))
    d2 = np.array(approx_hits(h))

    print(np.allclose(d1, d2))
    print(np.max(np.abs(d1 - d2)))



def main():
    test_calc()

if __name__ == '__main__':
    main()