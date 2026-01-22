import pygame
from enum import Enum
from pathlib import Path

# ---------- UTILITY ----------
def asset_path(*args):
    return str(Path(__file__).parent.joinpath(*args))

# ---------- STATI SPRITE ----------
class SpriteState(Enum):
    IDLE = "idle"
    MOVE_TO_TARGET = "move"
    ATTACK = "attack"
    RETURN = "return"

# ---------- SPRITE DEL GIOCATORE ----------
class CharacterSprite(pygame.sprite.Sprite):
    BAR_WIDTH = 60
    BAR_HEIGHT = 8
    SIZE_X = 180
    SIZE_Y = 180
    SPEED = 200
    ATTACK_DURATION = 1
    WALK_INTERVAL = 0.2

    def __init__(self, model, x, y, frames: dict):
        super().__init__()
        self.model = model
        self.state = SpriteState.IDLE
        self.target = None
        self.timer = 0
        self.walk_timer = 0
        self.walk_toggle = False
        self.start_pos = (x, y)  # posizione originale

        # Caricamento immagini
        self.frames = {}
        for key, path in frames.items():
            img = pygame.image.load(path).convert_alpha()
            self.frames[key] = pygame.transform.scale(img, (self.SIZE_X, self.SIZE_Y))

        self.image = self.frames["idle"]
        self.rect = self.image.get_rect(midbottom=(x, y))

    def start_attack(self, target_sprite):
        self.target = target_sprite
        self.state = SpriteState.MOVE_TO_TARGET
        self.timer = 0

    def _move_to_target(self, dt):
        dx = self.target.rect.centerx - self.rect.centerx
        if abs(dx) > 40:
            direction = 1 if dx > 0 else -1
            self.rect.x += direction * self.SPEED * dt
            self.walk_timer += dt
            if self.walk_timer >= self.WALK_INTERVAL:
                self.walk_timer = 0
                self.walk_toggle = not self.walk_toggle
            self.image = self.frames["walk_1"] if self.walk_toggle else self.frames["walk_2"]
        else:
            self.state = SpriteState.ATTACK
            self.timer = 0
            self.image = self.frames["attack"]

    def _attack(self, dt):
        self.timer += dt
        if self.timer >= self.ATTACK_DURATION:
            if self.target:
                self.model.attack(self.target.model)
            self.state = SpriteState.RETURN
            self.target = None

    def _return_to_start(self, dt):
        dx = self.start_pos[0] - self.rect.centerx
        if abs(dx) > 5:
            direction = 1 if dx > 0 else -1
            self.rect.x += direction * self.SPEED * dt
            self.image = self.frames["walk_1"] if self.walk_toggle else self.frames["walk_2"]
        else:
            self.rect.centerx = self.start_pos[0]
            self.state = SpriteState.IDLE
            self.image = self.frames["idle"]

    def draw_hp_bar(self, surface):
        ratio = self.model.hp / self.model.max_hp
        bar_x = self.rect.centerx - self.BAR_WIDTH // 2
        bar_y = self.rect.top - 10
        pygame.draw.rect(surface, (180, 0, 0), (bar_x, bar_y, self.BAR_WIDTH, self.BAR_HEIGHT))
        pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, int(self.BAR_WIDTH * ratio), self.BAR_HEIGHT))

    def update(self, dt):
        if self.state == SpriteState.IDLE:
            self.image = self.frames["idle"]
        elif self.state == SpriteState.MOVE_TO_TARGET:
            self._move_to_target(dt)
        elif self.state == SpriteState.ATTACK:
            self._attack(dt)
        elif self.state == SpriteState.RETURN:
            self._return_to_start(dt)


# ---------- SPRITE DEL NEMICO ----------
class EnemySprite(pygame.sprite.Sprite):
    BAR_WIDTH = 60
    BAR_HEIGHT = 8
    SIZE_X = 180
    SIZE_Y = 180
    SPEED = 150
    ATTACK_DURATION = 1
    WALK_INTERVAL = 0.3

    def __init__(self, model, x, y, frames: dict):
        super().__init__()
        self.model = model
        self.state = SpriteState.IDLE
        self.target = None
        self.timer = 0
        self.walk_timer = 0
        self.walk_toggle = False
        self.start_pos = (x, y)

        self.frames = {}
        for key, path in frames.items():
            img = pygame.image.load(path).convert_alpha()
            self.frames[key] = pygame.transform.scale(img, (self.SIZE_X, self.SIZE_Y))

        self.image = self.frames.get("idle")
        self.rect = self.image.get_rect(midbottom=(x, y))

    def set_target(self, target_sprite):
        self.target = target_sprite
        self.state = SpriteState.MOVE_TO_TARGET
        self.timer = 0

    def _move_to_target(self, dt):
        dx = self.target.rect.centerx - self.rect.centerx
        if abs(dx) > 50:
            direction = 1 if dx > 0 else -1
            self.rect.x += direction * self.SPEED * dt
            self.walk_timer += dt
            if self.walk_timer >= self.WALK_INTERVAL:
                self.walk_timer = 0
                self.walk_toggle = not self.walk_toggle
            self.image = self.frames.get("walk_1") if self.walk_toggle else self.frames.get("walk_2")
        else:
            self.state = SpriteState.ATTACK
            self.timer = 0
            self.image = self.frames.get("attack", self.image)

    def _attack_target(self, dt):
        self.timer += dt
        if self.timer >= self.ATTACK_DURATION:
            if self.target and self.target.model.hp > 0:
                self.model.attack(self.target.model)
            self.state = SpriteState.RETURN
            self.target = None

    def _return_to_start(self, dt):
        dx = self.start_pos[0] - self.rect.centerx
        if abs(dx) > 5:
            direction = 1 if dx > 0 else -1
            self.rect.x += direction * self.SPEED * dt
            self.image = self.frames.get("walk_1") if self.walk_toggle else self.frames.get("walk_2")
        else:
            self.rect.centerx = self.start_pos[0]
            self.state = SpriteState.IDLE
            self.image = self.frames.get("idle", self.image)

    def draw_hp_bar(self, surface):
        ratio = self.model.hp / self.model.max_hp
        bar_x = self.rect.centerx - self.BAR_WIDTH // 2
        bar_y = self.rect.top - 10
        pygame.draw.rect(surface, (180, 0, 0), (bar_x, bar_y, self.BAR_WIDTH, self.BAR_HEIGHT))
        pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, int(self.BAR_WIDTH * ratio), self.BAR_HEIGHT))

    def update(self, dt):
        if self.state == SpriteState.IDLE:
            self.image = self.frames.get("idle", self.image)
        elif self.state == SpriteState.MOVE_TO_TARGET and self.target:
            self._move_to_target(dt)
        elif self.state == SpriteState.ATTACK:
            self._attack_target(dt)
        elif self.state == SpriteState.RETURN:
            self._return_to_start(dt)
