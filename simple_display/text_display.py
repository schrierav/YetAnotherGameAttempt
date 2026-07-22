from shared.const import *
from shared.state import Coord, GameState, GamePhase, EquipmentSlot, ActionSlot, UnitState, AbilityDefinition, EquipmentDefinition
from shared.info_exchange import SubmittedAction, GameEvent, TurnStartedEvent, ActionAcceptedEvent, ActionRejectedEvent, AttackHitEvent, AttackMissedEvent, UnitMovedEvent, UnitDamagedEvent, UnitHealedEvent, ActionSlotSpentEvent, UnitActivationUpdatedEvent, UnitSelectionStartedEvent, UnitKilledEvent, RoundStartedEvent, GameEndedEvent
from pydantic import TypeAdapter

class TextDisplay:
    """A simple text-based display for the game state."""

    def __init__(self, equipmentDefinitions:dict, abilityDefinitions:dict):
        self.equipmentDefinitions = {}
        self.abilityDefinitions = {}
        for ability_id, ability in abilityDefinitions.items():
            self.abilityDefinitions[ability_id] = AbilityDefinition(**ability)
        for equipment_id, equipment in equipmentDefinitions.items():
            self.equipmentDefinitions[equipment_id] = EquipmentDefinition(**equipment)
    
    def getUnitActions(self, unit: UnitState):
        actions = []
        for slot in unit.equipment:
            gear = unit.equipment[slot]
            fulldef = self.equipmentDefinitions[gear]
            for granted_action_id in fulldef.granted_action_ids:
                actions.append(self.abilityDefinitions.get(granted_action_id))
        return actions


    def drawMap(self, gamestate: GameState):
        print(f"Current Phase: {gamestate.phase}")
        print(f"Active Player: {gamestate.active_player}")
        print("Units:")
        for unit_id, unit in gamestate.units.items():
            print(f"  Unit ID: {unit_id}, Position: ({unit.position.x}, {unit.position.y}), Wounds: {unit.wounds}")
        print("Map:")
        print(f"[x]", end="")
        for i in range(10):
            print(f"[{i}]", end="")
        print()
        for y in range(10):
            print(f"[{y}]", end="")
            for x in range(10):
                unit_here = next((u for u in gamestate.units.values() if u.position.x == x and u.position.y == y), None)
                if unit_here:
                    print(f"[{unit_here.unit_id[0]}]", end="")
                else:
                    print("[ ]", end="")
            print()  # New line after each row
    
    def getUserInput(self, state:GameState)->SubmittedAction:
        if state.phase == PHASESELECTINGUNITSTRING:
            activatable_units = []
            for unit in state.units.values():
                if unit.owner == state.active_player and unit.wounds < HITPOINTLIMIT:
                    activatable_units.append(unit)
            print("Which unit is activating?")
            for i in range(len(activatable_units)):
                print(f"{i}) {activatable_units[i].unit_id}")
            choice = int(input("Which unit is acting?"))
            if 0 <= choice < len(activatable_units):
                choice = "Unexpected input. Try again."
            unit = activatable_units[i]
        else:
            unit = state.units.get(state.active_unit)
        
        i = 0
        possibleActions = self.getUnitActions(unit)
        for action in possibleActions:
            print(f"{i}) {action.display_name}")
            i += 1
        print(f"{i}) End Turn Early")
        choice = int(input("Which action?"))
        if choice < len(possibleActions):
            action = possibleActions[choice].action_id
        else:
            action = "end_turn"
        target = input("Where?")
        target = target.strip()
        parts = target.split(",")
        if len(parts)== 2:
            target = Coord(x=parts[0], y=parts[1])

        
        return SubmittedAction(
            player_id=state.active_player,
            action_id= action,
            unit_id = unit.unit_id,
            target=target,
            handler="ability"
        )
    
    def handle_event(self, event: GameEvent) -> None:
        game_event_adaptor = TypeAdapter(GameEvent)
        parsed_event = game_event_adaptor.validate_python(event)
        match parsed_event:
            case ActionRejectedEvent():
                print(f"The action was rejected. Why? {parsed_event.reason}")

            case ActionAcceptedEvent():
                print("The action was accepted.")

            case AttackMissedEvent():
                print(f"{event["unit_id"]} goes to strike {event["target_id"]}, but rolls a {parsed_event.roll}!")
                print(f"{parsed_event.roll}+{parsed_event.bonus} isn't enough for the target EV!")

            case AttackHitEvent():
                print(f"{parsed_event.unit_id} goes to strike {parsed_event.target_id}, and rolls a {parsed_event.roll}!")
                print(f"{parsed_event.roll}+{parsed_event.bonus} is enough for the target EV!")

            case UnitMovedEvent():
                print(f"{parsed_event.unit_id} moves from {parsed_event.start} to {parsed_event.end}")

            case UnitDamagedEvent():
                print(f"Yowch! {parsed_event.unit_id} was hit for {parsed_event.amount} damage! Current wounds are {parsed_event.new_wounds}.")

            case UnitHealedEvent():
                print(f"Ahh! {parsed_event.unit_id} was healed of {parsed_event.amount} damage! Current wounds are {parsed_event.new_wounds}.")

            case UnitKilledEvent():
                print(f"Whelp, it looks like that's it for {parsed_event.unit_id}")

            case RoundStartedEvent():
                print("A new day dawns on the battlefield!")

            case GameEndedEvent():
                print("The game ended.")

            case TurnStartedEvent():
                print(f"New turn begins! Active player is {event.active_player}")

            case _:
                raise ValueError(f"Unhandled event type: {type(parsed_event).__name__}")

    def parseEvents(self, events: list):
        for event in events:
            print(event)
            self.handle_event(event)