import os
import pygame

class AssetsManager:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def asset_path(*args):
        return os.path.join(AssetsManager.BASE_DIR, *args)

    @staticmethod
    def load_image(folder, filename, scale=None):
        path = AssetsManager.asset_path("..", "assets", folder, filename)
        try:
            image = pygame.image.load(path).convert_alpha()
            if scale:
                image = pygame.transform.scale(image, scale)
            return image
        except pygame.error:
            print(f"Errore: Impossibile trovare {path}")
            return pygame.Surface((32, 32))

    @staticmethod
    def get_frames_for_character(char):
        folder = char.__class__.__name__.lower()
        return {
            "idle": AssetsManager.asset_path("..", "assets", folder, f"{folder}_1.png"),
            "walk_1": AssetsManager.asset_path("..", "assets", folder, f"{folder}_2.png"),
            "walk_2": AssetsManager.asset_path("..", "assets", folder, f"{folder}_3.png"),
            "attack": AssetsManager.asset_path("..", "assets", folder, f"{folder}_4.png")
        }