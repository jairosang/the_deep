from src.utils.tile_map import TileMap
from src.entities.base_entity import Entity
from src.entities.creatures.base_creature import Creature
from src.entities.creatures.creature_aggressive import AggressiveCreature
from pygame import Rect

def get_hits(tiles: list[Rect], rect: Rect) -> list[Rect]:
    hits = []
    for tile in tiles:
        if rect.colliderect(tile):
            hits.append(tile)
    return hits

def check_collisions_x(entity: Entity, tiles):
    collisions = get_hits(tiles, entity.rect)
    for tile in collisions:
        if entity.velocity.x > 0:
            entity.rect.right = tile.left
            entity.pos.x = entity.rect.x
            break
        elif entity.velocity.x < 0: 
            entity.rect.left = tile.right
            entity.pos.x = entity.rect.x
            break

def check_collisions_y(entity: Entity, tiles):
    collisions = get_hits(tiles, entity.rect)
    for tile in collisions:
        if entity.velocity.y < 0:
            entity.rect.top = tile.bottom
            entity.pos.y = entity.rect.y
            break
        elif entity.velocity.y > 0: 
            entity.rect.bottom = tile.top
            entity.pos.y = entity.rect.y
            break

def check_entity_collisions(player: Entity, creatures: list[Creature]):
    creature_hits: list[Creature] = []
    for creature in creatures:
        if player.rect.colliderect(creature.rect):
            player.get_damaged(7)  # The creatures should have a damage attribute that is the one taken here to damage the player
            player.velocity = creature.vel * 1.5
            creature.vel *= -1

            # COMMENTED THIS OUT UNTIL CREATURE MOVEMENT MATCHES THE PLAYER'S APPROACH WITH ACCELERATION AND THRUST (Changelog task)
            # Right now the creatures have instant velocity which makes this realistic collision approach not work well...
            # player_vel_x = ((player.mass - creature.mass)/(player.mass + creature.mass)) * player.velocity
            # player_vel_y = ((2 * creature.mass)/(player.mass + creature.mass)) * creature.vel

            # creature_vel_x = ((2 * player.mass)/(player.mass + creature.mass)) * player.velocity
            # creature_vel_y = ((creature.mass - player.mass)/(player.mass + creature.mass)) * creature.vel
            # creature.vel = creature_vel_x + creature_vel_y
            # player.velocity = player_vel_x + player_vel_y

    return creature_hits