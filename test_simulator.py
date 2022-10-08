"""
    A file for testing the functionality of simulator.py
"""
import unittest
import sys
sys.path.append('..')


from troop import Troop, Army, Power
from simulator import battle

class Basic(unittest.TestCase):

    def test_inf_small(self):
        a1 = Army(Power.J)
        a1[Troop.inf] += 2
        a2 = Army(Power.UK)
        a2[Troop.inf] += 1
        win_chance, tie_chance, loss_chance, avg_attack_loss, avg_defense_loss = battle(a1, a2)
        accuracy_decimal = 2

        self.assertAlmostEqual(win_chance, 0.677, places=accuracy_decimal)
        self.assertAlmostEqual(loss_chance, 0.269, places=accuracy_decimal)
        self.assertAlmostEqual(tie_chance, 1 - win_chance - loss_chance, places=accuracy_decimal)
        self.assertAlmostEqual(avg_attack_loss, 2.8, places=1)
        self.assertAlmostEqual(avg_defense_loss, 2.2, places=1)

    def test_inf_medium(self):
        a1 = Army(Power.J)
        a1[Troop.inf] += 10
        a2 = Army(Power.UK)
        a2[Troop.inf] += 4
        win_chance, tie_chance, loss_chance, avg_attack_loss, avg_defense_loss = battle(a1, a2)
        accuracy_decimal = 2

        self.assertAlmostEqual(win_chance, 0.977, places=accuracy_decimal)
        self.assertAlmostEqual(loss_chance, 0.022, places=accuracy_decimal)
        self.assertAlmostEqual(tie_chance, 1 - win_chance - loss_chance, places=accuracy_decimal)
        self.assertAlmostEqual(avg_attack_loss, 8.7, places=0)
        self.assertAlmostEqual(avg_defense_loss, 11.9, places=0)

    def test_bombard(self):
        a1 = Army(Power.US)
        a1[Troop.inf] += 2
        a1[Troop.tank] += 2
        a1[Troop.cruiser] += 1
        a1[Troop.battleship] += 1
        a2 = Army(Power.G)
        a2[Troop.inf] += 6
        win_chance, tie_chance, loss_chance, avg_attack_loss, avg_defense_loss = battle(a1, a2)
        accuracy_decimal = 2

        self.assertAlmostEqual(win_chance, 0.273, places=accuracy_decimal)
        self.assertAlmostEqual(loss_chance, 0.692, places=accuracy_decimal)
        self.assertAlmostEqual(tie_chance, 1 - win_chance - loss_chance, places=accuracy_decimal)
        self.assertAlmostEqual(avg_attack_loss, 15.2, places=0)
        self.assertAlmostEqual(avg_defense_loss, 12.1, places=0)

    def test_aa_basic(self):
        a1 = Army(Power.US)
        a1[Troop.fighter] += 1
        a2 = Army(Power.G)
        a2[Troop.aa] += 1
        win_chance, tie_chance, loss_chance, avg_attack_loss, avg_defense_loss = battle(a1, a2, need_conquer=False)
        accuracy_decimal = 2

        self.assertAlmostEqual(win_chance, 0.833, places=accuracy_decimal)
        self.assertAlmostEqual(loss_chance, 0.167, places=accuracy_decimal)
        self.assertAlmostEqual(tie_chance, 1 - win_chance - loss_chance, places=accuracy_decimal)
        self.assertAlmostEqual(avg_attack_loss, 1.7, places=0)
        self.assertAlmostEqual(avg_defense_loss, 4.2, places=0)

    def test_aa_simple(self):
        a1 = Army(Power.US)
        a1[Troop.fighter] += 1
        a2 = Army(Power.G)
        a2[Troop.inf] += 1
        a2[Troop.aa] += 1
        win_chance, tie_chance, loss_chance, avg_attack_loss, avg_defense_loss = battle(a1, a2, need_conquer=False)
        accuracy_decimal = 2

        self.assertAlmostEqual(win_chance, 0.208, places=accuracy_decimal)
        self.assertAlmostEqual(loss_chance, 0.688, places=accuracy_decimal)
        self.assertAlmostEqual(tie_chance, 1 - win_chance - loss_chance, places=accuracy_decimal)
        self.assertAlmostEqual(avg_attack_loss, 7.9, places=0)
        self.assertAlmostEqual(avg_defense_loss, 4.1, places=0)

    def test_aa(self):
        a1 = Army(Power.US)
        a1[Troop.inf] += 1
        a1[Troop.tank] += 1
        a1[Troop.fighter] += 1
        a2 = Army(Power.G)
        a2[Troop.inf] += 3
        a2[Troop.aa] += 1
        win_chance, tie_chance, loss_chance, avg_attack_loss, avg_defense_loss = battle(a1, a2)
        accuracy_decimal = 2

        self.assertAlmostEqual(win_chance, 0.325, places=accuracy_decimal)
        self.assertAlmostEqual(loss_chance, 0.626, places=accuracy_decimal)
        self.assertAlmostEqual(tie_chance, 1 - win_chance - loss_chance, places=accuracy_decimal)
        self.assertAlmostEqual(avg_attack_loss, 15.2, places=0)
        self.assertAlmostEqual(avg_defense_loss, 9.6, places=0)

    def test_air_bombard(self):
        a1 = Army(Power.US)
        a1[Troop.inf] += 1
        a1[Troop.tank] += 1
        a1[Troop.fighter] += 2
        a1[Troop.cruiser] += 1
        a2 = Army(Power.G)
        a2[Troop.inf] += 5
        a2[Troop.aa] += 1
        win_chance, tie_chance, loss_chance, avg_attack_loss, avg_defense_loss = battle(a1, a2)
        accuracy_decimal = 2

        self.assertAlmostEqual(win_chance, 0.229, places=accuracy_decimal)
        self.assertAlmostEqual(loss_chance, 0.743, places=accuracy_decimal)
        self.assertAlmostEqual(tie_chance, 1 - win_chance - loss_chance, places=accuracy_decimal)
        self.assertAlmostEqual(avg_attack_loss, 25.6, places=0)
        self.assertAlmostEqual(avg_defense_loss, 12.8, places=0)

    def test_nonconquer(self):
        a1 = Army(Power.US)
        a1[Troop.inf] += 1
        a1[Troop.bomber] += 2
        a2 = Army(Power.G)
        a2[Troop.inf] += 3
        win_chance, tie_chance, loss_chance, avg_attack_loss, avg_defense_loss = battle(a1, a2, need_conquer=False)
        accuracy_decimal = 2

        self.assertAlmostEqual(win_chance, 0.748, places=accuracy_decimal)
        self.assertAlmostEqual(loss_chance, 0.181, places=accuracy_decimal)
        self.assertAlmostEqual(tie_chance, 1 - win_chance - loss_chance, places=accuracy_decimal)
        self.assertAlmostEqual(avg_attack_loss, 11.8, places=0)
        self.assertAlmostEqual(avg_defense_loss, 8.2, places=0)

    def test_art_basic(self):
        a1 = Army(Power.R)
        a1[Troop.inf] += 1
        a1[Troop.art] += 1
        a2 = Army(Power.J)
        a2[Troop.inf] += 1
        win_chance, tie_chance, loss_chance, avg_attack_loss, avg_defense_loss = battle(a1, a2, need_conquer=False)
        accuracy_decimal = 2

        self.assertAlmostEqual(win_chance, 0.874, places=accuracy_decimal)
        self.assertAlmostEqual(loss_chance, 0.084, places=accuracy_decimal)
        self.assertAlmostEqual(tie_chance, 1 - win_chance - loss_chance, places=accuracy_decimal)
        self.assertAlmostEqual(avg_attack_loss, 1.9, places=0)
        self.assertAlmostEqual(avg_defense_loss, 2.7, places=0)

    def test_art_simple(self):
        a1 = Army(Power.R)
        a1[Troop.inf] += 4
        a1[Troop.art] += 2
        a2 = Army(Power.J)
        a2[Troop.inf] += 6
        win_chance, tie_chance, loss_chance, avg_attack_loss, avg_defense_loss = battle(a1, a2)
        accuracy_decimal = 2

        self.assertAlmostEqual(win_chance, 0.413, places=accuracy_decimal)
        self.assertAlmostEqual(loss_chance, 0.565, places=accuracy_decimal)
        self.assertAlmostEqual(tie_chance, 1 - win_chance - loss_chance, places=accuracy_decimal)
        self.assertAlmostEqual(avg_attack_loss, 15.8, places=0)
        self.assertAlmostEqual(avg_defense_loss, 12.9, places=0)

    def test_everything_small(self):
        a1 = Army(Power.US)
        a1[Troop.inf] += 2
        a1[Troop.art] += 1
        a1[Troop.tank] += 1
        a1[Troop.bomber] += 1
        a1[Troop.cruiser] += 1
        a2 = Army(Power.G)
        a2[Troop.inf] += 6
        a2[Troop.aa] += 1
        win_chance, tie_chance, loss_chance, avg_attack_loss, avg_defense_loss = battle(a1, a2)
        accuracy_decimal = 2

        self.assertAlmostEqual(win_chance, 0.303, places=accuracy_decimal)
        self.assertAlmostEqual(loss_chance, 0.670, places=accuracy_decimal)
        self.assertAlmostEqual(tie_chance, 1 - win_chance - loss_chance, places=accuracy_decimal)
        self.assertAlmostEqual(avg_attack_loss, 23.1, places=0)
        self.assertAlmostEqual(avg_defense_loss, 16.2, places=0)

    @unittest.skip("not done yet")
    def test_everything_medium(self):
        a1 = Army(Power.US)
        a1[Troop.inf] += 13
        a1[Troop.art] += 4
        a1[Troop.tank] += 1
        a1[Troop.fighter] += 1
        a1[Troop.cruiser] += 1
        a1[Troop.battleship] += 1
        a2 = Army(Power.G)
        a2[Troop.inf] += 20
        a2[Troop.art] += 1
        a2[Troop.aa] += 1
        win_chance, tie_chance, loss_chance, avg_attack_loss, avg_defense_loss = battle(a1, a2)
        accuracy_decimal = 2

        self.assertAlmostEqual(win_chance, 0.303, places=accuracy_decimal)
        self.assertAlmostEqual(loss_chance, 0.670, places=accuracy_decimal)
        self.assertAlmostEqual(tie_chance, 1 - win_chance - loss_chance, places=accuracy_decimal)
        self.assertAlmostEqual(avg_attack_loss, 23.1, places=0)
        self.assertAlmostEqual(avg_defense_loss, 16.2, places=0)

