from utilities import *
from stat_classes import *


from upgradable import AbstractUpgradable
from output import Op
# TODO: add ability to customize side effects


class AbstractActive(AbstractUpgradable):
    """
    The attacks all characters can use
    """

    #these are the formulae used by stat calculations
    def mult_f(base: int) -> float:
        """
        The formula used to calculate damage multipliers

        Min : 0  : 1.0
        Mid : 10 : 1.25
        Max : 20 : 1.5

        will balance later
        """
        return 1.0 + base * 0.025


    def dmg_weight(base: int) -> float:
        """
        The formula for damage weight

        Damage weight is how much of the attack's total damage will be devoted to
        a specific element.
        For example,
        by default, the weights are 10 for each element, so the total damage would be evenly divided.
        But, if their were 4 elements, weighted at 10, 10, 10, and 20; 20% of the total damage would go to each of the first 3,
        and the remaining 40% would go to the last
        """
        return base #very simple


    def cleave_form(base: int) -> float:
        """
        The formula used to calculate "cleave damage":
        whenever you attack an enemy, the attack will
        deal some percentage of that damage to each other
        enemy.

        Note that this does not decrease the damage of the initial hit
        """
        return base * 0.05


    def crit_form(base: int) -> float:
        """
        Used to calculate the chance of a critical hit based on the given base
        """
        return 2 * base


    def miss_form(base: int) -> float:
        """
        Used to calculate the chance of a miss based on the given base
        """
        return 40 - 2 * base


    def crit_mult_form(base: int) -> float:
        """
        Used to calculate the multiplier for critical hits
        """
        return 1.0 + 0.05 * base


    def miss_mult_form(base: int) -> float:
        """
        Used to calculate the multiplier for misses
        """
        return 0.5 + 0.025 * base


    # will make this able to generate from JSON soon
    def __init__(self, name: str, mult: int, energy_cost: int):
        """
        """
        super(AbstractActive, self).__init__(name)
        self.set_type("Active")
        self.add_attr("damage multiplier", Stat("damage multiplier", AbstractActive.mult_f, mult))

        for element in ELEMENTS:
            self.add_attr(element + " damage weight", Stat(element + " damage weight", AbstractActive.dmg_weight, 10))

        self.add_attr("cleave", Stat("cleave", AbstractActive.cleave_form, 0)) #default to no cleave

        self.add_attr("miss chance", Stat("miss chance", AbstractActive.miss_form, 10))
        self.add_attr("crit chance", Stat("crit chance", AbstractActive.crit_form, 10))
        self.add_attr("miss mult", Stat("miss mult", AbstractActive.miss_mult_form, 10))
        self.add_attr("crit mult", Stat("crit mult", AbstractActive.crit_mult_form, 10))
        self.energy_cost = energy_cost

        self.side_effects = []
        self.damages = {}

    def set_damage_distributions(self, new_dists: dict):
        """
        new_dist should be a dict
        """
        for k, v in new_dists.items():
            self.set_base(k, v)

    def add_side_effect(self, boost, chance = 100):
        """
        Add a boost to inflict upon hitting
        """
        self.side_effects.append({"effect": boost, "chance":chance})

    def set_cleave(self, base: int):
        """
        Sets the cleave base for this
        """
        self.set_base("cleave", base)

    def set_user(self, user):
        super(AbstractActive, self).set_user(user)
        self.distribute_damage()

    def init_for_battle(self):
        self.calc_all()
        self.distribute_damage()
        for side_effect in self.side_effects:
            side_effect["effect"].reset()

    def customize(self):
        """
        Start by showing what the attack's
        stats are
        """
        self.init_for_battle()
        self.display_data()
        """
        choice = choose("Do you want to change these damage stats, add a side effect, or change an existing one?", ("stats", "add effect", "change effect"))
        if choice == "stat":
            self.customize_damages()
        elif choice == "add effect":
            self.choose_effect_to_add()
        """
        self.customize_damages()
        # and display again
        self.init_for_battle()
        self.display_data()

    def customize_damages(self):
        # copy the old attack data into new data
        new_data = {}
        for k, v in self.damage_distribution.items():
            new_data[k] = v

        can_down = []
        # make sure it would not be decreased past 0
        #(base 12.5 system, can't be between 0 and 12.5)
        for k, v in self.damage_distribution.items():
            if v > 0:
                can_down.append(k)

        new_data[choose("Which damage stat do you want to increase by 12.5% of total damage?", list(new_data.keys()))] += 12.5
        new_data[choose("Which damage stat do you want to decrease by 12.5%? of total damage", can_down)] -= 12.5
        self.set_damage_distributions(new_data)

    def distribute_damage(self):
        self.calc_all()
        total = get_hit_perc(self.user.level) * self.get_stat("damage multiplier")
        split_between = 0
        self.damages = {}
        for element in ELEMENTS:
            split_between += self.get_stat(element + " damage weight")
        for element in ELEMENTS:
            self.damages[element] = total / split_between * self.get_stat(element + " damage weight")

    def total_dmg(self):
        ret = 0
        for damage in self.damages.values():
            ret += damage
        return ret

    def display_data(self):
        self.init_for_battle()
        Op.add(self.name)
        Op.indent()
        for type, value in self.damages.items():
            Op.add(type + " damage: " + str(int(value)))
        Op.unindent()
        Op.add("Critical hit chance: " + str(self.crit) + "%")
        Op.add("Miss chance: " + str(self.miss) + "%")
        Op.add("Critical hit multiplier: " + str(int(self.crit_mult * 100)) + "%")
        Op.add("Miss multiplier: " + str(int(self.miss_mult * 100)) + "%")
        Op.add("Cleave damage: " + str(int(self.cleave * 100)) + "% of damage from initial hit")
        #Op.add("SIDE EFFECTS:")
        Op.indent()
        for side_effect in self.side_effects:
            Op.add(str(side_effect["chance"]) + "% chance to inflict")
            side_effect["effect"].display_data()
        Op.display()

    def can_use(self):
        return self.user.energy >= self.energy_cost

    def calc_MHC(self):
        """
        Used to calculate hit type
        """
        ret = 1.0

        rand = roll_perc(self.user.get_stat("luck"))
        Dp.add(["rand in calc_MHC: " + str(rand), "Crit: " + str(100 - self.get_stat("crit chance")), "Miss: " + str(self.get_stat("miss chance"))])
        Dp.dp()
        if rand <= self.get_stat("miss chance"):
            Op.add("A glancing blow!")
            ret = self.get_stat("miss mult")

        elif rand >= 100 - self.get_stat("crit chance"):
            Op.add("A critical hit!")
            ret = self.get_stat("crit mult")
        Op.display()

        return ret

    def apply_side_effects_to(self, target):
        for side_effect in self.side_effects:
            rand = roll_perc(self.user.get_stat("luck"))

            Dp.add("Rolling for side effect...")
            Dp.add("Rolled: " + str(rand))
            Dp.add("Minimum to activate: " + str(side_effect["chance"]))
            Dp.dp()

            if rand > 100 - side_effect["chance"]:
                side_effect["effect"]()

    def use(self):
        self.user.lose_energy(self.energy_cost)
        if self.get_stat("damage multiplier") is not 0:
            self.user.team.enemy.active.take_DMG(self.user, self)
            self.apply_side_effects_to(self.user.team.enemy.active)
        if self.get_stat("cleave") is not 0.0:
            for enemy in self.user.team.enemy.members_rem:
                if enemy is not self.user.team.enemy.active:
                    enemy.direct_dmg(self.total_dmg() * self.get_stat("cleave"))
                    self.apply_side_effects_to(enemy)

    def generate_save_code(self):
        ret = ["<ACTIVE>: " + self.name]
        ret.append("*" + str(self.get_stat("damage multiplier")))
        ret.append(str(self.cleave) + "%")
        for k, v in self.damage_distribution.items():
            ret.append(k + ": " + str(v))
        ret.append("m%: " + str(self.miss))
        ret.append("c%: " + str(self.crit))
        ret.append("m*: " + str(self.miss_mult))
        ret.append("c*: " + str(self.crit_mult))
        ret.append("ENE: " + str(self.energy_cost))
        for status in self.side_effects:
            ret.append(status["effect"].generate_save_code() + ": " + str(status["chance"]) + "%")
        return ret

    @staticmethod
    def read_save_code(code):
        ret = None

        # start with the name
        name = ignore_text(code[0], "<ACTIVE>:").strip()
        dmg_mult = float(ignore_text(code[1], "*"))
        cleave = int(float(ignore_text(code[2], "%")) * 100)
        # * 100 is to counteract initializer
        new_dist = dict()
        for i in range(3, 8):
            line = code[i].split(":")
            new_dist[line[0].strip()] = int(float(line[1]))
        miss_c = int(float(ignore_text(code[8], "m%:")))
        crit_c = int(float(ignore_text(code[9], "c%:")))
        miss_m = float(ignore_text(code[10], "m*:"))
        crit_m = float(ignore_text(code[11], "c*:"))
        cost = int(float(ignore_text(code[12], "ENE: ")))

        #boosts...
        boosts = dict()
        boost_codes = code[13:]

        for boost_code in boost_codes:
            line = boost_code.split(":")
            boosts[Boost.read_save_code(line[0])] = int(float(ignore_text(line[1], "%")))

        if crit_c is not 0:
            ret = MeleeAttack(name, dmg_mult, miss_c, crit_c, miss_m, crit_m, cleave)

        else:
            ret = AbstractActive(name, dmg_mult, cleave, cost)

        ret.set_damage_distributions(new_dist)
        for boost, chance in boosts.items():
            ret.add_side_effect(boost, chance)

        return ret


    @staticmethod
    def get_defaults() -> list:
        """
        Returns the default attacks that every character can use
        """
        slash = MeleeAttack("Slash", 10, 10, 10, 10, 10)
        slash.set_cleave(10)

        jab = MeleeAttack("Jab", 5, 5, 15, 5, 15)
        slam = MeleeAttack("Slam", 15, 15, 5, 5, 5)

        return [slash, jab, slam]


class MeleeAttack(AbstractActive):
    def __init__(self, name, dmg, miss, crit, miss_mult, crit_mult):
        super(MeleeAttack, self).__init__(name, dmg, 0)
        self.set_base("miss chance", miss)
        self.set_base("crit chance", crit)
        self.set_base("miss mult", miss_mult)
        self.set_base("crit mult", crit_mult)
