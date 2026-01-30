from random import randint
import pygame

from project.view import BaseSprite, SpriteState, ProjectileSprite, UIManager
from project.game_state import GameState
from project.assets_manager import AssetsManager
from project.data_manager import DataManager

class GameController:
    def __init__(self):
        WIDTH, HEIGHT = 800, 600
        self.clock = pygame.time.Clock()
        self.running = True

        self.ui = UIManager(WIDTH, HEIGHT)

        self.game_state = GameState.CHARACTER_SELECT
        self.turn = "player"
        self.enemy_attack_timer = 0
        self.player_has_attacked = False
        self.inventory_changed = True

        self.selected_hero = None
        self.all_sprites = pygame.sprite.Group()
        self.projectiles_data = []
        self.characters = []
        self.monsters = []
        self.weapons = []

        self.load_resources()
        self.ui.create_character_selection_screen(self.characters)
        self.ui.create_battle_interface()

    def load_resources(self):
        chars, weapons, projs, monsters = DataManager.load_data()
        self.characters = chars
        self.weapons = weapons
        self.projectiles_data = projs
        self.monsters = monsters

    def create_enemy(self, model, frames):
        self.enemy_sprite = BaseSprite(model, (600, 500), frames)

    def choose_enemy(self):
        idx = randint(0, 1)
        monster_model = self.monsters[idx] if idx < len(self.monsters) else self.monsters[0]
        frames = self.get_frames_for_character(monster_model)
        self.create_enemy(monster_model, frames)

    def get_frames_for_character(self, char):
        folder = char.__class__.__name__.lower()
        return {
            "idle": AssetsManager.asset_path("..", "assets", folder, f"{folder}_1.png"),
            "walk_1": AssetsManager.asset_path("..", "assets", folder, f"{folder}_2.png"),
            "walk_2": AssetsManager.asset_path("..", "assets", folder, f"{folder}_3.png"),
            "attack": AssetsManager.asset_path("..", "assets", folder, f"{folder}_4.png")
        }

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.game_state == GameState.CHARACTER_SELECT and event.type == pygame.MOUSEBUTTONDOWN:
                selected_model = self.ui.handle_selection_click(event.pos)

                if selected_model:
                    self.selected_hero = selected_model
                    self.choose_enemy()

                    frames = self.get_frames_for_character(self.selected_hero)
                    self.hero_sprite = BaseSprite(self.selected_hero, (200, 490), frames)

                    self.all_sprites = pygame.sprite.Group(self.hero_sprite, self.enemy_sprite)
                    self.game_state = GameState.BATTLE_MODE

                    self.turn = "player"
                    self.player_has_attacked = False
                    self.enemy_attack_timer = 0

                    self.ui.update_inventory(self.selected_hero)
                    self.inventory_changed = False

            elif self.game_state == GameState.BATTLE_MODE and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.turn == "player" and not self.player_has_attacked:
                        self.perform_player_attack()

    def perform_player_attack(self):
        weapon = self.selected_hero.equipment.get("weapon")
        proj_info = None

        if weapon and weapon.weapon_type == "ranged":
            for p in self.projectiles_data:
                if p["weapon"] == weapon.name:
                    proj_info = {
                        "name": p["projectile_type"],
                        "speed": p["speed"],
                        "effect": p["effect"]
                    }
                    break

        self.hero_sprite.start_attack(
            self.enemy_sprite,
            projectile_data=proj_info,
            group=self.all_sprites,
            effect_name=proj_info["effect"] if proj_info else None
        )
        self.player_has_attacked = True

    def update(self, dt):
        if self.game_state == GameState.BATTLE_MODE:
            self.all_sprites.update(dt)

            if self.turn == "player":
                projectiles_in_flight = any(isinstance(s, ProjectileSprite) for s in self.all_sprites)
                if self.player_has_attacked and not projectiles_in_flight:
                    if self.hero_sprite.state == SpriteState.IDLE:
                        self.turn = "enemy"
                        self.player_has_attacked = False
                        self.enemy_attack_timer = 0

            elif self.turn == "enemy":
                self.handle_enemy_turn(dt)

            if self.hero_sprite.model.hp <= 0 or self.enemy_sprite.model.hp <= 0:
                self.running = False

            if self.inventory_changed:
                self.ui.update_inventory(self.selected_hero)
                self.inventory_changed = False

    def handle_enemy_turn(self, dt):
        if not hasattr(self.enemy_sprite, 'has_attacked'):
            self.enemy_sprite.has_attacked = False

        if not self.enemy_sprite.has_attacked:
            self.enemy_attack_timer += dt
            if self.enemy_attack_timer >= 1.5:
                self.enemy_sprite.start_attack(self.hero_sprite)
                self.enemy_sprite.has_attacked = True

        if self.enemy_sprite.has_attacked and self.enemy_sprite.state == SpriteState.IDLE:
            self.turn = "player"
            self.enemy_sprite.has_attacked = False

    def render(self):
        if self.game_state == GameState.BATTLE_MODE:
            self.ui.render_game(
                self.game_state,
                all_sprites=self.all_sprites,
                hero=self.hero_sprite,
                enemy=self.enemy_sprite
            )
        else:
            self.ui.render_game(self.game_state)

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000
            self.handle_events()
            self.update(dt)
            self.render()
        pygame.quit()


if __name__ == "__main__":
    controller = GameController()
    controller.run()