class Bulk(unittest.TestCase):

    @unittest.skip("debug skipping")
    def test_inf_large(self):
        a1 = Army(Power.J)
        a1[Troop.inf] += 100
        a2 = Army(Power.UK)
        a2[Troop.inf] += 65
        win_chance, tie_chance, loss_chance, avg_attack_loss, avg_defense_loss = battle(a1, a2)
        accuracy_decimal = 2

        self.assertAlmostEqual(win_chance, 0.860, places=accuracy_decimal)
        self.assertAlmostEqual(loss_chance, 0.140, places=accuracy_decimal)
        self.assertAlmostEqual(tie_chance, 1 - win_chance - loss_chance, places=accuracy_decimal)
        self.assertAlmostEqual(avg_attack_loss, 212.1, places=0)
        self.assertAlmostEqual(avg_defense_loss, 189.3, places=0)

    def test_everything_large(self):
        a1 = Army(Power.US)
        a1[Troop.inf] += 10
        a1[Troop.art] += 7
        a1[Troop.tank] += 3
        a1[Troop.fighter] += 4
        a1[Troop.bomber] += 1
        a1[Troop.cruiser] += 2
        a1[Troop.battleship] += 1
        a2 = Army(Power.G)
        a2[Troop.inf] += 18
        a2[Troop.art] += 2
        a2[Troop.fighter] += 3
        a2[Troop.bomber] += 1
        a2[Troop.aa] += 1
        win_chance, tie_chance, loss_chance, avg_attack_loss, avg_defense_loss = battle(a1, a2)
        accuracy_decimal = 2

        self.assertAlmostEqual(win_chance, 0.686, places=accuracy_decimal)
        self.assertAlmostEqual(loss_chance, 0.304, places=accuracy_decimal)
        self.assertAlmostEqual(tie_chance, 1 - win_chance - loss_chance, places=accuracy_decimal)
        self.assertAlmostEqual(avg_attack_loss, 87.3, places=0)
        self.assertAlmostEqual(avg_defense_loss, 96, places=0)


if __name__ == '__main__':
    unittest.main()