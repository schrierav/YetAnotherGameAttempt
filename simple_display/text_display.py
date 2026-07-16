from shared.state import Coord, GameState, GamePhase, EquipmentSlot, ActionSlot, UnitState, AbilityDefinition, EquipmentDefinition
from shared.info_exchange import SubmittedAction, GameEvent, ActionAcceptedEvent, ActionRejectedEvent, AttackHitEvent, AttackMissedEvent, UnitMovedEvent, UnitDamagedEvent, UnitHealedEvent, ActionSlotSpentEvent, UnitActivationUpdatedEvent, UnitSelectionStartedEvent, UnitKilledEvent, RoundStartedEvent, GameEndedEvent
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
    
    def getUnitActions(self, gamestate: GameState, unit: UnitState):
        print("Getting actions")
        if unit.unit_id in gamestate.activated_unit_ids:
            return "[ALREADY ACTIVATED]"
        actions = []
        for slot in unit.equipment:
            gear = unit.equipment[slot]
            fulldef = self.equipmentDefinitions[gear]
            actions.append(fulldef.granted_action_ids)
        return str(actions)


    def drawMap(self, gamestate: GameState):
        print(f"Current Phase: {gamestate.phase}")
        print(f"Active Player: {gamestate.active_player}")
        print("Units:")
        for unit_id, unit in gamestate.units.items():
            print(f"  Unit ID: {unit_id}, Position: ({unit.position.x}, {unit.position.y}), Wounds: {unit.wounds}")
            print(f"    Equipment: {unit.equipment}")
            print(f"    Actions: {self.getUnitActions(gamestate, unit)}")
        print("Map:")
        for y in range(10):
            for x in range(10):
                unit_here = next((u for u in gamestate.units.values() if u.position.x == x and u.position.y == y), None)
                if unit_here:
                    print(f"[{unit_here.unit_id[0]}]", end="")
                else:
                    print("[ ]", end="")
            print()  # New line after each row
    
    def getUserInput(self)->SubmittedAction:
        unit = input("Which unit is acting?")
        action = input("What is it doing?")
        target = input("Where?")
        target = target.strip()
        parts = target.split(",")
        if len(parts)== 2:
            target = Coord(x=parts[0], y=parts[1])
        return SubmittedAction(
            player_id="p2",
            action_id= action,
            unit_id = unit,
            target=target,
            handler="ability"
        )
    
    def handle_event(self, event: GameEvent) -> None:
        game_event_adaptor = TypeAdapter(GameEvent)
        parsed_event = game_event_adaptor.validate_python(event)
        match parsed_event:
            case ActionRejectedEvent():
                print(f"The action was rejected. Why? {event.reason}")

            case ActionAcceptedEvent():
                print("The action was accepted.")

            case AttackMissedEvent():
                print(f"{event["unit_id"]} goes to strike {event["target_id"]}, but rolls a {event.roll}!")
                print(f"{event.roll}+{event.bonus} isn't enough for the target EV!")
            case AttackHitEvent():
                print(f"{event.unit_id} goes to strike {event.target_id}, and rolls a {event.roll}!")
                print(f"{event.roll}+{event.bonus} is enough for the target EV!")

            case UnitMovedEvent():
                print(f"{event.unit_id} moves from {event.start} to {event.end}")

            case UnitDamagedEvent():
                print(f"Yowch! {event.unit_id} was hit for {event.amount} damage! Current wounds are {event.new_wounds}.")

            case UnitHealedEvent():
                print(f"Ahh! {event.unit_id} was healed of {event.amount} damage! Current wounds are {event.new_wounds}.")

            case UnitKilledEvent():
                print(f"Whelp, it looks like that's it for {event.unit_id}")

            case RoundStartedEvent():
                print("A new day dawns on the battlefield!")

            case GameEndedEvent():
                print("The game ended.")

            case _:
                raise ValueError(f"Unhandled event type: {type(event).__name__}")

    def parseEvents(self, events: list):
        for event in events:
            self.handle_event(event)