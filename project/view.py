import math
import os
import pygame
from enum import Enum
from project.assets_manager import AssetsManager
from project.game_state import GameState


class SpriteState(Enum):
    IDLE = "idle"
    MOVE_TO_TARGET = "move"
    ATTACK = "attack"
    RETURN = "return"


class Card:
    WIDTH = 100
    HEIGHT = 150
    PADDING = 10

    def __init__(self, card_image_path: str, content_image_path: str | None, model, center_pos: tuple[int, int],
                 font=None):
        self.model = model
        self.font = font

        raw_card_image = pygame.image.load(card_image_path).convert_alpha()
        self.card_image = pygame.transform.smoothscale(raw_card_image, (self.WIDTH, self.HEIGHT))
        self.card_rect = self.card_image.get_rect(center=center_pos)

        self.content_image_path = content_image_path
        self.content_image = None
        self.content_rect = None

        if self.content_image_path:
            raw_content_image = pygame.image.load(self.content_image_path).convert_alpha()
            max_width = self.WIDTH - self.PADDING * 2
            max_height = self.HEIGHT - self.PADDING * 2
            scale = min(max_width / raw_content_image.get_width(), max_height / raw_content_image.get_height())
            new_size = (int(raw_content_image.get_width() * scale), int(raw_content_image.get_height() * scale))

            self.content_image = pygame.transform.smoothscale(raw_content_image, new_size)
            self.content_rect = self.content_image.get_rect(center=self.card_rect.center)

    def draw(self, screen):
        screen.blit(self.card_image, self.card_rect)
        if self.content_image:
            screen.blit(self.content_image, self.content_rect)

        if self.font and self.model:
            font_small = pygame.font.Font(None, int(self.font.get_height() * 0.6))

            name_surface = self.font.render(self.model.name, True, (0, 0, 0))
            name_rect = name_surface.get_rect(center=(self.card_rect.centerx, self.card_rect.top + 40))
            screen.blit(name_surface, name_rect)

            class_name_text = self.model.__class__.__name__
            class_name_surface = font_small.render(class_name_text, True, (0, 0, 0))
            cls_rect = class_name_surface.get_rect(center=(self.card_rect.centerx, self.card_rect.top + 82))
            screen.blit(class_name_surface, cls_rect)

            if hasattr(self.model, "hp"):
                hp_text = f"HP: {self.model.hp}"
                hp_surface = font_small.render(hp_text, True, (0, 0, 0))
                hp_rect = hp_surface.get_rect(center=(self.card_rect.centerx, self.card_rect.bottom - 42))
                screen.blit(hp_surface, hp_rect)

            if hasattr(self.model, "mana"):
                mana_text = f"MANA: {self.model.mana}"
                mana_surface = font_small.render(mana_text, True, (0, 0, 0))
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
            try:
                raw_item = pygame.image.load(self.item_image_path).convert_alpha()
                max_w, max_h = self.WIDTH - 10, self.HEIGHT - 10
                scale = min(max_w / raw_item.get_width(), max_h / raw_item.get_height())
                new_size = (int(raw_item.get_width() * scale), int(raw_item.get_height() * scale))

                self.item_image = pygame.transform.smoothscale(raw_item, new_size)
                self.item_rect = self.item_image.get_rect(center=self.card_rect.center)
            except Exception as e:
                print(f"Error loading item image: {e}")
                self.item_image = None
        else:
            self.item_image = None

    def draw(self, screen):
        if self.asset_image:
            screen.blit(self.asset_image, self.asset_rect)
        if self.item_image:
            screen.blit(self.item_image, self.item_rect)


class EffectSprite(pygame.sprite.Sprite):
    SIZE_X = 100
    SIZE_Y = 100
    DURATION = 1.0

    def __init__(self, image_name: str, pos: tuple):
        super().__init__()
        image_path = AssetsManager.asset_path("..", "assets", "effect", f"{image_name}.png")
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.SIZE_X, self.SIZE_Y))
        self.rect = self.image.get_rect(center=pos)
        self.timer = 0

    def update(self, delta_time):
        self.timer += delta_time
        if self.timer > self.DURATION:
            self.kill()


