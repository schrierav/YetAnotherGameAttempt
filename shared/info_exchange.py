from enum import Enum
from typing import Literal, Annotated
from pydantic import BaseModel, Field
from shared.state import Coord, ActionSlot, PlayerSlot
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
    EndTurn = "endTurn"

class SubmittedAction(BaseModel):
    player_id:str
    action_id: str
    unit_id: str
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

class TurnStartedEvent(BaseModel):
    event_type: Literal["turn_ended"]
    active_player: PlayerSlot

class AttackMissedEvent(BaseModel):
    event_type: Literal["attack_missed"]
    unit_id: str
    action_id: str
    target_id: str
    roll: int
    bonus: int

class AttackHitEvent(BaseModel):
    event_type: Literal["attack_hit"]
    unit_id: str
    action_id: str
    target_id: str
    roll: int
    bonus: int

class UnitKilledEvent(BaseModel):
    event_type: Literal["unit_killed"]
    unit_id: str

GameEvent = Annotated[
    ActionRejectedEvent
    | ActionAcceptedEvent
    | AttackMissedEvent
    | AttackHitEvent
    | UnitMovedEvent
    | UnitDamagedEvent
    | UnitHealedEvent
    | ActionSlotSpentEvent
    | UnitActivationUpdatedEvent
    | UnitActivationEndedEvent
    | UnitSelectionStartedEvent
    | UnitKilledEvent
    | RoundStartedEvent
    | GameEndedEvent,
    Field(discriminator="event_type"),
]

