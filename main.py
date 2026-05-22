# main.py
import pygame
from src.ui.scene_manager import SceneManager
from src.ui.menu_scene import MenuScene
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)



import ctypes
try:
    
    myappid = 'mycompany.quoridor.game.1' 
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except AttributeError:
    pass

def main() -> None:
    pygame.init()

    try:
        icon_image = pygame.image.load("assets/icon.png")
        pygame.display.set_icon(icon_image)
    except FileNotFoundError:
        print("Warning: icon.png not found. Skipping custom icon.")

    WINDOW_TITLE = "Quoridor"
    W, H = 1000, 750

    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption(WINDOW_TITLE)

    manager = SceneManager(screen)
    manager.push(MenuScene(manager))

    manager.run()

    pygame.quit()


if __name__ == "__main__":
    main()