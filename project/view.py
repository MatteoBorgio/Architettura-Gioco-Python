import math

import pygame
from enum import Enum

# ---------- STATI SPRITE ----------
class SpriteState(Enum):
    IDLE = "idle"
    MOVE_TO_TARGET = "move"
    ATTACK = "attack"
    RETURN = "return"

class Card:
    WIDTH = 100
    HEIGHT = 150
    PADDING = 10

    def __init__(self, card_image_path: str, content_image_path: str | None, model, center_pos: tuple[int, int], font=None):
        self.model = model
        self.font = font

        raw_card_image = pygame.image.load(card_image_path).convert_alpha()
        self.card_image = pygame.transform.smoothscale(raw_card_image, (self.WIDTH, self.HEIGHT))
        self.card_rect = self.card_image.get_rect(center=center_pos)
        self.content_image_path = content_image_path

        if self.content_image_path is not None:
            raw_content_image = pygame.image.load(self.content_image_path).convert_alpha()

            max_width = self.WIDTH - self.PADDING * 2
            max_height = self.HEIGHT - self.PADDING * 2

            scale = min(max_width / raw_content_image.get_width(), max_height / raw_content_image.get_height())

            new_size = (int(raw_content_image.get_width() * scale), int(raw_content_image.get_height() * scale))

            self.content_image = pygame.transform.smoothscale(raw_content_image, new_size)

            self.content_rect = self.content_image.get_rect(center=self.card_rect.center)

    def draw(self, screen):
        font = pygame.font.Font(None, int(self.font.get_height() * 0.6))
        screen.blit(self.card_image, self.card_rect)
        if self.content_image_path is not None:
            screen.blit(self.content_image, self.content_rect)
        if self.font and self.content_image_path is not None:
            name_surface = self.font.render(self.model.name, True, (0, 0, 0))
            name_rect = name_surface.get_rect(center=(self.card_rect.centerx, self.card_rect.top + 40))
            screen.blit(name_surface, name_rect)

            class_name_text = self.model.__class__.__name__
            class_name_surface = font.render(class_name_text, True, (0, 0, 0))
            hp_rect = class_name_surface.get_rect(center=(self.card_rect.centerx, self.card_rect.top + 82))
            screen.blit(class_name_surface, hp_rect)

            if hasattr(self.model, "hp"):
                hp_text = f"HP: {self.model.hp}"
                hp_surface = font.render(hp_text, True, (0, 0, 0))
                hp_rect = hp_surface.get_rect(center=(self.card_rect.centerx, self.card_rect.bottom - 42))
                screen.blit(hp_surface, hp_rect)

            if hasattr(self.model, "mana"):
                mana_text = f"MANA: {self.model.mana}"
                mana_surface = font.render(mana_text, True, (0, 0, 0))
                mana_rect = mana_surface.get_rect(center=(self.card_rect.centerx, self.card_rect.bottom - 25))
                screen.blit(mana_surface, mana_rect)

    def is_clicked(self, mouse_pos):
        return self.card_rect.collidepoint(mouse_pos)

class CharacterCard(Card):
    WIDTH = 200
    HEIGHT = 300
    PADDING = 12

class InventoryCard(Card):
    WIDTH = 80
    HEIGHT = 110
    PADDING = 8

    def __init__(self, card_image_path, asset_image_path, model, center_pos, font=None):
        super().__init__(card_image_path, None, model, center_pos, font)
        self.asset_image_path = asset_image_path
        self.item_image_path = None
        self.asset_image = None
        self.item_image = None
        self.asset_rect = None
        self.item_rect = None
        self.load_images()

    def load_images(self):
        if self.asset_image_path:
            raw_asset = pygame.image.load(self.asset_image_path).convert_alpha()
            self.asset_image = pygame.transform.smoothscale(raw_asset, (self.WIDTH, self.HEIGHT))
            self.asset_rect = self.asset_image.get_rect(center=self.card_rect.center)

        if self.item_image_path:
            raw_item = pygame.image.load(self.item_image_path).convert_alpha()
            self.item_image = pygame.transform.smoothscale(raw_item, (self.WIDTH, self.HEIGHT))
            self.item_rect = self.item_image.get_rect(center=self.card_rect.center)

    def draw(self, screen):
        if self.asset_image:
            screen.blit(self.asset_image, self.asset_rect)
        if self.item_image:
            screen.blit(self.item_image, self.item_rect)