class ProjectileSprite(pygame.sprite.Sprite):
    SIZE_X = 60
    SIZE_Y = 60

    def __init__(self, image_name: str, start_pos: tuple, target_sprite, speed: int, effect_name: str):
        super().__init__()
        self.target_sprite = target_sprite
        self.effect_name = effect_name
        self.speed = speed

        image_path = AssetsManager.asset_path("..", "assets", "projectile", f"{image_name}.png")
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.SIZE_X, self.SIZE_Y))

        self.current_x, self.current_y = float(start_pos[0]), float(start_pos[1])

        tx, ty = target_sprite.rect.center
        dx = tx - self.current_x
        dy = ty - self.current_y
        dist = math.sqrt(dx ** 2 + dy ** 2)

        self.dir_x = dx / dist if dist != 0 else 0
        self.dir_y = dy / dist if dist != 0 else 0

        angle = math.degrees(math.atan2(-self.dir_y, self.dir_x))
        self.image = pygame.transform.rotate(self.image, angle)

        self.rect = self.image.get_rect(center=(int(self.current_x), int(self.current_y)))

    def on_impact(self):
        if self.effect_name:
            effect = EffectSprite(self.effect_name, self.target_sprite.rect.center)
            for group in self.groups():
                group.add(effect)
        self.kill()

    def update(self, dt):
        self.current_x += self.dir_x * self.speed * dt
        self.current_y += self.dir_y * self.speed * dt
        self.rect.center = (int(self.current_x), int(self.current_y))

        if self.rect.colliderect(self.target_sprite.rect):
            self.on_impact()


class BaseSprite(pygame.sprite.Sprite):
    BAR_WIDTH = 60
    BAR_HEIGHT = 8
    BAR_PADDING = 10
    SIZE_X = 180
    SIZE_Y = 180

    ATTACK_DURATION = 0.8
    WALK_INTERVAL = 0.2
    RETURN_INTERVAL = 1.0
    SPEED_MULTIPLIER = 150

    def __init__(self, model, coordinates: tuple[int, int], frames: dict):
        super().__init__()

        if model.name == "Troll":
            self.SIZE_X = int(self.SIZE_X * 1.5)
            self.SIZE_Y = int(self.SIZE_Y * 1.5)

        self.model = model
        self.speed_pixel = model.speed * 20
        self.is_ranged_attack = False

        self.state = SpriteState.IDLE
        self.target = None
        self.timer = 0
        self.walk_timer = 0
        self.return_timer = 0
        self.walk_toggle = False

        self.start_position = coordinates

        self.frames = {}
        for k, path in frames.items():
            image = pygame.image.load(path).convert_alpha()
            self.frames[k] = pygame.transform.scale(image, (self.SIZE_X, self.SIZE_Y))

        self.image = self.frames["idle"]
        self.rect = self.image.get_rect(midbottom=self.start_position)

    def start_attack(self, target, effect_name=None, projectile_data=None, group=None):
        self.target = target
        self.timer = 0

        if projectile_data:
            self.is_ranged_attack = True
            self.state = SpriteState.ATTACK
            self.launch_projectile(target, projectile_data['name'], projectile_data['speed'], group, effect_name)
        else:
            self.is_ranged_attack = False
            self.state = SpriteState.MOVE_TO_TARGET

    def launch_projectile(self, target_sprite, projectile_name, speed, group, effect_name):
        start_pos = self.rect.center
        projectile = ProjectileSprite(projectile_name, start_pos, target_sprite, speed, effect_name)
        self.image = self.frames["attack"]
        if group:
            group.add(projectile)

    def draw_hp_bar(self, surface):
        if self.model.max_hp <= 0: return
        ratio = max(0, self.model.hp / self.model.max_hp)

        bar_x = self.rect.centerx - self.BAR_WIDTH // 2
        bar_y = self.rect.top - self.BAR_PADDING

        pygame.draw.rect(surface, (180, 0, 0), (bar_x, bar_y, self.BAR_WIDTH, self.BAR_HEIGHT))
        pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, int(self.BAR_WIDTH * ratio), self.BAR_HEIGHT))

    def update(self, delta_time):
        if self.state == SpriteState.IDLE:
            self.image = self.frames["idle"]

        elif self.state == SpriteState.MOVE_TO_TARGET:
            self._move_to_target(delta_time)

        elif self.state == SpriteState.ATTACK:
            self._attack_logic(delta_time)

        elif self.state == SpriteState.RETURN:
            self._return_to_start(delta_time)

    def _move_to_target(self, dt):
        attack_range = 80
        target_x = self.target.rect.centerx
        my_x = self.rect.centerx
        dist = target_x - my_x

        if abs(dist) > attack_range:
            direction = 1 if dist > 0 else -1
            move_amount = self.speed_pixel * dt * direction
            self.rect.x += move_amount

            self.walk_timer += dt
            if self.walk_timer >= self.WALK_INTERVAL:
                self.walk_timer = 0
                self.walk_toggle = not self.walk_toggle
                self.image = self.frames["walk_1"] if self.walk_toggle else self.frames["walk_2"]
        else:
            self.state = SpriteState.ATTACK
            self.timer = 0
            self.image = self.frames["attack"]

    def _attack_logic(self, dt):
        self.timer += dt
        if self.timer >= self.ATTACK_DURATION:
            if self.target and self.target.model.hp > 0:
                # Ripristinato: infligge sempre danno al termine dell'animazione
                # anche se è un attacco a distanza.
                self.model.attack(self.target.model)

            self.target = None
            self.timer = 0

            if self.is_ranged_attack:
                self.state = SpriteState.IDLE
            else:
                self.state = SpriteState.RETURN
                self.return_timer = 0

    def _return_to_start(self, dt):
        self.return_timer += dt
        if self.return_timer >= self.RETURN_INTERVAL:
            self.rect.midbottom = self.start_position
            self.state = SpriteState.IDLE
            self.image = self.frames["idle"]
            self.return_timer = 0


