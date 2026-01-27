import os
import sys
import pygame
import json

from project.items import Weapon

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from project.characters import Warrior, Cleric, Thief, Wizard
from project.datatypes import Stats, Buff
from project.monsters import Goblin
from project.view import BaseSprite, SpriteState, CharacterCard, InventoryCard
from game_state import GameState


class GameController:

    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Combattimento a turni")
        self.clock = pygame.time.Clock()

        self.running = True
        self.game_state = GameState.CHARACTER_SELECT
        self.selected_hero = None
        self.all_sprites = pygame.sprite.Group()
        self.turn = "player"
        self.enemy_attack_timer = 0
        self.player_has_attacked = False
        self.inventory_changed = True

        self.font_path = self.asset_path("..", "assets", "font", "selection_font.ttf")
        self.selection_font = pygame.font.Font(self.font_path, 36)

        self.bg = pygame.image.load(self.asset_path("..", "assets", "background.jpg")).convert()
        self.bg = pygame.transform.scale(self.bg, (self.WIDTH, self.HEIGHT))

        self.bg_selection = pygame.image.load(
            self.asset_path("..", "assets", "menu_wooden_board.jpg")
        ).convert()
        self.bg_selection = pygame.transform.scale(self.bg_selection, (self.WIDTH, self.HEIGHT))

        self.screen_rect = self.screen.get_rect()
        self.card_center_y = self.screen_rect.centery + 50

        self.load_data()
        self.create_cards()
        self.create_enemy()

    @staticmethod
    def asset_path(*args):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, *args)

    def calculate_characters_card_positions(self, num_cards, card_width):
        total_width = num_cards * card_width
        start_x = self.screen_rect.centerx - total_width / 2 + card_width / 2
        return [(start_x + i * card_width, self.card_center_y) for i in range(num_cards)]

    def calculate_inventory_card_positions(self, card_width, card_height, bottom_margin=0, num_cards=5):
        total_width = num_cards * card_width
        start_x = self.screen_rect.centerx - total_width / 2 + card_width / 2
        center_y = self.screen_rect.bottom - bottom_margin - card_height / 2
        return [(start_x + i * card_width, center_y) for i in range(num_cards)]

    @staticmethod
    def create_character(data):
        base_stats = Stats(
            strength=data.get("strength", 0),
            dexterity=data.get("dexterity", 0),
            intelligence=data.get("intelligence", 0),
            defense=data.get("defense", 0)
        )

        sa = data.get("special_ability", {})
        special_ability = Buff(
            name=sa.get("name", ""),
            stat=sa.get("stat", ""),
            amount=sa.get("amount", 0),
            duration=sa.get("duration", 0)
        )

        cls_map = {"Warrior": Warrior, "Cleric": Cleric, "Thief": Thief, "Wizard": Wizard}
        cls = cls_map.get(data["class"])

        kwargs = {
            "name": data["name"],
            "hp": data["hp"],
            "base_stats": base_stats,
            "equipment": {"weapon": None, "armor": None},
            "mana": data.get("mana", 0),
            "mana_per_attack": data.get("mana_per_attack", 0),
            "special_ability": special_ability,
            "speed": data.get("speed", 10),
            "potions_set": data["potions_set"]
        }

        if cls is Warrior:
            kwargs["shield"] = data.get("shield", 0)
        elif cls is Cleric:
            kwargs["healing_per_attack"] = data.get("healing_per_attack", 0)
            kwargs["poisons_mitigation"] = data.get("poison_mitigation", 0)
        elif cls is Thief:
            kwargs["critical_bonus"] = data.get("critical_bonus", 0)
        elif cls is Wizard:
            kwargs["buff_amount_boost"] = data.get("buff_amount_boost", 0)
            kwargs["buff_duration_boost"] = data.get("buff_duration_boost", 0)

        return cls(**kwargs)

    @staticmethod
    def create_weapon(data):
        base_stats = Stats(
            strength=data.get("strength", 0),
            dexterity=data.get("dexterity", 0),
            intelligence=data.get("intelligence", 0),
            defense=data.get("defense", 0)
        )
        return Weapon(
            name=data["name"],
            weight=int(data["weight"]),
            bonus_stats=base_stats,
            damage_range=(data["damage_range_min"], data["damage_range_max"]),
            weapon_type=data["weapon_type"],
            slot=data["slot"]
        )

    def load_data(self):
        with open(self.asset_path("..", "data", "characters.json")) as f:
            characters_data = json.load(f)
        self.characters = [self.create_character(d) for d in characters_data]

        with open(self.asset_path("..", "data", "weapons.json")) as f:
            weapons_data = json.load(f)
        self.weapons = [self.create_weapon(d) for d in weapons_data]

        for char in self.characters:
            if isinstance(char, Warrior):
                for w in self.weapons:
                    if w.name == "Long Sword":
                        char.equipment["weapon"] = w
                        break
            if isinstance(char, Thief):
                for w in self.weapons:
                    if w.name == "Dagger":
                        char.equipment["weapon"] = w
                        break
            if isinstance(char, Cleric):
                for w in self.weapons:
                    if w.name == "Holy Spear":
                        char.equipment["weapon"] = w
                        break
            if isinstance(char, Wizard):
                for w in self.weapons:
                    if w.name == "Scepter":
                        char.equipment["weapon"] = w
                        break

    def create_cards(self):
        positions = self.calculate_characters_card_positions(
            len(self.characters), CharacterCard.WIDTH
        )

        self.characters_cards = [
            CharacterCard(
                self.asset_path("..", "assets", "wooden_board.png"),
                self.asset_path("..", "assets", char.__class__.__name__.lower(), f"{char.__class__.__name__.lower()}_1.png"),
                char,
                positions[i],
                self.selection_font
            ) for i, char in enumerate(self.characters)
        ]

        self.inventory_cards_positions = self.calculate_inventory_card_positions(
            InventoryCard.WIDTH, InventoryCard.HEIGHT
        )

        self.inventory_cards = [
            InventoryCard(
                self.asset_path("..", "assets", "wooden_board.png"),
                None,
                None,
                self.inventory_cards_positions[i],
                self.selection_font
            )
            for i in range(5)
        ]

    def create_enemy(self):
        self.goblin_model = Goblin(
            name="Goblin",
            hp=50,
            base_damage=8,
            bonus_damage=4,
            equipment={},
            buff_stole_per_turn=1,
            level=1,
            speed=20
        )

        self.enemy_sprite = BaseSprite(
            self.goblin_model,
            (600, 500),
            frames={
                "idle": self.asset_path("..", "assets", "goblin", "goblin_1.png"),
                "walk_1": self.asset_path("..", "assets", "goblin", "goblin_2.png"),
                "walk_2": self.asset_path("..", "assets", "goblin", "goblin_3.png"),
                "attack": self.asset_path("..", "assets", "goblin", "goblin_4.png")
            }
        )

    def get_frames_for_character(self, char):
        folder = char.__class__.__name__.lower()
        return {
            "idle": self.asset_path("..", "assets", folder, f"{folder}_1.png"),
            "walk_1": self.asset_path("..", "assets", folder, f"{folder}_2.png"),
            "walk_2": self.asset_path("..", "assets", folder, f"{folder}_3.png"),
            "attack": self.asset_path("..", "assets", folder, f"{folder}_4.png")
        }

    def update_inventory_cards(self):
        for i, slot in enumerate(list(self.selected_hero.equipment.keys()) + [None]*5):
            if i >= len(self.inventory_cards):
                break
            card = self.inventory_cards[i]
            card.card_rect.center = self.inventory_cards_positions[i]
            if slot is None or self.selected_hero.equipment.get(slot) is None:
                card.model = None
                card.asset_image_path = self.asset_path("..", "assets", "wooden_board.png")
                card.item_image_path = None
            else:
                item = self.selected_hero.equipment[slot]
                card.model = item
                card.asset_image_path = self.asset_path("..", "assets", "wooden_board.png")
                if slot == "weapon":
                    card.item_image_path = self.asset_path("..", "assets", "weapon", f"{item.name}.png")
                elif slot == "armor":
                    card.item_image_path = self.asset_path("..", "assets", "armor", f"{item.name}.png")
            card.load_images()

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000
            self.handle_events()
            self.update(dt)
            self.render()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.game_state == GameState.CHARACTER_SELECT and event.type == pygame.MOUSEBUTTONDOWN:
                for character_card in self.characters_cards:
                    if character_card.is_clicked(event.pos):
                        self.selected_hero = character_card.model
                        frames = self.get_frames_for_character(self.selected_hero)
                        self.hero_sprite = BaseSprite(self.selected_hero, (200, 490), frames)
                        self.all_sprites = pygame.sprite.Group(self.hero_sprite, self.enemy_sprite)
                        self.game_state = GameState.BATTLE_MODE
                        self.turn = "player"
                        self.player_has_attacked = False
                        self.enemy_attack_timer = 0
                        self.inventory_changed = True

            elif self.game_state == GameState.BATTLE_MODE and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if (self.turn == "player"
                        and self.hero_sprite.model.hp > 0
                        and self.goblin_model.hp > 0
                        and not self.player_has_attacked):
                        self.hero_sprite.start_attack(self.enemy_sprite)
                        self.player_has_attacked = True

    # ---------- LOGICA ----------
    def update(self, dt):
        if self.game_state == GameState.BATTLE_MODE:
            if self.turn == "player":
                self.hero_sprite.update(dt)
                if self.player_has_attacked and self.hero_sprite.state == SpriteState.IDLE and self.hero_sprite.target is None:
                    self.turn = "enemy"
                    self.player_has_attacked = False

            elif self.turn == "enemy":
                self.enemy_sprite.update(dt)
                if not hasattr(self.enemy_sprite, 'has_attacked'):
                    self.enemy_sprite.has_attacked = False
                if not self.enemy_sprite.has_attacked and self.enemy_sprite.state == SpriteState.IDLE and self.enemy_sprite.target is None:
                    self.enemy_attack_timer += dt
                    if self.enemy_attack_timer >= 2:
                        self.enemy_sprite.start_attack(self.hero_sprite)
                        self.enemy_sprite.has_attacked = True
                        self.enemy_attack_timer = 0
                if self.enemy_sprite.state == SpriteState.IDLE and self.enemy_sprite.target is None and self.enemy_sprite.has_attacked:
                    self.turn = "player"
                    self.enemy_sprite.has_attacked = False

            if self.hero_sprite.model.hp <= 0 or self.goblin_model.hp <= 0:
                self.running = False

    # ---------- RENDER ----------
    def render(self):
        if self.game_state == GameState.CHARACTER_SELECT:
            self.screen.blit(self.bg_selection, (0, 0))
            text_surface = self.selection_font.render("SELECT YOUR CHARACTER:", True, (0, 0, 0))
            text_rect = text_surface.get_rect(
                center=(self.screen_rect.centerx, self.screen_rect.centery - 150)
            )
            self.screen.blit(text_surface, text_rect)
            for card in self.characters_cards:
                card.draw(self.screen)

        elif self.game_state == GameState.BATTLE_MODE:
            self.screen.blit(self.bg, (0, 0))
            self.all_sprites.draw(self.screen)
            self.hero_sprite.draw_hp_bar(self.screen)
            self.enemy_sprite.draw_hp_bar(self.screen)
            if self.inventory_changed:
                self.update_inventory_cards()
                self.inventory_changed = False
            for card in self.inventory_cards:
                card.draw(self.screen)

        pygame.display.flip()

if __name__ == "__main__":
    controller = GameController()
    controller.run()