class ProjectileSprite(pygame.sprite.Sprite):
    SIZE_X = 90
    SIZE_Y = 90

    def __init__(self, image_name: str, start_pos: tuple, target_sprite, speed: int):
        super().__init__()
        self.target_sprite = target_sprite
        self.image = pygame.image.load(f"../assets/projectile/{image_name}.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.SIZE_X, self.SIZE_Y))
        self.current_x, self.current_y = float(start_pos[0]), float(start_pos[1])

        tx, ty = target_sprite.rect.center
        dx = tx - self.current_x
        dy = ty - self.current_y
        dist = math.sqrt(dx ** 2 + dy ** 2)

        self.dir_x = dx / dist if dist != 0 else 0
        self.dir_y = dy / dist if dist != 0 else 0
        self.speed = speed

        angle = math.degrees(math.atan2(-self.dir_y, self.dir_x))
        self.image = pygame.transform.rotate(self.image, angle)

        self.rect = self.image.get_rect(center=(int(self.current_x), int(self.current_y)))

    def update(self, dt):
        self.current_x += self.dir_x * self.speed * dt
        self.current_y += self.dir_y * self.speed * dt

        self.rect.center = (int(self.current_x), int(self.current_y))

        if self.rect.colliderect(self.target_sprite.rect):
            self.kill()

class BaseSprite(pygame.sprite.Sprite):
    BAR_WIDTH = 60
    BAR_HEIGHT = 8
    BAR_PADDING = 10

    SIZE_X = 180
    SIZE_Y = 180

    ATTACK_DURATION = 1
    ATTACK_RANGE = 100

    WALK_INTERVAL = 0.2
    RETURN_INTERVAL = 1

    def __init__(self, model, coordinates: tuple[int, int], frames: dict):
        super().__init__()
        self.is_ranged_attack = False
        self.model = model
        self.SPEED = self.model.speed * 10
        self.state = SpriteState.IDLE
        self.target = None
        self.timer = 0
        self.walk_timer = 0
        self.reach_timer = 0
        self.return_timer = 0
        self.walk_toggle = False
        self.start_position = coordinates

        self.frames = {}
        for k, path in frames.items():
            image = pygame.image.load(path).convert_alpha()
            self.frames[k] = pygame.transform.scale(image, (self.SIZE_X, self.SIZE_Y))

        self.image = self.frames["idle"]
        self.rect = self.image.get_rect(midbottom=self.start_position)

    def start_attack(self, target, projectile_data=None, group=None):
        self.target = target
        self.state = SpriteState.MOVE_TO_TARGET
        self.timer = 0

        if projectile_data:
            self.is_ranged_attack = True
            self.launch_projectile(target, projectile_data['name'], projectile_data['speed'], group)
        else:
            self.is_ranged_attack = False

    def _move_to_target(self, delta_time):
        distance = self.target.rect.centerx - self.rect.centerx

        if abs(distance) > self.ATTACK_RANGE:
            direction = 1 if distance > 0 else -1
            self.rect.x += direction * self.SPEED * delta_time
            self.walk_timer += delta_time
            if self.walk_timer >= self.WALK_INTERVAL:
                self.walk_timer = 0
                self.walk_toggle = not self.walk_toggle
            self.image = self.frames["walk_1"] if self.walk_toggle else self.frames["walk_2"]
        else:
            self.state = SpriteState.ATTACK
            self.timer = 0
            self.image = self.frames["attack"]

    def launch_projectile(self, target_sprite, projectile_name, speed, group):
        start_pos = self.rect.center

        projectile = ProjectileSprite(
            image_name=projectile_name,
            start_pos=start_pos,
            target_sprite=target_sprite,
            speed=speed
        )

        self.image = self.frames["attack"]

        group.add(projectile)

    def _return_to_start(self, delta_time):
        self.return_timer += delta_time
        if self.return_timer >= self.RETURN_INTERVAL:
            self.rect.centerx = self.start_position[0]
            self.state = SpriteState.IDLE
            self.image = self.frames["idle"]
            self.return_timer = 0

    def draw_hp_bar(self, surface):
        ratio = self.model.hp / self.model.max_hp
        bar_x = self.rect.centerx - self.BAR_WIDTH // 2
        bar_y = self.rect.top - self.BAR_PADDING

        pygame.draw.rect(surface, (180, 0, 0), (bar_x, bar_y, self.BAR_WIDTH, self.BAR_HEIGHT))
        pygame.draw.rect(surface, (0, 200, 0),(bar_x, bar_y, int(self.BAR_WIDTH * ratio), self.BAR_HEIGHT))

    def _attack(self, delta_time):
        self.timer += delta_time
        if self.timer >= self.ATTACK_DURATION:
            if self.target and self.target.model.hp > 0:
                self.model.attack(self.target.model)

            self.target = None
            self.state = SpriteState.RETURN
            self.timer = 0

    def update(self, delta_time):
        if self.state == SpriteState.IDLE:
            self.image = self.frames["idle"]

        elif self.state == SpriteState.MOVE_TO_TARGET:
            if self.is_ranged_attack:
                self.state = SpriteState.ATTACK
            else:
                self._move_to_target(delta_time)

        elif self.state == SpriteState.ATTACK:
            self._attack(delta_time)

        elif self.state == SpriteState.RETURN:
            self._return_to_start(delta_time)
            self.is_ranged_attack = False





