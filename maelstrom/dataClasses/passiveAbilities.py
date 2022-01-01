"""
Passive abilities are attributes a character can have that trigger when a
condition is met, such as when a character is hit or reaches a certain threshold
of health
"""



from characters.stat_classes import Boost
from util.serialize import AbstractJsonSerialable
from util.utilities import ELEMENTS, roll_perc
from battle.events import HIT_GIVEN_EVENT, HIT_TAKEN_EVENT, UPDATE_EVENT
from abc import abstractmethod



class AbstractPassive(AbstractJsonSerialable):
    def __init__(self, name, description):
        """
        name should be a unique identifier
        """
        super().__init__(type="Passive")
        self.name = name
        self.description = description

    @abstractmethod
    def copy(self):
        pass

    @abstractmethod
    def registerTo(self, user):
        """
        This method should add listeners to the given user and reset this
        object's internal state
        """
        pass

    def toJson(self): # override default method
        return self.name


class ThresholdPassive(AbstractPassive):
    def __init__(self, name, boost, threshold):
        """
        threshold must be a decimal number
        """
        super().__init__(
            name,
            f'{name}: Inflicts user with {boost.getDisplayData()} when at or below {int(threshold * 100)}% HP'
        )
        self.boost = boost.copy()
        self.threshold = threshold

    def copy(self):
        return ThresholdPassive(self.name, self.boost, self.threshold)

    def registerTo(self, user):
        user.addActionListener(UPDATE_EVENT, self.checkTrigger)

    def checkTrigger(self, updated):
        if updated.getHpPerc() <= self.threshold * 100:
            updated.boost(self.boost.copy())

class OnHitGivenPassive(AbstractPassive):
    def __init__(self, name, boost, chance, targetsUser):
        """
        chance should be a decimal number
        """
        super().__init__(
            name,
            f'{name}: your hits have a {int(chance * 100)}% chance to inflict {"you" if targetsUser else "the target"} with {boost.getDisplayData()}'
        )
        self.boost = boost.copy()
        self.chance = chance
        self.targetsUser = targetsUser

    def copy(self):
        return OnHitGivenPassive(self.name, self.boost, self.chance, self.targetsUser)

    def registerTo(self, user):
        user.addActionListener(HIT_GIVEN_EVENT, self.checkTrigger)

    def checkTrigger(self, onHitEvent):
        if roll_perc(onHitEvent.hitter.getStatValue("luck")) > 100 - self.chance * 100:
            if self.targetsUser:
                onHitEvent.hitter.boost(self.boost.copy())
            else:
                onHitEvent.hitee.boost(self.boost.copy())

class OnHitTakenPassive(AbstractPassive):
    def __init__(self, name, boost, chance, targetsUser):
        """
        chance should be a decimal number
        """
        super().__init__(
            name,
            f'{name}: hits against you have a {int(chance * 100)}% chance to inflict {"you" if targetsUser else "the attacker"} with {boost.getDisplayData()}'
        )
        self.boost = boost.copy()
        self.chance = chance
        self.targetsUser = targetsUser

    def copy(self):
        return OnHitTakenPassive(self.name, self.boost, self.chance, self.targetsUser)

    def registerTo(self, user):
        user.addActionListener(HIT_TAKEN_EVENT, self.checkTrigger)

    def checkTrigger(self, onHitEvent):
        if roll_perc(onHitEvent.hitee.getStatValue("luck")) > 100 - self.chance * 100:
            if self.targetsUser:
                onHitEvent.hitee.boost(self.boost.copy())
            else:
                onHitEvent.hitter.boost(self.boost.copy())



def getPassiveAbilityList():
    return [
        ThresholdPassive("Threshhold test", Boost("resistance", 0.5, 1, "Threshhold test"), 0.25),
        OnHitGivenPassive("On Hit Given Test", Boost("luck", 0.25, 3, "On Hit Given Test"), 0.25, True),
        OnHitTakenPassive("On Hit Taken Test", Boost("control", -0.25, 3, "On Hit Taken Test"), 0.25, False)
    ]
