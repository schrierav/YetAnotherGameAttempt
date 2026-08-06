import pygame
from gui.spritesheet import SpriteSheet

GRID_SIZE = 64
BG_COLOR = (40, 40, 40)
GRID_COLOR = (80, 80, 80)
SPRITE_SCALE = 2
SPRITE_SIZE = 32 * SPRITE_SCALE
paths = ["assets/character_sprites/Human-Commander.png", "assets/character_sprites/Human-Paladin.png", "assets/character_sprites/Human-Commander.png"]


class GameHandler:
    def __init__(self, display: pygame.display, gamestate):
        self.gamestate = gamestate
        self.display = display
        self.unitSprites = {}
        self.active_unit = None

        index = 0
        for unit in self.gamestate.get("units", {}).values():
            self.unitSprites[unit["unit_id"]] = SpriteSheet(paths[index % len(paths)], SPRITE_SCALE)
            index += 1

    def drawMap(self):
        self.display.fill(BG_COLOR)
        for x in range(0, self.display.get_width(), GRID_SIZE):
            pygame.draw.line(self.display, GRID_COLOR, (x, 0), (x, self.display.get_height()))
        for y in range(0, self.display.get_height(), GRID_SIZE):
            pygame.draw.line(self.display, GRID_COLOR, (0, y), (self.display.get_width(), y))
        for unit in self.gamestate.get("units", {}).values():
            sprite = self.unitSprites[unit["unit_id"]].image_at((0, 0, SPRITE_SIZE, SPRITE_SIZE), colorkey=(0, 0 ,0))
            self.display.blit(sprite, (unit["position"]["x"] * GRID_SIZE, unit["position"]["y"] * GRID_SIZE))
        pygame.display.flip()

    def handleClick(self, pos):
        grid_x = pos[0] // GRID_SIZE
        grid_y = pos[1] // GRID_SIZE
        if self.active_unit:
            self.active_unit["position"]["x"] = grid_x
            self.active_unit["position"]["y"] = grid_y
            self.active_unit = None
            print(f"Moved unit to grid coordinates: ({grid_x}, {grid_y})")
        else:
            for unit in self.gamestate.get("units", {}).values():
                if unit["position"]["x"] == grid_x and unit["position"]["y"] == grid_y:
                    self.active_unit = unit
                    print(f"Selected unit {unit['unit_id']} at grid coordinates: ({grid_x}, {grid_y})")
                    break