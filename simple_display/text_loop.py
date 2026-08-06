from helpers.helpers import sampleEquipment, sampleAbility
from simple_display.text_display import TextDisplay
from shared.state import GameState
from shared.info_exchange import GameEvent
from pydantic import TypeAdapter
import requests

def text_loop():
    url = "http://127.0.0.1:8000/game/"
    """
    MANUAL VERSION SAVED FOR POSTERITY
    gamestate = sampleGamestate()
    resolver = sampleResolver()
    display = TextDisplay(sampleEquipment(), sampleAbility())

    running = True
    while running:
        display.drawMap(gamestate)
        player_input = display.getUserInput(gamestate)
        print(gamestate.activated_unit_ids)
        isLegal, response = resolver.verify_action(gamestate, player_input)
        gamestate, events = resolver.resolve_action(gamestate, player_input)
        display.parseEvents(events)
    """

    display = TextDisplay(sampleEquipment(), sampleAbility())
    response = requests.get(url)
    event_list_adapter = TypeAdapter(list[GameEvent])


    gamestate = GameState.model_validate(response.json())
    display.drawMap(gamestate)
    running = True
    while running:
        display.drawMap(gamestate)
        player_input = display.getUserInput(gamestate)
        response = requests.post(url=url+"resolve", json=player_input.model_dump(mode="json"))
        events = event_list_adapter.validate_python(response.json())
        response = requests.get(url)
        gamestate = GameState.model_validate(response.json())
        display.parseEvents(events)