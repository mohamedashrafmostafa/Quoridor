# main.py
import pygame
from src.ui.scene_manager import SceneManager
from src.ui.menu_scene import MenuScene

# --- Windows Taskbar Fix (Optional but highly recommended) ---
import ctypes
try:
    # This forces Windows to show your custom icon on the taskbar 
    # instead of the generic Python snake logo.
    myappid = 'mycompany.quoridor.game.1' 
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except AttributeError:
    pass
# -----------------------------------------------------------

def main() -> None:
    pygame.init()

    # --- ADD YOUR ICON HERE ---
    try:
        icon_image = pygame.image.load("assets/icon.png")
        pygame.display.set_icon(icon_image)
    except FileNotFoundError:
        print("Warning: icon.png not found. Skipping custom icon.")
    # --------------------------

    WINDOW_TITLE = "Quoridor"
    W, H = 1000, 750

    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption(WINDOW_TITLE)

    # Initialize the Scene Manager and push the Main Menu as the first state
    manager = SceneManager(screen)
    manager.push(MenuScene(manager))

    # This will block and run the game loop until the window is closed
    manager.run()

    pygame.quit()


if __name__ == "__main__":
    main()