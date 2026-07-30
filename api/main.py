from fastapi import Query, FastAPI
from pydantic import BaseModel
from shared.info_exchange import SubmittedAction, GameEvent
from shared.state import GameState
from helpers.helpers import sampleResolver, sampleGamestate


gamestate = sampleGamestate()
resolver = sampleResolver()

app = FastAPI()

@app.get("/game/")
async def get_gamestate()->GameState:
    return gamestate

@app.post("/game/resolve")
async def resolve_action(action: SubmittedAction)->list[GameEvent]:
    global gamestate
    gs, events = resolver.resolve_action(gamestate, action)
    gamestate = gs
    return events
