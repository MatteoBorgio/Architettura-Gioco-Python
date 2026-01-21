import pygame

from project.characters import Character

class CharacterSprite(pygame.sprite.Sprite):
    def __init__(self, model: Character, x, y):
        super().__init__()
        self.model = model

def main():
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    bg = pygame.image.load("../assets/background.jpg")
    bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.blit(bg, (0, 0))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()

