import pytest
from pydantic import ValidationError

from shared.state import Coord, StatName, StatModifier, AbilityDefinition, ActionSlot, EquipmentDefinition,EquipmentSlot, UnitState

@pytest.mark.parametrize(
    "x, y, legal",
    [
        (0, 0, True),
        (0, 45, True),
        (45, 0, True),
        (45, 45, True),
        (1, 4, True),
        (-1, 4, False),
        (1, -4, False),
        (-1, -4, False),
        (1, "Four", False),
        ("One", 4, False),
        ("One", "Four", False),
    ]
)

def test_coords_accepts_legal_coordinates(x, y, legal):
    if legal:
        coord = Coord(x=x, y=y)
        assert coord.x == x
        assert coord.y == y
    else:
        with pytest.raises(ValidationError):
            coord = Coord(x=x,y=y)

@pytest.mark.parametrize(
    "stat, modifier, legal",
    [
        (StatName.MAXHEALTH, 1, True),
        (StatName.ARMOR, -1, True),
        (StatName.EVASION, 2, True),
        (StatName.ACCURACY, -2, True),
        (StatName.MOVEMENT, 0, True),
        (StatName.MAXHEALTH, 5000, True),
        ("ATTACK", 1, False),
        ("armoure", 1, False),
        (StatName.ARMOR, "One", False),
    ]
)

def test_modifier_validation(stat, modifier, legal):
    if legal:
        mod = StatModifier(stat=stat, value=modifier)
        assert mod.stat == stat
        assert mod.value == modifier
    else:
        with pytest.raises(ValidationError):
            mod = StatModifier(stat=stat, value=modifier)
@pytest.mark.parametrize(
    "action_id, display_name, action_slot, range_min, range_max, effects, legal",
    [
        (
            "01",
            "stab",
            ActionSlot.MAIN,
            1,
            1,
            [{"effect_type": "damage", "amount": 3}],
            True,
        ),
        (
            "02",
            "Shoot Bow",
            ActionSlot.MAIN,
            1,
            5,
            [{"effect_type": "damage", "amount": 2}],
            True,
        ),
        (
            "03",
            "Heal Spell",
            ActionSlot.MAIN,
            0,
            3,
            [{"effect_type": "heal", "amount": 3}],
            True,
        ),
        (
            "04",
            "Dash",
            ActionSlot.BONUS,
            0,
            0,
            [{"effect_type": "move", "max_distance": 3}],
            True,
        ),
        (
            "scorpion",
            "Get Over Here!",
            ActionSlot.MAIN,
            1,
            1,
            [
                {"effect_type": "damage", "amount": 1},
                {"effect_type": "pull", "destination": {"x": 3, "y": 4}},
            ],
            True,
        ),

        # Invalid: effects must be a list
        (
            "01",
            "stab",
            ActionSlot.MAIN,
            1,
            1,
            {"effect_type": "damage", "amount": 3},
            False,
        ),

        # Invalid: display_name should be str
        (
            "02",
            431,
            ActionSlot.MAIN,
            1,
            5,
            [{"effect_type": "damage", "amount": 2}],
            False,
        ),

        # Invalid: action_id should be str
        (
            3,
            "Heal Spell",
            ActionSlot.MAIN,
            0,
            3,
            [{"effect_type": "heal", "amount": 3}],
            False,
        ),

        # Invalid: action_slot should be an ActionSlot
        (
            "04",
            "Dash",
            "freebie action",
            0,
            0,
            [{"effect_type": "move", "max_distance": 3}],
            False,
        ),

        # Invalid: unknown effect_type
        (
            "scorpion",
            "Get Over Here!",
            ActionSlot.MAIN,
            1,
            1,
            [
                {"effect_type": "damage", "amount": 1},
                {"effect_type": "PullEffect", "destination": {"x": 3, "y": 4}},
            ],
            False,
        ),
    ],
)
def test_action_definition_validation(
    action_id,
    display_name,
    action_slot,
    range_min,
    range_max,
    effects,
    legal,
):
    if legal:
        act = AbilityDefinition(
            action_id=action_id,
            display_name=display_name,
            action_slot=action_slot,
            range_min=range_min,
            range_max=range_max,
            effects=effects,
        )

        assert act.action_id == action_id
        assert act.display_name == display_name
        assert act.action_slot == action_slot
        assert act.range_min == range_min
        assert act.range_max == range_max

    else:
        with pytest.raises(ValidationError):
            AbilityDefinition(
                action_id=action_id,
                display_name=display_name,
                action_slot=action_slot,
                range_min=range_min,
                range_max=range_max,
                effects=effects,
            )

