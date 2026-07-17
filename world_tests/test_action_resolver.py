import pytest
from typing import Literal
from pydantic import ValidationError

from shared.info_exchange import ActionHandler, SubmittedAction
from shared.state import Coord, GamePhase, GameState, UnitState, EquipmentSlot, ActionSlot, PlayerSlot
from world.action_resolver import Resolver

@pytest.fixture
def sampleResolver():
    equipmentDefinitions = {
        "short_sword": {
            "equipment_id":"short_sword", 
            "display_name":"Short Sword", 
            "slot":EquipmentSlot.MAINHAND, 
            "point_cost":0, 
            "stat_modifiers":[], 
            "granted_actions":["basicAttack"]},
        "amulet_of_dodging_everything" : {
            "equipment_id":"amulet_of_dodging_everything", 
            "display_name":"Amulet of Dodging Everything", 
            "slot":EquipmentSlot.ACCESSORY, 
            "point_cost":0, 
            "stat_modifiers":[{"stat":"evasion", "value":100}], 
            "granted_actions":[]}
            }
    abilityDefinitions = {
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
    return Resolver(equipmentDefinitions, abilityDefinitions)

@pytest.fixture
def sampleGamestate():
    unit1 = UnitState(
        unit_id="generico",
        owner="player1",
        position={"x": 1, "y": 2},
        wounds=0,
        statuses=[],
        equipment={EquipmentSlot.MAINHAND:"short_sword"}
        )
    
    unit2 = UnitState(
        unit_id="genericum",
        owner="player2",
        position={"x": 2, "y": 2},
        wounds=0,
        statuses=[],
        equipment={EquipmentSlot.MAINHAND:"short_sword"}
        )

    return GameState(
        match_id="sampleMatch",
        map_id="sampleMap",
        player1_id="p1",
        player2_id="p2",
        active_player="player2",
        phase=GamePhase.SELECTING_UNIT,
        units={"generico":unit1, "genericum":unit2},
        round_number=1,
        activated_unit_ids=["generico"],
        available_action_slots=[ActionSlot.MAIN, ActionSlot.BONUS, ActionSlot.MOVE],
        winner=None
        )

def test_verify_action(sampleResolver, sampleGamestate):
    ## Test a valid action
    action = SubmittedAction(
        player_id="p2",
        unit_id="genericum",
        action_id="basicAttack",
        handler=ActionHandler.Ability,
        target="generico"
    )
    result, _ = sampleResolver.verify_action(sampleGamestate, action)
    assert result == True

    ## Test an invalid action due to wrong player
    action = SubmittedAction(
        player_id="p3",
        unit_id="genericum",
        action_id="basicAttack",
        handler=ActionHandler.Ability,
        target="generico"
    )
    result, _ = sampleResolver.verify_action(sampleGamestate, action)
    assert result == False

    ## Test an invalid action due to wrong unit
    action = SubmittedAction(
        player_id="p2",
        unit_id="genericles",
        action_id="basicAttack",
        handler=ActionHandler.Ability,
        target="generico"
    )
    result, _ = sampleResolver.verify_action(sampleGamestate, action)
    assert result == False

    sampleGamestate.available_action_slots.remove(ActionSlot.MAIN)

    ## Test an invalid action due to unavailable action slot
    action = SubmittedAction(
        player_id="p2",
        unit_id="genericum",
        action_id="basicAttack",
        handler=ActionHandler.Ability,
        target="generico"
    )
    result, _ = sampleResolver.verify_action(sampleGamestate, action)
    assert result == False

    sampleGamestate.available_action_slots.append(ActionSlot.MAIN)

    ## Test an invalid action due to wrong game phase
    action = SubmittedAction(
        player_id="p2",
        unit_id="genericum",
        action_id="basicAttack",
        handler=ActionHandler.DeployUnit,
        target="generico"
    )
    result, msg = sampleResolver.verify_action(sampleGamestate, action)
    print(msg)
    assert result == False

    ## Test an invalid action due to unrecognized action_id
    action = SubmittedAction(
        player_id="p2",
        unit_id="genericum",
        action_id="nonexistentAction",
        handler=ActionHandler.Ability,
        target="generico"
    )
    result, _ = sampleResolver.verify_action(sampleGamestate, action)
    assert result == False

def testHandleMoveEffect(sampleResolver, sampleGamestate):
    action = SubmittedAction(
        player_id="p2",
        unit_id="genericum",
        action_id="run",
        handler=ActionHandler.Ability,
        target={"x": 3, "y": 4}
        )
    events = []
    sampleResolver.handleMoveEffect(sampleGamestate, action, events)
    assert len(events) == 1
    assert events[0]["event_type"] == "unit_moved"
    assert events[0]["unit_id"] == "genericum"
    assert events[0]["start"] == Coord(x=2, y=2)
    assert events[0]["end"] == Coord(x=3, y=4)
    assert sampleGamestate.units["genericum"].position == Coord(x=3, y=4)

def testHandleDamageEffect(sampleResolver, sampleGamestate):
    ## Test the handleDamageEffect method
    ## NOT the full combat loop, Ari.
    action = SubmittedAction(
        player_id="p2",
        unit_id="genericum",
        action_id="basicAttack",
        handler=ActionHandler.Ability,
        target="generico"
        )
    effect = sampleResolver.abilityDefinitions.get("basicAttack").effects[0]
    print(f"Effect type: {type(effect)}")
    event_list = []
    sampleResolver.handleDamageEffect(sampleGamestate, action, effect, event_list)
    assert len(event_list) == 1
    assert event_list[0]["event_type"] == "unit_damaged"
    assert event_list[0]["unit_id"] == "generico"
    assert event_list[0]["amount"] == 2
    assert event_list[0]["new_wounds"] == 2

def testHandleKillEffect(sampleResolver, sampleGamestate):
    ## Test the handleDamageEffect method with a kill guaranteed
    ## NOT the full combat loop, Ari.
    action = SubmittedAction(
        player_id="p2",
        unit_id="genericum",
        action_id="killAnything",
        handler=ActionHandler.Ability,
        target="generico"
        )
    effect = sampleResolver.abilityDefinitions.get("killAnything").effects[0]
    print(f"Effect type: {type(effect)}")
    event_list = []
    sampleResolver.handleDamageEffect(sampleGamestate, action, effect, event_list)
    assert len(event_list) == 2
    assert event_list[0]["event_type"] == "unit_damaged"
    assert event_list[0]["unit_id"] == "generico"
    assert event_list[0]["amount"] == 2000
    assert event_list[0]["new_wounds"] == 2000
    assert event_list[1]["event_type"] == "unit_killed"
    assert event_list[1]["unit_id"] == "generico"

def testHandleHealEffect(sampleResolver, sampleGamestate):
    ## Test the handleHealEffect method
    action = SubmittedAction(
        player_id="p2",
        unit_id="genericum",
        action_id="heal",
        handler=ActionHandler.Ability,
        target="generico"
        )
    effect = sampleResolver.abilityDefinitions.get("heal").effects[0]
    event_list = []
    sampleGamestate.units["generico"].wounds = 5
    sampleResolver.handleHealEffect(sampleGamestate, action, effect, event_list)
    assert len(event_list) == 1
    assert event_list[0]["event_type"] == "unit_healed"
    assert event_list[0]["unit_id"] == "generico"
    assert event_list[0]["amount"] == 2
    assert event_list[0]["new_wounds"] == 3

def testHandleApplyStatusEffect(sampleResolver, sampleGamestate):
    ## Test the handleApplyStatusEffect method
    action = SubmittedAction(
        player_id="p2",
        unit_id="genericum",
        action_id="poison_dart",
        handler=ActionHandler.Ability,
        target="generico"
        )
    effect = sampleResolver.abilityDefinitions.get("poison_dart").effects[0]
    event_list = []
    sampleResolver.handleApplyStatusEffect(sampleGamestate, action, effect, event_list)
    assert len(event_list) == 1
    assert "poisoned" in sampleGamestate.units["generico"].statuses
    assert event_list[0]["event_type"] == "status_applied"
    assert event_list[0]["unit_id"] == "generico"
    assert event_list[0]["status_id"] == "poisoned"

def testResolverBasicFunctions(sampleResolver, sampleGamestate):
    ## Just a quick smoke-test. Individual effect handlers are tested in their own functions above.
    ## I just want to make sure the resolver can run through an assortmment of full action resolutions without throwing exceptions.
    for action_id in ["basicAttack", "heal", "poison_dart", "run"]:
        action = SubmittedAction(
            player_id="p2",
            unit_id="genericum",
            action_id=action_id,
            handler=ActionHandler.Ability,
            target="generico" if action_id != "run" else {"x": 3, "y": 4}
            )
        newState, events = sampleResolver.resolve_action(sampleGamestate, action)
        assert isinstance(newState, GameState)
        assert isinstance(events, list)

def testComputeStat(sampleResolver, sampleGamestate):
    ## Test the computeStat method
    unit = sampleGamestate.units["genericum"]
    # The unit has no equipment that modifies stats, so the base value should be returned.
    assert sampleResolver.compute_stat(sampleGamestate, unit.unit_id, "evasion") == 0
    # Equip the unit with an accessory that modifies evasion.
    unit.equipment[EquipmentSlot.ACCESSORY] = "amulet_of_dodging_everything"
    assert sampleResolver.compute_stat(sampleGamestate, unit.unit_id, "evasion") == 100

def test_turn_advancer(sampleResolver, sampleGamestate):
    ##Should not change anything, since there are still actions to be taken
    assert sampleResolver.advance_turn(sampleGamestate) == []
    sampleGamestate.available_action_slots = []
    assert len(sampleResolver.advance_turn(sampleGamestate)) == 1
    assert sampleGamestate.active_player == "player1"
    assert len(sampleGamestate.available_action_slots) == 3