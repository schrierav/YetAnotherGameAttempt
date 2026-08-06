import asyncio
import pygame
from gui.game_handler import GameHandler


WIDTH = 800
HEIGHT = 600



async def gui_main() -> None:
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("My Pygbag Game")

    clock = pygame.time.Clock()

    running = True

    ###Building a sample gamestate to display
    unit1 = {"unit_id":"A",
            "owner":"player1",
            "position":{"x": 1, "y": 2},
            "wounds":0,
            "statuses":[],
            "equipment":{"mainhand":"short_sword", "boots":"old_boots"}
    }
        
    unit2 = {"unit_id":"B",
            "owner":"player2",
            "position":{"x": 2, "y": 2},
            "wounds":0,
            "statuses":[],
            "equipment":{"mainhand":"short_sword", "boots":"old_boots"}
    }

    gamestate = {
            "match_id":"sampleMatch",
            "map_id":"sampleMap",
            "player1_id":"player1",
            "player2_id":"player2",
            "active_player":"player2",
            "phase":"Placeholder Phase",
            "units":{"A":unit1, "B":unit2},
            "round_number":1,
            "activated_unit_ids":["A"],
            "available_action_slots":["Placeholder1", "Placeholder2", "Placeholder3"],
            "winner":None
    }

    display = GameHandler(screen, gamestate)

    while running:
        # Handle events.
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                        # 1 = Left Click, 2 = Middle Click, 3 = Right Click
                        if event.button == 1: 
                                display.handleClick(event.pos)

        # Update game state.
        display.drawMap()

        # Limit the game to approximately 60 FPS.
        dt = clock.tick(30)

        # Give control back to the browser.
        await asyncio.sleep(0)

    pygame.quit()
