import os
import sys
import pygame
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from project.characters import Warrior, Cleric, Thief, Wizard
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


def create_character(data):
    """Crea un'istanza di personaggio a partire dai dati JSON."""
    base_stats = Stats(
        strength=data.get("strength", 0),
        dexterity=data.get("dexterity", 0),
        intelligence=data.get("intelligence", 0),
        defense=data.get("defense", 0)
    )

    # Creo la special ability
    sa = data.get("special_ability", {})
    special_ability = Buff(
        name=sa.get("name", ""),
        stat=sa.get("stat", ""),
        amount=sa.get("amount", 0),
        duration=sa.get("duration", 0)
    )

    cls_map = {
        "Warrior": Warrior,
        "Cleric": Cleric,
        "Thief": Thief,
        "Wizard": Wizard
    }

    cls = cls_map.get(data["class"])
    if not cls:
        raise ValueError(f"Classe non riconosciuta: {data['class']}")

    # Parametri comuni
    kwargs = {
        "name": data["name"],
        "hp": data["hp"],
        "base_stats": base_stats,
        "equipment": {slot: None for slot in ["weapon", "armor"]},
        "mana": data.get("mana", 0),
        "mana_per_attack": data.get("mana_per_attack", 0),
        "special_ability": special_ability,
        "speed": data.get("speed", 10),
        "potions_set": data["potions_set"]
    }

    # Parametri specifici per classe
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


# ---------- INIZIALIZZAZIONE PYGAME ----------
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Combattimento a turni")
clock = pygame.time.Clock()

font_path = asset_path("..", "assets", "font", "selection_font.ttf")
selection_font = pygame.font.Font(font_path, 36)

bg = pygame.image.load(asset_path("..", "assets", "background.jpg")).convert()
bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
bg_selection = pygame.transform.scale(
    pygame.image.load(asset_path("..", "assets", "menu_wooden_board.jpg")).convert(),
    (WIDTH, HEIGHT)
)

screen_rect = screen.get_rect()
card_width = 200
card_center_y = screen_rect.centery + 50

# ---------- CARICAMENTO JSON DEI PERSONAGGI ----------
with open(asset_path("..", "data", "characters.json")) as f:
    character_data = json.load(f)

characters = [create_character(d) for d in character_data]

# ---------- CREAZIONE CARD ----------
positions = calculate_card_positions(screen_rect, len(characters), card_width, card_center_y)

cards = []
for i, char in enumerate(characters):
    card = CharacterCard(
        card_image_path=asset_path("..", "assets", "wooden_board.png"),
        character_image_path=asset_path("..", "assets", char.__class__.__name__.lower(), f"{char.__class__.__name__.lower()}_1.png"),
        model=char,
        center_pos=positions[i],
        font=selection_font
    )
    cards.append(card)

# ---------- CREAZIONE NEMICO ----------
goblin_model = Goblin(name="Goblin", hp=50, base_damage=8, bonus_damage=4, equipment={}, buff_stole_per_turn=1, level=1,
                      speed=20)
enemy_sprite = BaseSprite(goblin_model, (600, 500), frames={
    "idle": asset_path("..", "assets", "goblin", "goblin_1.png"),
    "walk_1": asset_path("..", "assets", "goblin", "goblin_2.png"),
    "walk_2": asset_path("..", "assets", "goblin", "goblin_3.png"),
    "attack": asset_path("..", "assets", "goblin", "goblin_4.png")
})

# ---------- VARIABILI DI STATO ----------
game_state = GameState.CHARACTER_SELECT
selected_hero = None
all_sprites = pygame.sprite.Group()
turn = "player"
enemy_attack_timer = 0
player_has_attacked = False


# ---------- FUNZIONE PER I FRAMES DELLO SPRITE ----------
def get_frames_for_character(char):
    folder = char.__class__.__name__.lower()
    return {
        "idle": asset_path("..", "assets", folder, f"{folder}_1.png"),
        "walk_1": asset_path("..", "assets", folder, f"{folder}_2.png"),
        "walk_2": asset_path("..", "assets", folder, f"{folder}_3.png"),
        "attack": asset_path("..", "assets", folder, f"{folder}_4.png")
    }


# ---------- MAIN LOOP ----------
running = True
while running:
    dt = clock.tick(60) / 1000

    # ---------- EVENTI ----------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == GameState.CHARACTER_SELECT and event.type == pygame.MOUSEBUTTONDOWN:
            for card in cards:
                if card.is_clicked(event.pos):
                    selected_hero = card.model
                    frames = get_frames_for_character(selected_hero)
                    hero_sprite = BaseSprite(selected_hero, (200, 490), frames=frames)
                    all_sprites = pygame.sprite.Group(hero_sprite, enemy_sprite)
                    game_state = GameState.BATTLE_MODE
                    turn = "player"
                    player_has_attacked = False
                    enemy_attack_timer = 0

        elif game_state == GameState.BATTLE_MODE and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
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
        screen.blit(bg_selection, (0, 0))
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
