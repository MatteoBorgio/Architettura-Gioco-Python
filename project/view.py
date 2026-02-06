import math
import os
import pygame
from enum import Enum
from project.assets_manager import AssetsManager
from project.game_state import GameState

PLAYER_START_POS = (200, 400)
ENEMY_START_POS = (600, 400)

class SpriteState(Enum):
    IDLE = "idle"
    MOVE_TO_TARGET = "move"
    ATTACK = "attack"
    RETURN = "return"

class Button:
    def __init__(self, pos, filename, scale):
        self.image = pygame.image.load(filename).convert_alpha()
        self.image = pygame.transform.scale(self.image, scale)
        self.rect = self.image.get_rect(center=pos)

        self.is_active = True
        self._pressed = False
        self.clicked = False

    def handle_event(self, event):
        if not self.is_active:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._pressed = True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._pressed and self.rect.collidepoint(event.pos):
                self.clicked = True
            self._pressed = False

    def update(self):
        self.clicked = False

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Card:
    WIDTH = 100
    HEIGHT = 150
    PADDING = 10

    def __init__(self, card_image_path: str, content_image_path: str | None, model, center_pos: tuple[float, float],
                 font=None):
        self.model = model
        self.font = font

        raw_card_image = pygame.image.load(card_image_path).convert_alpha()
        self.card_image = pygame.transform.smoothscale(raw_card_image, (self.WIDTH, self.HEIGHT))
        self.card_rect = self.card_image.get_rect(center=center_pos)

        self.content_image = None
        self.content_rect = None

        if content_image_path:
            raw_content_image = pygame.image.load(content_image_path).convert_alpha()
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
            self._draw_text_info(screen)

    def _draw_text_info(self, screen):
        font_small = pygame.font.Font(None, int(self.font.get_height() * 0.6))

        name_surface = self.font.render(self.model.name, True, (0, 0, 0))
        name_rect = name_surface.get_rect(center=(self.card_rect.centerx, self.card_rect.top + 40))
        screen.blit(name_surface, name_rect)

        class_name_text = self.model.__class__.__name__
        class_name_surface = font_small.render(class_name_text, True, (0, 0, 0))
        cls_rect = class_name_surface.get_rect(center=(self.card_rect.centerx, self.card_rect.top + 82))
        screen.blit(class_name_surface, cls_rect)

        if hasattr(self.model, "hp"):
            hp_surface = font_small.render(f"HP: {self.model.hp}", True, (0, 0, 0))
            screen.blit(hp_surface, hp_surface.get_rect(center=(self.card_rect.centerx, self.card_rect.bottom - 42)))

        if hasattr(self.model, "mana"):
            mana_surface = font_small.render(f"MANA: {self.model.mana}", True, (0, 0, 0))
            screen.blit(mana_surface,
                        mana_surface.get_rect(center=(self.card_rect.centerx, self.card_rect.bottom - 25)))

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
        self.load_images()

    def load_images(self):
        if self.asset_image_path:
            raw = pygame.image.load(self.asset_image_path).convert_alpha()
            self.asset_image = pygame.transform.smoothscale(raw, (self.WIDTH, self.HEIGHT))
            self.asset_rect = self.asset_image.get_rect(center=self.card_rect.center)

        if self.item_image_path:
            try:
                raw = pygame.image.load(self.item_image_path).convert_alpha()
                max_w, max_h = self.WIDTH - 10, self.HEIGHT - 10
                scale = min(max_w / raw.get_width(), max_h / raw.get_height())
                self.item_image = pygame.transform.smoothscale(raw, (
                int(raw.get_width() * scale), int(raw.get_height() * scale)))
                self.item_rect = self.item_image.get_rect(center=self.card_rect.center)
            except Exception as e:
                print(f"Error loading item image: {e}")
                self.item_image = None
        else:
            self.item_image = None

    def draw(self, screen):
        if self.asset_image: screen.blit(self.asset_image, self.asset_rect)
        if self.item_image: screen.blit(self.item_image, self.item_rect)


