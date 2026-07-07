from enum import Enum
from typing import Literal, Annotated
from pydantic import BaseModel, Field

class Coord(BaseModel):
    x:int = Field(ge=0)
    y:int = Field(ge=0)

class EquipmentSlot(str, Enum):
    ARMOR = "armor"
    ACCESSORY = "accessory"
    MAINHAND = "main-hand"
    OFFHAND = "off-hand"
    TWOHAND = "two-handed"

class StatName(str, Enum):
    MAXHEALTH = "maximum health"
    ARMOR = "armor"
    EVASION = "evasion"
    ACCURACY = "accuracy"
    MOVEMENT = "movement"

class ActionSlot(str, Enum):
    BONUS = "bonus action"
    MAIN = "main action"
    MOVE = "movement action"

class StatModifier(BaseModel):
    stat: StatName
    value: int

class MoveEffect(BaseModel):
    effect_type: Literal["move"]
    max_distance: int

class HealEffect(BaseModel):
    effect_type: Literal["heal"]
    amount: int

class DamageEffect(BaseModel):
    effect_type: Literal["damage"]
    amount: int
    quality_bonus: int = 0
    damage_roll: str = '1d6'

class PullEffect(BaseModel):
    effect_type: Literal["pull"]
    distance: int

class ApplyStatusEffect(BaseModel):
    effect_type: Literal["apply_status"]
    status_id: str
    duration: int

EffectDefinition = Annotated[MoveEffect | HealEffect | DamageEffect | PullEffect | ApplyStatusEffect,
                             Field(discriminator = "effect_type")]

class ActionDefinition(BaseModel):
    action_id:str
    display_name:str
    action_slot: ActionSlot
    range_min: int = 1
    range_max: int = 1
    effects: list[EffectDefinition] = Field(default_factory=list)

class EquipmentDefinition(BaseModel):
    equipment_id:str
    display_name:str
    slot: EquipmentSlot
    point_cost: int = 0
    stat_modifiers: list[StatModifier] = Field(default_factory=list)
    granted_actions: list[ActionDefinition] = Field(default_factory=list)

PlayerSlot = Literal["player1", "player2"]

class UnitState(BaseModel):
    unit_id:str
    owner:PlayerSlot
    position:Coord
    wounds:int
    statuses: list[str] = Field(default_factory=list)
    equipment: dict[EquipmentSlot, str] = Field(default_factory=dict)

class GamePhase(str, Enum):
    DEPLOYMENT = "deployment"
    ACTIVE_UNIT = "active_unit"
    SELECTING_UNIT = "selecting_unit"
    GAME_OVER = "game_over"

class GameState(BaseModel):
    match_id:str
    map_id:str
    player1_id:str
    player2_id:str
    active_player:PlayerSlot
    phase: GamePhase
    units: dict[str, UnitState]
    round_number:int = 0
    activated_unit_ids: list[str] = Field(default_factory=list)
    available_action_slots: list[ActionSlot] = Field(default_factory=lambda: [
    ActionSlot.MAIN,
    ActionSlot.MOVE,
    ActionSlot.BONUS,])
    available_actions: list[ActionSlot] | None = None
    winner: PlayerSlot | None=None

