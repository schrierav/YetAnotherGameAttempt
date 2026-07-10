import copy
from random import randint
from shared.state import ApplyStatusEffect, Coord, DamageEffect, GameState, ActionSlot, GamePhase, AbilityDefinition, HealEffect, PullEffect, EquipmentDefinition
from shared.info_exchange import SubmittedAction, ActionHandler
from shared.const import HITPOINTLIMIT, DEFAULTDAMAGE, TOHIT

def rollDice(dice_str: str) -> int:
    """
    Rolls dice based on a string like '2d6+3' and returns the total.
    """
    import re
    import random

    match = re.match(r'(\d+)d(\d+)([+-]\d+)?', dice_str)
    if not match:
        raise ValueError(f"Invalid dice string: {dice_str}")

    num_dice = int(match.group(1))
    die_size = int(match.group(2))
    modifier = int(match.group(3)) if match.group(3) else 0

    total = sum(random.randint(1, die_size) for _ in range(num_dice)) + modifier
    return total

class Resolver():
    """
    Varifies actions. Holds a stock of everything possible and ensures that whatever is being submitted makes sense.
    """
    def __init__(self, equipmentDefinitions:dict, abilityDefinitions:dict):
        self.equipmentDefinitions = {}
        self.abilityDefinitions = {}
        for ability_id, ability in abilityDefinitions.items():
            self.abilityDefinitions[ability_id] = AbilityDefinition(**ability)
        for equipment_id, equipment in equipmentDefinitions.items():
            self.equipmentDefinitions[equipment_id] = EquipmentDefinition(**equipment)

        self.maps = {}

    def compute_stat(self, state:GameState, unit_id:str, stat:str):
        """
        Computes a stat for a unit, taking into account equipment and other modifiers.
        """
        default_stat = 0
        unit = state.units[unit_id]
        for equipment_id in unit.equipment.values():
            equipment = self.equipmentDefinitions[equipment_id]
            for modifier in equipment.stat_modifiers:
                if modifier.stat == stat:
                    default_stat += modifier.value
        return default_stat

    def verify_action(self, state:GameState, action:SubmittedAction)->bool:
        """
        Makes sure that an action is kosher before applying it
        """
        chosenAction = self.abilityDefinitions.get(action.action_id, None)
        if not chosenAction:
            return False, "Action not found"
        if not((state.active_player == "player1" and state.player1_id == action.player_id) 
               or (state.active_player == "player2" and state.player2_id == action.player_id)):
            return False, "Player is not the active player"
        if ((state.phase == GamePhase.DEPLOYMENT and action.handler != ActionHandler.DeployUnit) or 
            (state.phase != GamePhase.DEPLOYMENT and action.handler == ActionHandler.DeployUnit)):
            return False, "Invalid action for current game phase"
        if action.unit_id not in state.units or action.unit_id in state.activated_unit_ids:
            return False, "Invalid unit"
        if not((chosenAction.action_slot == ActionSlot.FREE) or (chosenAction.action_slot in state.available_action_slots)):
            return False, "Action slot not available"
        if type(action.target) == str:
            if action.target not in state.units:
                return False, "Target unit not found"
            coords = state.units[action.target].position
        else:
            coords = action.target
            manhattan = abs(coords.x - state.units[action.unit_id].position.x) + abs(coords.y - state.units[action.unit_id].position.y)
            if manhattan < chosenAction.range_min or manhattan > chosenAction.range_max:
                return False, "Target out of range"
        return True, "Action is valid"
    
    def handleMoveEffect(self, state:GameState, action:SubmittedAction, events:list)->None:
        unit = state.units.get(action.unit_id)
        start = unit.position
        end = action.target
        unit.position = end
        events.append({
            "event_type": "unit_moved",
            "unit_id": unit.unit_id,
            "start": start,
            "end": end,
            "path": [start, end]
        })
    def handleHealEffect(self, state:GameState, action:SubmittedAction, effect:HealEffect, events:list)->None:
        unit = state.units[action.target]
        unit.wounds -= effect.amount
        if unit.wounds < 0:
            unit.wounds = 0
        events.append({
            "event_type": "unit_healed",
            "unit_id": unit.unit_id,
            "amount": effect.amount,
            "new_wounds": unit.wounds
        })
    def handleDamageEffect(self, state:GameState, action:SubmittedAction, effect:DamageEffect, events:list)->None:
        unit = state.units[action.target]
        total = rollDice(effect.damage_roll) + effect.quality_bonus
        unit.wounds += total
        events.append({
            "event_type": "unit_damaged",
            "unit_id": unit.unit_id,
            "amount": total,
            "new_wounds": unit.wounds
        })
        if unit.wounds >= HITPOINTLIMIT:
            events.append({
                "event_type": "unit_killed",
                "unit_id": unit.unit_id
            })
    def handlePullEffect(self, state:GameState, action:SubmittedAction, effect:PullEffect, events:list)->None:
        unit = state.units[action.target]
        start = unit.position
        end = effect.destination
        unit.position = end
        events.append({
            "event_type": "unit_moved",
            "unit_id": unit.unit_id,
            "start": start,
            "end": end,
            "path": [start, end]
        })
    def handleApplyStatusEffect(self, state:GameState, action:SubmittedAction, effect:ApplyStatusEffect, events:list)->None:
        unit = state.units[action.target]
        unit.statuses.append(effect.status_id)
        events.append({
            "event_type": "status_applied",
            "unit_id": unit.unit_id,
            "status_id": effect.status_id,
            "duration": effect.duration
        })
    def roll_to_hit(self, state:GameState, action:SubmittedAction, effect:AbilityDefinition, events:list)->tuple[bool, dict]:
        event = {
            "event_type": "attack_hit",
            "unit_id": action.unit_id,
            "action_id": action.action_id,
            "target_id": action.target,
            "roll": 0,
            "bonus": effect.tohit_bonus
            }
        events.append(event)
        return True


    def resolve_action(self, state:GameState, action: SubmittedAction)->tuple[GameState, list]:
        if not self.verify_action(state, action):
            return state, []
        newState = copy.deepcopy(state)
        ability = self.abilityDefinitions[action.action_id]
        events = []
        if ability.tohit_bonus is not None: #Make an attack roll!
            if not self.roll_to_hit(newState, action, ability, events):
                return newState, events
        for effect in ability.effects:
            match effect.effect_type:
                case "move":
                    self.handleMoveEffect(newState, action, events)
                case "heal":
                    self.handleHealEffect(newState, action, effect, events)
                case "damage":
                    self.handleDamageEffect(newState, action, effect, events)
                case "pull":
                    self.handlePullEffect(newState, action, effect, events)
                case "apply_status":
                    self.handleApplyStatusEffect(newState, action, effect, events)
        return newState, events