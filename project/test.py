import os
import pygame
from project.characters import Warrior
from project.datatypes import Stats, Buff
from project.monsters import Goblin
from project.view import CharacterSprite, EnemySprite, SpriteState

# ---------- FUNZIONE ASSET PATH ----------
def asset_path(*args):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, *args)

# ---------- INIZIALIZZAZIONE ----------
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Combattimento a turni")
clock = pygame.time.Clock()

# ---------- BACKGROUND ----------
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
    shield=5
)

hero_sprite = CharacterSprite(hero, x=200, y=500, frames={
    "idle": asset_path("..", "assets", "warrior", "warrior_1.png"),
    "walk_1": asset_path("..", "assets", "warrior", "warrior_3.png"),
    "walk_2": asset_path("..", "assets", "warrior", "warrior_4.png"),
    "attack": asset_path("..", "assets", "warrior", "warrior_2.png")
})

# ---------- CREAZIONE DEL NEMICO ----------
goblin_model = Goblin(
    name="Goblin",
    hp=50,
    base_damage=8,
    bonus_damage=4,
    equipment={},
    buff_stole_per_turn=1,
    level=1
)

enemy_sprite = EnemySprite(goblin_model, x=600, y=500, frames={
    "idle": asset_path("..", "assets", "goblin", "goblin_1.png"),
    "walk_1": asset_path("..", "assets", "goblin", "goblin_2.png"),
    "walk_2": asset_path("..", "assets", "goblin", "goblin_3.png"),
    "attack": asset_path("..", "assets", "goblin", "goblin_4.png")
})

all_sprites = pygame.sprite.Group(hero_sprite, enemy_sprite)

# ---------- TURNO ----------
turn = "player"

# ---------- LOOP PRINCIPALE ----------
running = True
while running:
    dt = clock.tick(60) / 1000  # delta time in secondi

    # ---------- EVENTI ----------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ATTACCO PLAYER
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if turn == "player" and hero.hp > 0 and goblin_model.hp > 0:
                hero_sprite.start_attack(enemy_sprite)

    # ---------- LOGICA TURNO ----------
    if turn == "player":
        hero_sprite.update(dt)
        # Aspetta che il player torni alla posizione iniziale prima di passare turno
        if hero_sprite.state == SpriteState.IDLE and hero_sprite.target is None:
            turn = "enemy"

    elif turn == "enemy":
        if enemy_sprite.state == SpriteState.IDLE and enemy_sprite.target is None:
            enemy_sprite.set_target(hero_sprite)
        enemy_sprite.update(dt)
        # Aspetta che il nemico torni alla posizione iniziale prima di passare turno
        if enemy_sprite.state == SpriteState.IDLE and enemy_sprite.target is None:
            turn = "player"

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
