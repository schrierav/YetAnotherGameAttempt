from enum import Enum
from typing import Literal, Annotated
from pydantic import BaseModel, Field
from state import Coord, ActionSlot, PlayerSlot
"""
Let's talk actions that are possible.
When submitting an action, that will look like:
Spawning a character in a location
Moving your active character
Targeting another character with an ability
Ending a turn early
"""

class ActionHandler(str, Enum):
    Effect = "effects"
    Ability = "ability"
    DeployUnit = "deploy"
    SelectUnit = "selectUnit"

class SubmittedAction(BaseModel):
    action_id: str
    handler: ActionHandler
    target: Coord | str

class ActionRejectedEvent(BaseModel):
    event_type: Literal["action_rejected"]
    reason: str

class ActionAcceptedEvent(BaseModel):
    event_type: Literal["action_accepted"]
    action_id: str
    unit_id: str

class UnitMovedEvent(BaseModel):
    event_type: Literal["unit_moved"]
    unit_id: str
    start: Coord
    end: Coord
    path: list[Coord] = Field(default_factory=list)

class UnitDamagedEvent(BaseModel):
    event_type: Literal["unit_damaged"]
    unit_id: str
    amount: int
    new_wounds: int

class UnitHealedEvent(BaseModel):
    event_type: Literal["unit_healed"]
    unit_id: str
    amount: int
    new_wounds: int

class ActionSlotSpentEvent(BaseModel):
    event_type: Literal["action_slot_spent"]
    unit_id: str
    slot: ActionSlot
    remaining_slots: list[ActionSlot]

class UnitActivationUpdatedEvent(BaseModel):
    event_type: Literal["unit_activation_updated"]
    active_player: PlayerSlot
    active_unit_id: str
    available_action_slots: list[ActionSlot]

class UnitActivationEndedEvent(BaseModel):
    event_type: Literal["unit_activation_ended"]
    unit_id: str

class UnitSelectionStartedEvent(BaseModel):
    event_type: Literal["unit_selection_started"]
    active_player: PlayerSlot

class RoundStartedEvent(BaseModel):
    event_type: Literal["round_started"]
    round_number: int
    active_player: PlayerSlot

class GameEndedEvent(BaseModel):
    event_type: Literal["game_ended"]
    winner: PlayerSlot | None

GameEvent = Annotated[
    ActionRejectedEvent
    | ActionAcceptedEvent
    | UnitMovedEvent
    | UnitDamagedEvent
    | UnitHealedEvent
    | ActionSlotSpentEvent
    | UnitActivationUpdatedEvent
    | UnitActivationEndedEvent
    | UnitSelectionStartedEvent
    | RoundStartedEvent
    | GameEndedEvent,
    Field(discriminator="event_type"),
]

