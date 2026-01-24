import os
import sys
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from project.characters import Warrior, Cleric, Thief
from project.datatypes import Stats, Buff
from project.monsters import Goblin
from project.view import BaseSprite, SpriteState, CharacterCard
from game_state import GameState

# ---------- FUNZIONI UTILI ----------
def asset_path(*args):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, *args)

def calculate_card_positions(screen_rect, num_cards, card_width, card_center_y):
    total_width = num_cards * card_width
    start_x = screen_rect.centerx - total_width / 2 + card_width / 2
    positions = [(start_x + i * card_width, card_center_y) for i in range(num_cards)]
    return positions

# ---------- INIZIALIZZAZIONE ----------
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Combattimento a turni")
clock = pygame.time.Clock()

# ---------- FONT ----------
font_path = asset_path("..", "assets", "font", "selection_font.ttf")
selection_font = pygame.font.Font(font_path, 36)  # dimensione 36

# ---------- SFONDO ----------
bg = pygame.image.load(asset_path("..", "assets", "background.jpg")).convert()
bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))

card_bg_image = pygame.image.load(asset_path("..", "assets", "menu_wooden_board.jpg")).convert()
bg_selection = pygame.transform.scale(card_bg_image, (WIDTH, HEIGHT))

# ---------- CREAZIONE NEMICO ----------
goblin_model = Goblin(
    name="Goblin",
    hp=50,
    base_damage=8,
    bonus_damage=4,
    equipment={},
    buff_stole_per_turn=1,
    level=1,
    speed=20
)

enemy_sprite = BaseSprite(goblin_model, (600, 500), frames={
    "idle": asset_path("..", "assets", "goblin", "goblin_1.png"),
    "walk_1": asset_path("..", "assets", "goblin", "goblin_2.png"),
    "walk_2": asset_path("..", "assets", "goblin", "goblin_3.png"),
    "attack": asset_path("..", "assets", "goblin", "goblin_4.png")
})

# ---------- CREAZIONE STATI E VARIABILI ----------
game_state = GameState.CHARACTER_SELECT
selected_hero = None
all_sprites = pygame.sprite.Group()

# ---------- CREAZIONE CARD ----------
warrior_stats = Stats(strength=9, dexterity=4, intelligence=3, defense=4)
warrior = Warrior(
    name="Warrior",
    hp=120,
    base_stats=warrior_stats,
    equipment={slot: None for slot in ["weapon", "armor"]},
    mana=50,
    mana_per_attack=5,
    special_ability=Buff("Warrior's might", "strength", 2, 2),
    potions_set=[],
    shield=5,
    speed=15
)

cleric_stats = Stats(strength=5, dexterity=5, intelligence=9, defense=1)
cleric = Cleric(
    name="Cleric",
    hp=100,
    base_stats=cleric_stats,
    equipment={slot: None for slot in ["weapon", "armor"]},
    mana=60,
    mana_per_attack=4,
    special_ability=Buff("God Protecion", "defense", 5, 2),
    potions_set=[],
    poisons_mitigation=3,
    healing_per_attack=5,
    speed=10
)

thief_stats = Stats(strength=4, dexterity=9, intelligence=6, defense=1)
thief = Thief(
    name="Thief",
    hp=80,
    base_stats=thief_stats,
    equipment={slot: None for slot in ["weapon", "armor"]},
    mana=30,
    mana_per_attack=3,
    special_ability=Buff("Art of stealing", "dexterity", 4, 3),
    potions_set=[],
    critical_bonus=5,
    speed=30
)

screen_rect = screen.get_rect()
card_spacing = 110
card_width = 200
card_center_y = screen_rect.centery + 50

positions = calculate_card_positions(screen_rect, 3, card_width, card_center_y)

cards = [
    CharacterCard(
        card_image_path=asset_path("..", "assets", "wooden_board.png"),
        character_image_path=asset_path("..", "assets", "warrior", "warrior_1.png"),
        model=warrior,
        center_pos=positions[0],
        font=selection_font
    ),
    CharacterCard(
        card_image_path=asset_path("..", "assets", "wooden_board.png"),
        character_image_path=asset_path("..", "assets", "cleric", "cleric_1.png"),
        model=cleric,
        center_pos=positions[1],
        font=selection_font
    ),
    CharacterCard(
        card_image_path=asset_path("..", "assets", "wooden_board.png"),
        character_image_path=asset_path("..", "assets", "thief", "thief_1.png"),
        model=thief,
        center_pos=positions[2],
        font=selection_font
    )
]

