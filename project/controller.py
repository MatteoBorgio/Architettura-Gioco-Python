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
        self.turn_started = False
        self.round_active = False

        self.player_action_performed = False
        self.enemy_action_performed = False
        self.enemy_wait_timer = 0

        self.waiting_for_respawn = False
        self.respawn_timer = 0

        self.selected_hero = None
        self.all_sprites = pygame.sprite.Group()
        self.inventory_changed = True

        self.load_resources()
        self.ui.create_character_selection_screen(self.characters)
        self.ui.create_battle_interface()

    def load_resources(self):
        chars_objs, weapons_objs, potions_objs = DataManager.load_data()
        self.characters = chars_objs
        self.weapons = weapons_objs
        self.potions = potions_objs

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

    def activate_ability(self):
        if not self.selected_hero.used_special_ability:
            self.selected_hero.add_buff(self.selected_hero.special_ability)
            self.selected_hero.used_special_ability = True
            self.player_action_performed = True
            print("Special ability activated")

    def pick_new_enemy(self):
        monster_model = DataManager.get_random_monster()
        frames = self._get_frames(monster_model)
        self.enemy_sprite = BaseSprite(monster_model, ENEMY_START_POS, frames)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.game_state == GameState.CHARACTER_SELECT:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    selected_model = self.ui.handle_selection_click(event.pos)
                    if selected_model:
                        self.start_battle(selected_model)


            elif self.game_state == GameState.BATTLE_MODE:

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if (
                            self.turn == "player"
                            and not self.player_action_performed
                            and not self.waiting_for_respawn
                    ):
                        for slot in self.ui.inventory_cards:
                            used = slot.check_collide(event.pos, self.selected_hero)
                            if used:
                                if slot.model in self.selected_hero.potions_set:
                                    self.selected_hero.potions_set.remove(slot.model)
                                self.player_action_performed = True
                                self.inventory_changed = True
                                break

                self.ui.handle_ui_event(event)

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
        if self.game_state != GameState.BATTLE_MODE:
            return

        if (
            self.selected_hero
            and self.turn == "player"
            and not self.player_action_performed
            and not self.waiting_for_respawn
        ):
            if self.ui.attack_button.clicked:
                self.perform_player_attack()
                self.ui.attack_button.clicked = False
            elif self.ui.special_ability_button.clicked:
                self.activate_ability()
                self.ui.special_ability_button.clicked = False

        self.ui.update()
        self.all_sprites.update(dt)
        self._update_battle_logic(dt)

        self.ui.attack_button.is_active = (
            self.turn == "player" and not self.player_action_performed and not self.waiting_for_respawn
        )

        self.ui.special_ability_button.is_active = (
            self.turn == "player"
            and not self.player_action_performed
            and not self.waiting_for_respawn
            and self.selected_hero
            and not self.selected_hero.used_special_ability
        )

        if self.selected_hero and self.selected_hero.hp <= 0:
            self.running = False
            return

        if (
            not self.waiting_for_respawn
            and self.enemy_sprite
            and self.enemy_sprite.model.hp <= 0
        ):
            self.enemy_sprite.kill()
            if self.round_active:
                self.selected_hero.end_round()
                self.round_active = False
            self.waiting_for_respawn = True
            self.selected_hero.used_special_ability = False
            self.respawn_timer = 0

        if self.ui.is_over:
            self.running = False
            return

        if self.inventory_changed and self.selected_hero:
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
                    self.turn_started = False
                    self.round_active = False
                    self.player_action_performed = False
                    self.enemy_action_performed = False
                    print("Nuovo nemico apparso!")
                    self.ui.refresh_background()
            return

        if self.turn == "player":
            if not self.turn_started:
                self.selected_hero.start_turn()
                self.turn_started = True
                self.round_active = True

            projectiles_active = any(isinstance(s, ProjectileSprite) for s in self.all_sprites)

            if self.player_action_performed and not projectiles_active:
                if self.hero_sprite.state == SpriteState.IDLE:
                    self.turn = "enemy"
                    self.turn_started = False
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
            if self.round_active:
                self.selected_hero.end_round()
                self.round_active = False

            self.turn = "player"
            self.enemy_action_performed = False
            self.player_action_performed = False

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