class EffectSprite(pygame.sprite.Sprite):
    SIZE_X = 100
    SIZE_Y = 100
    DURATION = 1.0

    def __init__(self, image_name: str, pos: tuple):
        super().__init__()
        path = AssetsManager.asset_path("..", "assets", "effect", f"{image_name}.png")
        self.image = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.SIZE_X, self.SIZE_Y))
        self.rect = self.image.get_rect(center=pos)
        self.timer = 0

    def update(self, dt):
        self.timer += dt
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

        path = AssetsManager.asset_path("..", "assets", "projectile", f"{image_name}.png")
        self.image = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.SIZE_X, self.SIZE_Y))

        self.current_x, self.current_y = float(start_pos[0]), float(start_pos[1])

        tx, ty = target_sprite.rect.center
        dx, dy = tx - self.current_x, ty - self.current_y
        dist = math.sqrt(dx ** 2 + dy ** 2)

        self.dir_x = dx / dist if dist != 0 else 0
        self.dir_y = dy / dist if dist != 0 else 0

        angle = math.degrees(math.atan2(-self.dir_y, self.dir_x))
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=(int(self.current_x), int(self.current_y)))

    def update(self, dt):
        self.current_x += self.dir_x * self.speed * dt
        self.current_y += self.dir_y * self.speed * dt
        self.rect.center = (int(self.current_x), int(self.current_y))

        if self.rect.colliderect(self.target_sprite.rect):
            self.on_impact()

    def on_impact(self):
        if self.effect_name:
            effect = EffectSprite(self.effect_name, self.target_sprite.rect.center)
            for group in self.groups():
                group.add(effect)
        self.kill()


class BaseSprite(pygame.sprite.Sprite):
    BAR_WIDTH = 60
    BAR_HEIGHT = 8
    SIZE_X = 180
    SIZE_Y = 180

    ATTACK_DURATION = 0.8
    WALK_INTERVAL = 0.2
    RETURN_INTERVAL = 1.0

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
            img = pygame.image.load(path).convert_alpha()
            self.frames[k] = pygame.transform.scale(img, (self.SIZE_X, self.SIZE_Y))

        self.image = self.frames["idle"]
        self.rect = self.image.get_rect(midbottom=self.start_position)

    def trigger_attack_animation(self, target_sprite, projectile_data=None, sprite_group=None):
        self.target = target_sprite
        self.timer = 0

        if projectile_data:
            self.is_ranged_attack = True
            self.state = SpriteState.ATTACK
            self._spawn_projectile(target_sprite, projectile_data, sprite_group)
        else:
            self.is_ranged_attack = False
            self.state = SpriteState.MOVE_TO_TARGET

    def _spawn_projectile(self, target, data, group):
        start_pos = self.rect.center
        projectile = ProjectileSprite(data['name'], start_pos, target, data['speed'], data['effect'])
        self.image = self.frames["attack"]
        if group:
            group.add(projectile)

    def draw_hp_bar(self, surface):
        if self.model.max_hp <= 0: return
        ratio = max(0, self.model.hp / self.model.max_hp)

        bx = self.rect.centerx - self.BAR_WIDTH // 2
        by = self.rect.top - 10

        pygame.draw.rect(surface, (180, 0, 0), (bx, by, self.BAR_WIDTH, self.BAR_HEIGHT))
        pygame.draw.rect(surface, (0, 200, 0), (bx, by, int(self.BAR_WIDTH * ratio), self.BAR_HEIGHT))

    def update(self, dt):
        if self.state == SpriteState.IDLE:
            self.image = self.frames["idle"]
        elif self.state == SpriteState.MOVE_TO_TARGET:
            self._update_movement(dt)
        elif self.state == SpriteState.ATTACK:
            self._update_attack(dt)
        elif self.state == SpriteState.RETURN:
            self._update_return(dt)

    def _update_movement(self, dt):
        attack_range = 80
        dist = self.target.rect.centerx - self.rect.centerx

        if abs(dist) > attack_range:
            direction = 1 if dist > 0 else -1
            self.rect.x += self.speed_pixel * dt * direction

            self.walk_timer += dt
            if self.walk_timer >= self.WALK_INTERVAL:
                self.walk_timer = 0
                self.walk_toggle = not self.walk_toggle
                self.image = self.frames["walk_1"] if self.walk_toggle else self.frames["walk_2"]
        else:
            self.state = SpriteState.ATTACK
            self.timer = 0
            self.image = self.frames["attack"]

    def _update_attack(self, dt):
        self.timer += dt
        if self.timer >= self.ATTACK_DURATION:
            if self.target and self.target.model.hp > 0:
                self.model.attack(self.target.model)

            self.target = None
            self.timer = 0

            if self.is_ranged_attack:
                self.state = SpriteState.IDLE
            else:
                self.state = SpriteState.RETURN
                self.return_timer = 0

    def _update_return(self, dt):
        self.return_timer += dt
        if self.return_timer >= self.RETURN_INTERVAL:
            self.rect.midbottom = self.start_position
            self.state = SpriteState.IDLE
            self.image = self.frames["idle"]
            self.return_timer = 0

