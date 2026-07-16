from helpers.helpers import sampleResolver, sampleGamestate, sampleEquipment, sampleAbility
from simple_display.text_display import TextDisplay

if __name__ == "__main__":
    print("This script is being run directly.")

    gamestate = sampleGamestate()
    resolver = sampleResolver()
    display = TextDisplay(sampleEquipment(), sampleAbility())

    running = True
    loops = 0
    while running:
        display.drawMap(gamestate)
        player_input = display.getUserInput()
        isLegal, response = resolver.verify_action(gamestate, player_input)
        gamestate, events = resolver.resolve_action(gamestate, player_input)
        display.parseEvents(events)
