from shared.state import GameState, GamePhase, EquipmentSlot, ActionSlot, UnitState
from world.action_resolver import Resolver

def sampleEquipment():
    equipmentDefinitions = {
        "short_sword": {
            "equipment_id":"short_sword", 
            "display_name":"Short Sword", 
            "slot":EquipmentSlot.MAINHAND, 
            "point_cost":0, 
            "stat_modifiers":[], 
            "granted_action_ids":["basicAttack"]},
        "old_boots":{
            "equipment_id":"old_boots", 
            "display_name":"Nasty Old Boots", 
            "slot":EquipmentSlot.BOOTS, 
            "point_cost":0, 
            "stat_modifiers":[], 
            "granted_action_ids":["run"]},
        "amulet_of_dodging_everything" : {
            "equipment_id":"amulet_of_dodging_everything", 
            "display_name":"Amulet of Dodging Everything", 
            "slot":EquipmentSlot.ACCESSORY, 
            "point_cost":0, 
            "stat_modifiers":[{"stat":"evasion", "value":100}], 
            "granted_action_ids":[]}
            }
    return equipmentDefinitions

def sampleAbility():
    return {
        "basicAttack":{
            "action_id":"basicAttack",
            "display_name":"Sword Swing",
            "action_slot": ActionSlot.MAIN,
            "range_min": 1,
            "range_max":1,
            "tohit_bonus": 100,
            "effects": [
                {
                "effect_type": "damage",
                "quality_bonus": 0,
                "damage_roll": '2d1'
                },
            ]
        },
        "killAnything":{
            "action_id":"killAnything",
            "display_name":"Kill Anything",
            "action_slot": ActionSlot.MAIN,
            "range_min": 1,
            "range_max":1,
            "tohit_bonus": 100,
            "effects": [
                {
                "effect_type": "damage",
                "quality_bonus": 0,
                "damage_roll": '2000d1'
                },
            ]
        },
        "run":{
            "action_id":"run",
            "display_name":"Run",
            "action_slot": ActionSlot.MOVE,
            "range_min": 1,
            "range_max":6,
            "effects": [
                {
                "effect_type": "move",
                },
            ]
        },
        "heal":{
            "action_id":"heal",
            "display_name":"Heal",
            "action_slot": ActionSlot.MAIN,
            "range_min": 0,
            "range_max":3,
            "effects": [
                {
                "effect_type": "heal",
                "amount": 2
                },
            ]
        },
        "poison_dart":{
            "action_id":"poison_dart",
            "display_name":"Poison Dart",
            "action_slot": ActionSlot.MAIN,
            "range_min": 1,
            "range_max":3,
            "effects": [
                {
                "effect_type": "apply_status",
                "status_id": "poisoned",
                "duration": 2
                },
            ]
        }
    }


def sampleResolver():
    equipmentDefinitions = sampleEquipment()
    abilityDefinitions = sampleAbility()
    return Resolver(equipmentDefinitions, abilityDefinitions)

def sampleGamestate():
    unit1 = UnitState(
        unit_id="A",
        owner="player1",
        position={"x": 1, "y": 2},
        wounds=0,
        statuses=[],
        equipment={EquipmentSlot.MAINHAND:"short_sword", EquipmentSlot.BOOTS:"old_boots"}
        )
    
    unit2 = UnitState(
        unit_id="B",
        owner="player2",
        position={"x": 2, "y": 2},
        wounds=0,
        statuses=[],
        equipment={EquipmentSlot.MAINHAND:"short_sword", EquipmentSlot.BOOTS:"old_boots"}
        )

    return GameState(
        match_id="sampleMatch",
        map_id="sampleMap",
        player1_id="p1",
        player2_id="p2",
        active_player="player2",
        phase=GamePhase.SELECTING_UNIT,
        units={"A":unit1, "B":unit2},
        round_number=1,
        activated_unit_ids=["A"],
        available_action_slots=[ActionSlot.MAIN, ActionSlot.BONUS, ActionSlot.MOVE],
        winner=None
        )