@pytest.mark.parametrize(
    "equipment_id, display_name, slot, point_cost, legal",
    [
        ("leather_armor", "Leather Armor", EquipmentSlot.ARMOR, 0, True),
        ("power_ring", "Ring of Power", EquipmentSlot.ACCESSORY, 5, True),
        ("short_sword", "Short Sword", EquipmentSlot.MAINHAND, 3, True),
        ("shield", "Shield", EquipmentSlot.OFFHAND, 2, True),
        ("greatsword", "Greatsword", EquipmentSlot.TWOHAND, 6, True),

        # Invalid equipment_id
        (123, "Leather Armor", EquipmentSlot.ARMOR, 0, False),

        # Invalid display_name
        ("leather_armor", 123, EquipmentSlot.ARMOR, 0, False),

        # Invalid slot
        ("leather_armor", "Leather Armor", "hat", 0, False),

        # This is currently legal unless you add a constraint
        ("cursed_ring", "Cursed Ring", EquipmentSlot.ACCESSORY, -5, True),
    ],
)
def test_equipment_definition_basic_validation(
    equipment_id,
    display_name,
    slot,
    point_cost,
    legal,
):
    if legal:
        equipment = EquipmentDefinition(
            equipment_id=equipment_id,
            display_name=display_name,
            slot=slot,
            point_cost=point_cost,
        )

        assert equipment.equipment_id == equipment_id
        assert equipment.display_name == display_name
        assert equipment.slot == slot
        assert equipment.point_cost == point_cost

    else:
        with pytest.raises(ValidationError):
            EquipmentDefinition(
                equipment_id=equipment_id,
                display_name=display_name,
                slot=slot,
                point_cost=point_cost,
            )

@pytest.mark.parametrize(
    "unit_id, owner, position, wounds, statuses, equipment, legal",
    [
        (
            "unit_01",
            "player1",
            {"x": 1, "y": 2},
            0,
            [],
            {},
            True,
        ),
        (
            "unit_02",
            "player2",
            Coord(x=3, y=4),
            2,
            ["poisoned", "stunned"],
            {EquipmentSlot.MAINHAND: "iron_sword"},
            True,
        ),

        # Invalid unit_id
        (
            123,
            "player1",
            {"x": 1, "y": 2},
            0,
            [],
            {},
            False,
        ),

        # Invalid owner
        (
            "unit_01",
            "player_three",
            {"x": 1, "y": 2},
            0,
            [],
            {},
            False,
        ),

        # Invalid position
        (
            "unit_01",
            "player1",
            {"x": -1, "y": 2},
            0,
            [],
            {},
            False,
        ),

        # Invalid wounds
        (
            "unit_01",
            "player1",
            {"x": 1, "y": 2},
            "bad",
            [],
            {},
            False,
        ),

        # Invalid statuses: should be list[str]
        (
            "unit_01",
            "player1",
            {"x": 1, "y": 2},
            0,
            "poisoned",
            {},
            False,
        ),

        # Invalid statuses: list contains non-string
        (
            "unit_01",
            "player1",
            {"x": 1, "y": 2},
            0,
            ["poisoned", 123],
            {},
            False,
        ),

        # Invalid equipment: should be dict[EquipmentSlot, str]
        (
            "unit_01",
            "player1",
            {"x": 1, "y": 2},
            0,
            [],
            ["iron_sword"],
            False,
        ),

        # Invalid equipment key
        (
            "unit_01",
            "player1",
            {"x": 1, "y": 2},
            0,
            [],
            {"helmet": "iron_helmet"},
            False,
        ),

        # Invalid equipment value
        (
            "unit_01",
            "player1",
            {"x": 1, "y": 2},
            0,
            [],
            {EquipmentSlot.MAINHAND: 123},
            False,
        ),
    ],
)
def test_unit_state_field_validation(
    unit_id,
    owner,
    position,
    wounds,
    statuses,
    equipment,
    legal,
):
    if legal:
        unit = UnitState(
            unit_id=unit_id,
            owner=owner,
            position=position,
            wounds=wounds,
            statuses=statuses,
            equipment=equipment,
        )

        assert unit.unit_id == unit_id
        assert unit.owner == owner
        assert unit.wounds == wounds
        assert unit.statuses == statuses
        assert unit.equipment == equipment

    else:
        with pytest.raises(ValidationError):
            UnitState(
                unit_id=unit_id,
                owner=owner,
                position=position,
                wounds=wounds,
                statuses=statuses,
                equipment=equipment,
            )