# ---------- VARIABILI TURNO ----------
turn = "player"
enemy_attack_timer = 0
player_has_attacked = False

# ---------- MAIN LOOP ----------
running = True
while running:
    dt = clock.tick(60) / 1000  # delta time in secondi

    # ---------- EVENTI ----------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == GameState.CHARACTER_SELECT:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for card in cards:
                    if card.is_clicked(event.pos):
                        selected_hero = card.model

                        if isinstance(selected_hero, Warrior):
                            frames = {
                                "idle": asset_path("..", "assets", "warrior", "warrior_1.png"),
                                "walk_1": asset_path("..", "assets", "warrior", "warrior_3.png"),
                                "walk_2": asset_path("..", "assets", "warrior", "warrior_4.png"),
                                "attack": asset_path("..", "assets", "warrior", "warrior_2.png")
                            }
                        elif isinstance(selected_hero, Cleric):
                            frames = {
                                "idle": asset_path("..", "assets", "cleric", "cleric_1.png"),
                                "walk_1": asset_path("..", "assets", "cleric", "cleric_2.png"),
                                "walk_2": asset_path("..", "assets", "cleric", "cleric_3.png"),
                                "attack": asset_path("..", "assets", "cleric", "cleric_4.png")
                            }
                        elif isinstance(selected_hero, Thief):
                            frames = {
                                "idle": asset_path("..", "assets", "thief", "thief_1.png"),
                                "walk_1": asset_path("..", "assets", "thief", "thief_2.png"),
                                "walk_2": asset_path("..", "assets", "thief", "thief_3.png"),
                                "attack": asset_path("..", "assets", "thief", "thief_4.png")
                            }

                        hero_sprite = BaseSprite(selected_hero, (200, 490), frames=frames)
                        all_sprites = pygame.sprite.Group(hero_sprite, enemy_sprite)
                        turn = "player"
                        player_has_attacked = False
                        enemy_attack_timer = 0
                        game_state = GameState.BATTLE_MODE

        elif game_state == GameState.BATTLE_MODE:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if turn == "player" and hero_sprite.model.hp > 0 and goblin_model.hp > 0 and not player_has_attacked:
                    hero_sprite.start_attack(enemy_sprite)
                    player_has_attacked = True

    # ---------- LOGICA ----------
    if game_state == GameState.BATTLE_MODE:
        if turn == "player":
            hero_sprite.update(dt)
            if player_has_attacked and hero_sprite.state == SpriteState.IDLE and hero_sprite.target is None:
                turn = "enemy"
                player_has_attacked = False

        elif turn == "enemy":
            enemy_sprite.update(dt)
            if not hasattr(enemy_sprite, 'has_attacked'):
                enemy_sprite.has_attacked = False

            if not enemy_sprite.has_attacked and enemy_sprite.state == SpriteState.IDLE and enemy_sprite.target is None:
                enemy_attack_timer += dt
                if enemy_attack_timer >= 2:
                    enemy_sprite.start_attack(hero_sprite)
                    enemy_sprite.has_attacked = True
                    enemy_attack_timer = 0

            if enemy_sprite.state == SpriteState.IDLE and enemy_sprite.target is None and enemy_sprite.has_attacked:
                turn = "player"
                enemy_sprite.has_attacked = False

    # ---------- RENDER ----------
    if game_state == GameState.CHARACTER_SELECT:
        screen.blit(bg_selection, (0, 0))  # sfondo selezione

        text_surface = selection_font.render("SELECT YOUR CHARACTER:", True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(screen_rect.centerx, screen_rect.centery - 150))
        screen.blit(text_surface, text_rect)

        for card in cards:
            card.draw(screen)

    elif game_state == GameState.BATTLE_MODE:
        screen.blit(bg, (0, 0))
        all_sprites.draw(screen)
        hero_sprite.draw_hp_bar(screen)
        enemy_sprite.draw_hp_bar(screen)

    pygame.display.flip()

    # ---------- FINE COMBATTIMENTO ----------
    if game_state == GameState.BATTLE_MODE:
        if hero_sprite.model.hp <= 0:
            print(f"{hero_sprite.model.name} è stato sconfitto!")
            running = False
        elif goblin_model.hp <= 0:
            print(f"{goblin_model.name} è stato sconfitto!")
            running = False

pygame.quit()
