import pygame

from project.characters import Character
from enum import Enum

from project.monsters import Monster

class SpriteState(Enum):
    IDLE = "idle"
    MOVE_TO_TARGET = "move"
    ATTACK = "attack"

class CharacterSprite(pygame.sprite.Sprite):
    BAR_WIDTH = 60
    BAR_HEIGHT = 8
    CHARACTER_SIZE_X = 180
    CHARACTER_SIZE_Y  = 180
    SPEED = 200
    ATTACK_DURATION = 1
    WALK_INTERVAL = 0.2

    def __init__(self, model: Character, x: int, y: int, frames: dict[str, str]):
        super().__init__()
        self.model = model

        self.frames = {}
        for key, path in frames.items():
            image = pygame.image.load(path).convert_alpha()
            self.frames[key] = pygame.transform.scale(image, (self.CHARACTER_SIZE_X, self.CHARACTER_SIZE_Y))

        self.state = SpriteState.IDLE
        self.target = None
        self.timer = 0.0
        self.walk_timer = 0.0
        self.walk_frame_toggle = False

        self.image = self.frames["idle"]
        self.rect = self.image.get_rect(midbottom=(x, y))

    # -----     ATTACK MECHANICS     -----
    def start_attack(self, target_sprite):
        self.target = target_sprite
        self.state = SpriteState.MOVE_TO_TARGET
        self.timer = 0.0

    def _move_to_target(self, dt):
        dx = self.target.rect.centerx - self.rect.centerx

        if abs(dx) > 40:
            direction = 1 if dx > 0 else -1
            self.rect.x += direction * self.SPEED * dt
            self.walk_timer += dt
            if self.walk_timer >= self.WALK_INTERVAL:
                self.walk_timer = 0.0
                self.walk_frame_toggle = not self.walk_frame_toggle

            self.image = self.frames["walk_1"] if self.walk_frame_toggle else self.frames["walk_2"]

        else:
            self.state = "attack"
            self.timer = 0.0
            self.image = self.frames["attack"]

    def _attack(self, dt):
        self.timer += dt
        if self.timer >= self.ATTACK_DURATION:
            self.state = SpriteState.IDLE
            self.target = None
            self.image = self.frames["idle"]


    # -----     HP BAR     -----
    def draw_hp_bar(self, surface: pygame.Surface):
        hp_ratio = self.model.hp / self.model.max_hp
        bar_x = self.rect.centerx - self.BAR_WIDTH // 2
        bar_y = self.rect.top

        pygame.draw.rect(
            surface,
            (180, 0, 0),
            (bar_x, bar_y, self.BAR_WIDTH, self.BAR_HEIGHT)
        )

        pygame.draw.rect(
            surface,
            (0, 200, 0),
            (bar_x, bar_y, int(self.BAR_WIDTH * hp_ratio), self.BAR_HEIGHT)
        )

    def update(self, dt: float):
        if self.state == SpriteState.IDLE:
            self.image = self.frames["idle"]

        elif self.state == SpriteState.MOVE_TO_TARGET:
            self._move_to_target(dt)

        elif self.state == SpriteState.ATTACK:
            self._attack(dt)

class EnemySprite(pygame.sprite.Sprite):
    BAR_WIDTH = 60
    BAR_HEIGHT = 8
    SIZE_X = 180
    SIZE_Y = 180
    WALK_ANIM_INTERVAL = 0.3
    SPEED = 150

    def __init__(self, model: Monster, x: int, y: int, frames: dict[str, str]):
        super().__init__()
        self.model = model

        self.frames = {}
        for key, path in frames.items():
            img = pygame.image.load(path).convert_alpha()
            self.frames[key] = pygame.transform.scale(img, (self.SIZE_X, self.SIZE_Y))

        self.image = self.frames.get("idle", list(self.frames.values())[0])
        self.rect = self.image.get_rect(midbottom=(x, y))

        self.walk_timer = 0
        self.walk_toggle = False

        self.state = "idle"
        self.target = None
        self.attack_timer = 0

    def draw_hp_bar(self, surface: pygame.Surface):
        hp_ratio = self.model.hp / self.model.max_hp
        bar_x = self.rect.centerx - self.BAR_WIDTH // 2
        bar_y = self.rect.top - 10

        pygame.draw.rect(surface, (180, 0, 0), (bar_x, bar_y, self.BAR_WIDTH, self.BAR_HEIGHT))
        pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, int(self.BAR_WIDTH * hp_ratio), self.BAR_HEIGHT))

    # --------- LOGICA BASE ---------
    def update(self, dt):
        if self.state == "walk" and self.target:
            self._move_to_target(dt)
        elif self.state == "attack":
            self._attack_target(dt)

    def _move_to_target(self, dt):
        dx = self.target.rect.centerx - self.rect.centerx

        if abs(dx) > 50:  # distanza minima per attacco
            direction = 1 if dx > 0 else -1
            self.rect.x += direction * self.SPEED * dt

            # alternanza animazione walk
            self.walk_timer += dt
            if self.walk_timer >= self.WALK_ANIM_INTERVAL:
                self.walk_timer = 0
                self.walk_toggle = not self.walk_toggle

            self.image = self.frames.get("walk_1") if self.walk_toggle else self.frames.get("walk_2")

        else:
            self.state = "attack"
            self.attack_timer = 0
            self.image = self.frames.get("attack", self.image)

    def _attack_target(self, dt):
        self.attack_timer += dt
        if self.attack_timer >= 1.0:
            if self.target and self.target.hp > 0:
                self.model.attack(self.target)
            self.state = "idle"
            self.image = self.frames.get("idle", self.image)

    def set_target(self, target: Character):
        self.target = target
        self.state = "walk"

