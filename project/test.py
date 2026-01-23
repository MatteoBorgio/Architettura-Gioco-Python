import os
import sys
import pygame
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from project.characters import Warrior
from project.datatypes import Stats, Buff
from project.monsters import Goblin
from project.view import BaseSprite, SpriteState

def asset_path(*args):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, *args)

# ---------- INIZIALIZZAZIONE GIOCO ----------
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Combattimento a turni")
clock = pygame.time.Clock()

# ---------- CREAZIONE DEL BACKGROUND ----------
bg = pygame.image.load(asset_path("..", "assets", "background.jpg")).convert()
bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))

# ---------- CREAZIONE DEL PERSONAGGIO ----------
hero_stats = Stats(strength=10, dexterity=5, intelligence=3, defense=2)
hero = Warrior(
    name="Hero",
    hp=100,
    base_stats=hero_stats,
    equipment={slot: None for slot in ["weapon", "armor"]},
    mana=50,
    mana_per_attack=5,
    special_ability=Buff("Warrior's might", "strength", 2, 2),
    potions_set=[],
    shield=5,
    speed=15
)

hero_sprite = BaseSprite(hero, (200, 500), frames={
    "idle": asset_path("..", "assets", "warrior", "warrior_1.png"),
    "walk_1": asset_path("..", "assets", "warrior", "warrior_3.png"),
    "walk_2": asset_path("..", "assets", "warrior", "warrior_4.png"),
    "attack": asset_path("..", "assets", "warrior", "warrior_2.png")
})

# ---------- CREAZIONE L NEMICO ----------
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

all_sprites = pygame.sprite.Group(hero_sprite, enemy_sprite)

# ---------- TURNO ----------
turn = "player"
enemy_attack_timer = 0
player_has_attacked = False

# ---------- LOOP PRINCIPALE ----------
running = True
while running:
    dt = clock.tick(60) / 1000  # delta time in secondi

    # ---------- EVENTI ----------

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if turn == "player" and hero.hp > 0 and goblin_model.hp > 0 and not player_has_attacked:
                hero_sprite.start_attack(enemy_sprite)
                player_has_attacked = True

    # ---------- LOGICA TURNO ----------
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
    screen.blit(bg, (0, 0))
    all_sprites.draw(screen)
    hero_sprite.draw_hp_bar(screen)
    enemy_sprite.draw_hp_bar(screen)
    pygame.display.flip()

    # ---------- FINE COMBATTIMENTO ----------
    if hero.hp <= 0:
        print(f"{hero.name} è stato sconfitto!")
        running = False
    elif goblin_model.hp <= 0:
        print(f"{goblin_model.name} è stato sconfitto!")
        running = False

pygame.quit()
