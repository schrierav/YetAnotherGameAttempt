from typing import Literal, Annotated
from pydantic import BaseModel, Field
from enums import ActionSlot, EquipmentSlot, StatName, GamePhase
from literals import PlayerSlot
from .const import *

class Coord(BaseModel):
    x:int = Field(ge=0)
    y:int = Field(ge=0)

class StatModifier(BaseModel):
    stat: StatName
    value: int

class MoveEffect(BaseModel):
    effect_type: Literal["move"]

class HealEffect(BaseModel):
    effect_type: Literal["heal"]
    amount: int

class DamageEffect(BaseModel):
    effect_type: Literal["damage"]
    quality_bonus: int = 0
    damage_roll: str = DEFAULTDAMAGE

class PullEffect(BaseModel):
    effect_type: Literal["pull"]
    destination: Coord

class ApplyStatusEffect(BaseModel):
    effect_type: Literal["apply_status"]
    status_id: str
    duration: int

class EndTurnEffect(BaseModel):
    effect_type: Literal["end_turn"]

EffectDefinition = Annotated[MoveEffect | HealEffect | DamageEffect | PullEffect | ApplyStatusEffect | EndTurnEffect,
                             Field(discriminator = "effect_type")]

class AbilityDefinition(BaseModel):
    action_id:str
    display_name:str
    action_slot: ActionSlot
    range_min: int = 1
    range_max: int = 1
    effects: list[EffectDefinition] = Field(default_factory=list)
    tohit_bonus: int | None = None #Some actions may have an attack roll associated with them. If extant, it will be an int containing the bonus to hit. If not, it will be None.

class EquipmentDefinition(BaseModel):
    equipment_id:str
    display_name:str
    slot: EquipmentSlot
    point_cost: int = 0
    stat_modifiers: list[StatModifier] = Field(default_factory=list)
    granted_action_ids: list[str] = Field(default_factory=list)

class UnitState(BaseModel):
    unit_id:str
    owner:PlayerSlot
    position:Coord
    wounds:int
    statuses: list[str] = Field(default_factory=list)
    equipment: dict[EquipmentSlot, str] = Field(default_factory=dict)

class GameState(BaseModel):
    match_id:str
    map_id:str
    player1_id:str
    player2_id:str
    active_player:PlayerSlot
    active_unit: str | None = None
    phase: GamePhase
    units: dict[str, UnitState]
    round_number:int = 0
    activated_unit_ids: list[str] = Field(default_factory=list)
    available_action_slots: list[ActionSlot] = Field(default_factory=lambda: [
    ActionSlot.MAIN,
    ActionSlot.MOVE,
    ActionSlot.BONUS,])
    winner: PlayerSlot | None=None