class UIManager:
    def __init__(self, width, height):
        pygame.init()
        self.WIDTH = width
        self.HEIGHT = height
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Code Combat")

        self.screen_rect = self.screen.get_rect()
        self.card_center_y = self.screen_rect.centery + 50

        self.font_path = AssetsManager.asset_path("..", "assets", "font", "selection_font.ttf")
        if os.path.exists(self.font_path):
            self.font = pygame.font.Font(self.font_path, 36)
        else:
            self.font = pygame.font.SysFont("Arial", 36)

        self.bg_battle = pygame.image.load(AssetsManager.asset_path("..", "assets", "background.jpg")).convert()
        self.bg_battle = pygame.transform.scale(self.bg_battle, (self.WIDTH, self.HEIGHT))

        self.bg_selection = pygame.image.load(
            AssetsManager.asset_path("..", "assets", "menu_wooden_board.jpg")
        ).convert()
        self.bg_selection = pygame.transform.scale(self.bg_selection, (self.WIDTH, self.HEIGHT))

        self.character_cards = []
        self.inventory_cards = []

    def create_character_selection_screen(self, characters):
        self.character_cards.clear()
        num_cards = len(characters)
        if num_cards == 0: return

        card_width = CharacterCard.WIDTH
        total_width = num_cards * card_width
        start_x = self.screen_rect.centerx - total_width / 2 + card_width / 2

        for i, char in enumerate(characters):
            pos = (start_x + i * card_width, self.card_center_y)
            folder = char.__class__.__name__.lower()
            char_image_path = AssetsManager.asset_path("..", "assets", folder, f"{folder}_1.png")
            bg_image_path = AssetsManager.asset_path("..", "assets", "wooden_board.png")

            card = CharacterCard(bg_image_path, char_image_path, char, pos, self.font)
            self.character_cards.append(card)

    def create_battle_interface(self):
        self.inventory_cards.clear()
        num_cards = 5
        card_width = InventoryCard.WIDTH
        card_height = InventoryCard.HEIGHT

        total_width = num_cards * card_width
        start_x = self.screen_rect.centerx - total_width / 2 + card_width / 2
        center_y = self.screen_rect.bottom - card_height / 2 - 10

        bg_path = AssetsManager.asset_path("..", "assets", "wooden_board.png")

        for i in range(num_cards):
            pos = (start_x + i * card_width, center_y)
            card = InventoryCard(bg_path, bg_path, None, pos, self.font)
            card.item_image_path = None
            card.load_images()
            self.inventory_cards.append(card)

    def update_inventory(self, hero):
        equipment_keys = list(hero.equipment.keys())
        slots = equipment_keys + [None] * (5 - len(equipment_keys))

        for i, card in enumerate(self.inventory_cards):
            if i >= len(slots):
                break

            slot_name = slots[i]
            item = hero.equipment.get(slot_name) if slot_name else None

            card.model = item
            card.asset_image_path = AssetsManager.asset_path("..", "assets", "wooden_board.png")

            if item:
                folder = "weapon" if slot_name == "weapon" else "armor"
                card.item_image_path = AssetsManager.asset_path("..", "assets", folder, f"{item.name}.png")
            else:
                card.item_image_path = None

            card.load_images()

    def handle_selection_click(self, mouse_pos):
        for card in self.character_cards:
            if card.is_clicked(mouse_pos):
                return card.model
        return None

    def render_game(self, game_state, all_sprites=None, hero=None, enemy=None):
        if game_state == GameState.CHARACTER_SELECT:
            self._draw_character_selection_scene()

        elif game_state == GameState.BATTLE_MODE:
            self._draw_battle_scene(all_sprites, hero, enemy)

        pygame.display.flip()

    def _draw_character_selection_scene(self):
        self.screen.blit(self.bg_selection, (0, 0))

        text_surface = self.font.render("SELECT YOUR CHARACTER:", True, (0, 0, 0))
        text_rect = text_surface.get_rect(
            center=(self.screen_rect.centerx, self.screen_rect.centery - 150)
        )
        self.screen.blit(text_surface, text_rect)

        for card in self.character_cards:
            card.draw(self.screen)

    def _draw_battle_scene(self, all_sprites, hero, enemy):
        self.screen.blit(self.bg_battle, (0, 0))

        if all_sprites:
            all_sprites.draw(self.screen)

        if hero:
            hero.draw_hp_bar(self.screen)
        if enemy:
            enemy.draw_hp_bar(self.screen)

        for card in self.inventory_cards:
            card.draw(self.screen)