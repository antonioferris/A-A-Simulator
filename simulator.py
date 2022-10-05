"""
    This file contains code to simulate a game of Axis and Allies Online.

    TODO:
        Compute attack units able to reach a territory using map.py
        Combine defending armies and call calculators simulation code in combat
        Classify territories as Axis / Allies based on powers, use that for plane movement

"""
from ast import Raise
from functools import lru_cache
from troop import Troop, Army, Power, ATTACK_HIT_DIE, DEFENSE_HIT_DIE, LOSS_ORDER_TROOP, AIR_UNITS
import calculator

class CasualtyBall:
    """
        This class precomputes what hitters will be laft after an army takes
        certain casualties, in order to save time during the calculation process.
    """
    def __init__(self, army, attacker, loss_order, need_conquer):
        if attacker:
            HIT_DIE = ATTACK_HIT_DIE
        else:
            HIT_DIE = DEFENSE_HIT_DIE
        self.units = sum(army.troops.values())
        self.land_units = army.troops[Troop.inf] + army.troops[Troop.art] + army.troops[Troop.tank]
        self.need_conquer = need_conquer

        self.troops = army.troops.copy() # copy troops for casualty ball use only
        self.loss_order = loss_order

        hits = [0] * 5
        for troop, cnt in self.troops.items():
            if cnt > 0:
                hits[HIT_DIE[troop]] += cnt

        if need_conquer:
            # save our most valuable land troop
            if self.troops[Troop.tank]:
                self.mvp = Troop.tank
                self.troops[Troop.tank] -= 1
            elif self.troops[Troop.art]:
                self.mvp = Troop.art
                self.troops[Troop.art] -= 1
            elif self.troops[Troop.inf]:
                self.mvp = Troop.inf
                self.troops[Troop.inf] -= 1
            else:
                raise ValueError("Tried to conquer without land units")


        air_losses = [0] * 5
        self.universal_hit_list = [tuple(hits)]
        self.air_loss_list = [tuple(air_losses)]
        for c in loss_order:
            troop = LOSS_ORDER_TROOP[c]
            for _ in range(self.troops[troop]): # for universal hits, we store the hits remaining after n casualties
                hits[HIT_DIE[troop]] -= 1
                self.universal_hit_list.append(tuple(hits))
            if troop in AIR_UNITS: # for air losses, we store the losses taken (in dice #s) after n casualties
                air_losses[HIT_DIE[troop]] += 1
                self.air_loss_list.append(air_losses)

        # finally, our last hero land unit succumbs
        if need_conquer:
            hits[HIT_DIE[self.mvp]] -= 1
            self.universal_hit_list.append(tuple(hits))

        assert(sum(hits) == 0) # we should have 0 remaining troops at this point

    def remaining_hits(self, hits, aa_hits=0):
        """
            this function returns the hit dice remaining after a certain number of hits
            can be called 10,000+ times, needs to be fast!!
        """
        if hits >= self.land_units: # if all land units are hit, just add hits together!
            remaining = self.universal_hit_list[hits + aa_hits]
        else: # otherwise,
            remaining = self.universal_hit_list[hits] # what hit die do we have left from regular units?
            aa_losses = self.air_loss_list[aa_hits]
            remaining = [remaining[i] - aa_losses[i] for i in range(len(remaining))] # subtract out losses from AA
        return remaining

    def remaining_troops(self, hits, aa_hits=0):
        """
            this function returns an Army with the troops left alive after the combat.
            called only n * k times per battle, where n is the number of troops
            and k is the number of AA shots
        """
        r = Army(None)
        # return empty army if no one survived:
        if hits + aa_hits >= self.units:
            return r

        # assume everyone survived, and then kill them off
        r.troops = self.troops.copy()

        # if need_conquer, our MVP survived!!
        if self.need_conquer:
            r.troops[self.mvp] += 1

        if hits < self.land_units: # if hits is too small, we need AA seperate
            for c in self.loss_order:
                troop = LOSS_ORDER_TROOP[c]
                if troop not in AIR_UNITS: # only AA hits here
                    continue
                if self.troops[troop] >= aa_hits:
                    r.troops[troop] -= aa_hits
                    break
                else:
                    aa_hits -= self.troops[troop]
                    r.troops[troop] = 0
        else:
            hits += aa_hits # otherwise, just combine them!

        for c in self.loss_order:
            troop = LOSS_ORDER_TROOP[c]
            if self.troops[troop] >= hits:
                r.troops[troop] -= hits
                return r
            else:
                hits -= self.troops[troop]
                r.troops[troop] = 0

        return r


def battle(attacking_army, defense, need_conquer=True, attack_loss_order="IATFB", defense_loss_order="GIABTF"):
    """
        Given a battle between armies, this function forms a call to calculator.calculate_full_battle
        and then returns.
        Defense can be either an army or a list of armies
        (win_chance, tie_chance, loss_chance, avg_attack_loss, avg_defense_loss)
    """
    if isinstance(defense, list):
       defending_army = sum(defense) # sum all defending armies
    else:
        defending_army = defense

    attack_ball = CasualtyBall(attacking_army, attacker=True, loss_order=attack_loss_order, need_conquer=need_conquer)
    defense_ball = CasualtyBall(defending_army, attacker=False, loss_order=defense_loss_order, need_conquer=False)

    states = calculator.calculate_full_battle(attacking_army, attack_ball, defending_army, defense_ball)
    n = attack_ball.units
    m = defense_ball.units
    orig_attack_val = attacking_army.value()
    orig_defense_val = defending_army.value()

    win_chance, tie_chance, loss_chance = 0, 0, 0
    avg_attack_loss, avg_defense_loss = 0, 0
    for state, prob in states.items():
        if state[0] + state[2] == n and state[1] == m:
            a = Army(None) # empty armies since everything died
            d = Army(None)
            tie_chance = prob
        elif state[0] + state[2] == n:
            a = Army(None)
            d = defense_ball.remaining_troops(state[1])
            loss_chance += prob
            # print(f"{prob:.3f} Chance of defense winning with {state[1]} hits and these units left:\n{a}")
        elif state[1] == m:
            a = attack_ball.remaining_troops(state[0], state[2])
            d = Army(None)
            win_chance += prob
            # print(f"{prob:.3f} Chance of attack winning with {state[0]} hits and these units left:\n{a}")
        else:
            continue # skip non-terminal states
        avg_attack_loss += prob * (orig_attack_val - a.value())
        avg_defense_loss += prob * (orig_defense_val - d.value())


    return win_chance, tie_chance, loss_chance, avg_attack_loss, avg_defense_loss



def test_simple_battle():
    a1 = Army(Power.J)
    a1[Troop.inf] += 2
    a2 = Army(Power.UK)
    a2[Troop.inf] += 1
    win_chance, tie_chance, loss_chance, avg_attack_loss, avg_defense_loss = battle(a1, a2)
    print(f"{win_chance*100:.1f}% win -{avg_attack_loss:.1f} attack IPC, {tie_chance*100:.1f}% tie, {loss_chance*100:.1f}% loss -{avg_defense_loss:.1f} defense IPC")

def main():
    test_simple_battle()

if __name__ == '__main__':
    main()
