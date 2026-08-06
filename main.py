import asyncio
import pygame

from gui.gui_runner import gui_main


async def main() -> None:
    print("Root main.py loaded")
    print("Pygame loaded from:", getattr(pygame, "__file__", None))
    print("Pygame version:", getattr(pygame, "__version__", None))

    await gui_main()


asyncio.run(main())