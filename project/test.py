import pygame

from project.characters import Warrior
from project.datatypes import Stats, Buff
from project.monsters import Goblin
from project.view import CharacterSprite, EnemySprite  # il tuo view.py

# ---------- INIZIALIZZAZIONE ----------
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Combattimento a turni")
clock = pygame.time.Clock()

# ---------- BACKGROUND ----------
bg = pygame.Surface((WIDTH, HEIGHT))
bg.fill((50, 50, 50))  # sfondo grigio scuro

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
    "idle": "../assets/warrior/warrior_1.png",
    "walk_1": "../assets/warrior/warrior_3.png",
    "walk_2": "../assets/warrior/warrior_4.png",
    "attack": "../assets/warrior/warrior_2.png"
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
    "idle": "../assets/goblin/goblin_1.png",
    "walk_1": "../assets/goblin/goblin_2.png",
    "walk_2": "../assets/goblin/goblin_3.png",
    "attack": "../assets/goblin/goblin_4.png"
})
enemy_sprite.set_target(hero_sprite)

all_sprites = pygame.sprite.Group(hero_sprite, enemy_sprite)

# ---------- TURNO ----------
turn = "player"  # player o enemy
player_attack_ready = True

# ---------- LOOP PRINCIPALE ----------
running = True
while running:
    dt = clock.tick(60) / 1000  # delta time in secondi

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ATTACCO PLAYER
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if turn == "player" and hero.hp > 0 and goblin_model.hp > 0 and player_attack_ready:
                hero_sprite.start_attack(enemy_sprite)
                player_attack_ready = False

    # ---------- LOGICA TURNO ----------
    if turn == "player":
        # Se il personaggio termina l'attacco, passa al nemico
        if hero_sprite.state == hero_sprite.SpriteState.IDLE and not player_attack_ready:
            if goblin_model.hp > 0:
                enemy_sprite.set_target(hero_sprite)
            turn = "enemy"
            player_attack_ready = True

    elif turn == "enemy":
        # Se il nemico termina l'attacco, passa al player
        if enemy_sprite.state == "idle":
            turn = "player"
        else:
            enemy_sprite.update(dt)

    # ---------- AGGIORNAMENTO SPRITE ----------
    hero_sprite.update(dt)

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