class UIManager:
    NUMBER_OF_BACKGROUNDS = 9
    def __init__(self, width, height):
        pygame.init()
        self.WIDTH = width
        self.HEIGHT = height
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Code Combat")
        self.screen_rect = self.screen.get_rect()

        self.font = self._load_font()
        self.backgrounds = []
        self._load_backgrounds("bg")

        self.background = self.backgrounds[0]
        self.is_over = False
        self.bg_selection = self._load_background_image("menu_wooden_board.jpg")

        self.character_cards = []
        self.inventory_cards = []

        self.attack_button = Button((100, 530), AssetsManager.asset_path("..", "assets", "buttons", "attack.png"), (200, 200))
        self.special_ability_button = Button((700, 530), AssetsManager.asset_path("..", "assets", "buttons", "special.png"), (200, 200))

    def handle_ui_event(self, event):
        self.attack_button.handle_event(event)
        self.special_ability_button.handle_event(event)

    @staticmethod
    def _load_font():
        path = AssetsManager.asset_path("..", "assets", "font", "selection_font.ttf")
        return pygame.font.Font(path, 36) if os.path.exists(path) else pygame.font.SysFont("Arial", 36)

    def _load_background_image(self, filename, subfolder=None):
        if subfolder:
            path = AssetsManager.asset_path("..", "assets", subfolder, filename)
        else:
            path = AssetsManager.asset_path("..", "assets", filename)
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, (self.WIDTH, self.HEIGHT))

    def _load_backgrounds(self, subfolder=None):
        for i in range(self.NUMBER_OF_BACKGROUNDS):
            bg = self._load_background_image(
                f"sfondo_{i + 1}.png",
                subfolder=subfolder
            )
            self.backgrounds.append(bg)

    def refresh_background(self):
        if not self.backgrounds:
            self.is_over = True
            return
        self.background = self.backgrounds[0]
        self.backgrounds.remove(self.backgrounds[0])

    def create_character_selection_screen(self, characters):
        self.character_cards.clear()
        if not characters: return

        card_w = CharacterCard.WIDTH
        total_w = len(characters) * card_w
        start_x = self.screen_rect.centerx - total_w / 2 + card_w / 2
        center_y = self.screen_rect.centery + 50

        bg_board = AssetsManager.asset_path("..", "assets", "wooden_board.png")

        for i, char in enumerate(characters):
            pos = (start_x + i * card_w, center_y)
            folder = char.__class__.__name__.lower()
            char_img = AssetsManager.asset_path("..", "assets", folder, f"{folder}_1.png")

            self.character_cards.append(CharacterCard(bg_board, char_img, char, pos, self.font))

    def create_battle_interface(self):
        self.inventory_cards.clear()
        card_w, card_h = InventoryCard.WIDTH, InventoryCard.HEIGHT
        num_cards = 5

        total_w = num_cards * card_w
        start_x = self.screen_rect.centerx - total_w / 2 + card_w / 2
        center_y = self.screen_rect.bottom - card_h / 2 - 10
        bg_path = AssetsManager.asset_path("..", "assets", "wooden_board.png")

        for i in range(num_cards):
            pos = (start_x + i * card_w, center_y)
            card = InventoryCard(bg_path, bg_path, None, pos, self.font)
            card.item_image_path = None
            card.load_images()
            self.inventory_cards.append(card)

    def update_inventory(self, hero):
        keys = list(hero.equipment.keys())
        slots = keys + [None] * (5 - len(keys))

        for i, card in enumerate(self.inventory_cards):
            if i >= len(slots): break
            slot = slots[i]
            item = hero.equipment.get(slot) if slot else None

            card.model = item
            card.asset_image_path = AssetsManager.asset_path("..", "assets", "wooden_board.png")

            if item:
                folder = "weapon" if slot == "weapon" else "armor"
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
        txt = self.font.render("SELECT YOUR CHARACTER:", True, (0, 0, 0))
        self.screen.blit(txt, txt.get_rect(center=(self.screen_rect.centerx, self.screen_rect.centery - 150)))
        for card in self.character_cards:
            card.draw(self.screen)

    def update(self):
        self.attack_button.update()
        self.special_ability_button.update()

    def _draw_battle_scene(self, all_sprites, hero, enemy):
        if self.background:
            self.screen.blit(self.background, (0, 0))
            self.attack_button.draw(self.screen)
            self.special_ability_button.draw(self.screen)

            if all_sprites:
                all_sprites.draw(self.screen)

            if hero:
                hero.draw_hp_bar(self.screen)

            if enemy:
                enemy.draw_hp_bar(self.screen)

            for card in self.inventory_cards:
                card.draw(self.screen)