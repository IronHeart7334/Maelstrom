"""
This module handles creating the default instances for character-related classes.
This helps circumvent several circular-dependency issues, and abstractifies the
object creation process a bit.
"""



from battle.area import Area, Location
from battle.battle import Battle
from characters.actives.actives import AbstractActive, MeleeAttack
from characters.character import EnemyCharacter, PlayerCharacter
from characters.characterLoader import EnemyLoader
from characters.item import Item
from characters.passives import Threshhold, OnHitGiven, OnHitTaken
import random



NEXT_ITEM_NUM = 1 # I don't like globals, but need this for now



def saveDefaultData():
    """
    Creates all the default
    enemies in the enemy directory
    """
    enemyLoader = EnemyLoader()
    for enemy in createDefaultEnemies():
        enemyLoader.save(enemy)

def createDefaultArea()->"Area":
    return Area(
        name="Test Area",
        desc="No description",
        locations=[createDefaultLocation()],
        levels=[createRandomBattle()]
    )

def createRandomBattle()->"Battle":
    enemyNames = []
    numEnemies = random.randint(1, 4)
    allEnemyNames = EnemyLoader().getOptions()

    for i in range(numEnemies):
        enemyNames.append(random.choice(allEnemyNames))

    return Battle(
        name="Random encounter",
        desc="Random battle",
        enemyNames=enemyNames,
        level=1,
        rewards=[createRandomItem()]
    )

def createDefaultLocation():
    return Location(
        name="Shoreline",
        desc="Gentle waves lap at the shore.",
        script=[
            "I'm not sure how I feel about the sand...",
            "is it course and rough?",
            "or soft?"
        ]
    )

def createDefaultPlayer(name, element)->"PlayerCharacter":
    return PlayerCharacter(
        name=name,
        element=element,
        actives=createDefaultActives(element),
        passives=createDefaultPassives()
    )

def createDefaultActives(element: str)->"List<AbstractActive>":
    bolt = AbstractActive(
        name=element+" bolt",
        stats={
            "cleave":-5,
            "crit chance":-2,
            "damage multiplier":7
        }
    )

    slash = MeleeAttack(name="Slash")
    jab = MeleeAttack(
        name="Jab",
        stats={
            "miss chance":-5,
            "crit chance":5,
            "miss mult":-5,
            "crit mult":5
        }
    )
    slam = MeleeAttack(
        name="Slam",
        stats={
            "damage multiplier":5,
            "miss chance":-5
        }
    )

    return [bolt, slash, jab, slam]

def createDefaultPassives()->"List<AbstractPassive>":
    p = Threshhold(
        name="Threshhold test",
        boostedStat="resistance",
    )

    o = OnHitGiven(
        name="On Hit Given Test",
        boostedStat="luck",
    )

    h = OnHitTaken(
        name="On Hit Taken Test",
        boostedStat="control",
        targetsUser=False
    )

    return [p, o, h]

def createRandomItem()->"Item":
    global NEXT_ITEM_NUM
    name = f'Random Item #{NEXT_ITEM_NUM}'
    NEXT_ITEM_NUM += 1
    return Item(name=name)

def createDefaultEnemies():
    enemies = []

    enemies.append(EnemyCharacter(
        name="Lightning Entity",
        element="lightning",
        stats={
            "energy" : 10,
            "resistance" : -10
        },
        actives=createDefaultActives("lightning"),
        passives=createDefaultPassives() # each needs their own copy
    ))

    enemies.append(EnemyCharacter(
        name="Rain Entity",
        element="rain",
        stats={
            "potency" : 10,
            "control" : -10
        },
        actives=createDefaultActives("rain"),
        passives=createDefaultPassives()
    ))

    enemies.append(EnemyCharacter(
        name="Hail Entity",
        element = "hail",
        stats={
            "resistance" : 10,
            "luck" : -10
        },
        actives=createDefaultActives("hail"),
        passives=createDefaultPassives()
    ))

    enemies.append(EnemyCharacter(
        name="Wind Entity",
        element = "wind",
        stats={
            "luck" : 10,
            "potency" : -10
        },
        actives=createDefaultActives("wind"),
        passives=createDefaultPassives()
    ))

    enemies.append(EnemyCharacter(
        name="Stone Soldier",
        element="stone",
        stats={
            "control":5,
            "resistance":10,
            "luck":-5,
            "energy":-5,
            "potency":-5
        },
        actives=createDefaultActives("stone"),
        passives=createDefaultPassives()
    ))

    return enemies