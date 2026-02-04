import pygame

from project.view import BaseSprite, SpriteState, ProjectileSprite, UIManager, PLAYER_START_POS, ENEMY_START_POS
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

        self.enemy_wait_timer = 0
        self.player_action_performed = False
        self.enemy_action_performed = False

        self.waiting_for_respawn = False
        self.respawn_timer = 0

        self.inventory_changed = True
        self.selected_hero = None
        self.all_sprites = pygame.sprite.Group()

        self.characters = []
        self.weapons = []

        self.load_resources()
        self.ui.create_character_selection_screen(self.characters)
        self.ui.create_battle_interface()

    def load_resources(self):
        chars_objs, weapons_objs = DataManager.load_data()
        self.characters = chars_objs
        self.weapons = weapons_objs

    def _get_frames(self, model):
        return AssetsManager.get_frames_for_character(model)

    def start_battle(self, selected_hero_model):
        self.selected_hero = selected_hero_model

        hero_frames = self._get_frames(self.selected_hero)
        self.hero_sprite = BaseSprite(self.selected_hero, PLAYER_START_POS, hero_frames)

        self.pick_new_enemy()

        self.all_sprites = pygame.sprite.Group(self.hero_sprite, self.enemy_sprite)

        self.game_state = GameState.BATTLE_MODE
        self.turn = "player"
        self.player_action_performed = False
        self.enemy_action_performed = False
        self.waiting_for_respawn = False

        self.ui.update_inventory(self.selected_hero)
        self.inventory_changed = False

    def pick_new_enemy(self):
        monster_model = DataManager.get_random_monster()
        frames = self._get_frames(monster_model)
        self.enemy_sprite = BaseSprite(monster_model, ENEMY_START_POS, frames)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.game_state == GameState.CHARACTER_SELECT and event.type == pygame.MOUSEBUTTONDOWN:
                selected_model = self.ui.handle_selection_click(event.pos)
                if selected_model:
                    self.start_battle(selected_model)

            elif self.game_state == GameState.BATTLE_MODE and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.waiting_for_respawn:
                    if self.turn == "player" and not self.player_action_performed:
                        self.perform_player_attack()

    def perform_player_attack(self):
        weapon = self.selected_hero.equipment.get("weapon")
        proj_info = None

        if weapon and weapon.weapon_type == "ranged":
            proj_info = DataManager.get_projectile_data(weapon.name)

        self.hero_sprite.trigger_attack_animation(
            self.enemy_sprite,
            projectile_data=proj_info,
            sprite_group=self.all_sprites
        )
        self.player_action_performed = True

    def update(self, dt):
        if self.game_state == GameState.BATTLE_MODE:
            self.all_sprites.update(dt)
            self._update_battle_logic(dt)

            if self.selected_hero.hp <= 0:
                print("GAME OVER")
                self.running = False

            if self.ui.is_over:
                print("GAME OVER")
                self.running = False

            elif self.enemy_sprite.model.hp <= 0 and not self.waiting_for_respawn:
                print("Nemico sconfitto. Attesa respawn...")
                self.enemy_sprite.kill()
                self.waiting_for_respawn = True
                self.respawn_timer = 0

            if self.inventory_changed:
                self.ui.update_inventory(self.selected_hero)
                self.inventory_changed = False

    def _update_battle_logic(self, dt):
        if self.waiting_for_respawn:
            if self.hero_sprite.state == SpriteState.IDLE:
                self.respawn_timer += dt

                if self.respawn_timer >= 2.0:
                    self.pick_new_enemy()
                    self.all_sprites.add(self.enemy_sprite)

                    self.waiting_for_respawn = False
                    self.turn = "player"
                    self.player_action_performed = False
                    self.enemy_action_performed = False
                    print("Nuovo nemico apparso!")
                    self.ui.refresh_background()
            return

        if self.turn == "player":
            projectiles_active = any(isinstance(s, ProjectileSprite) for s in self.all_sprites)

            if self.player_action_performed and not projectiles_active:
                if self.hero_sprite.state == SpriteState.IDLE:
                    self.turn = "enemy"
                    self.player_action_performed = False
                    self.enemy_action_performed = False
                    self.enemy_wait_timer = 0

        elif self.turn == "enemy":
            self._handle_enemy_turn_logic(dt)

    def _handle_enemy_turn_logic(self, dt):
        if not self.enemy_action_performed:
            self.enemy_wait_timer += dt
            if self.enemy_wait_timer >= 1.5:
                self.enemy_sprite.trigger_attack_animation(self.hero_sprite)
                self.enemy_action_performed = True

        if self.enemy_action_performed and self.enemy_sprite.state == SpriteState.IDLE:
            self.turn = "player"
            self.enemy_action_performed = False

    def render(self):
        if self.game_state == GameState.BATTLE_MODE:
            current_enemy = None if self.waiting_for_respawn else self.enemy_sprite

            self.ui.render_game(
                self.game_state,
                all_sprites=self.all_sprites,
                hero=self.hero_sprite,
                enemy=current_enemy
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