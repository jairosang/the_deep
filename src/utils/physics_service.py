from typing import TYPE_CHECKING
from pygame import Rect
# This is to avoid circular imports
if TYPE_CHECKING:
    from src.entities.base_moving_thing import MovingThing
    from src.entities.creatures.creature_aggressive import AggressiveCreature
    from src.entities.player import Player

def get_hits(tiles: list[Rect], rect: Rect) -> list[Rect]:
    hits = []
    for tile in tiles:
        if rect.colliderect(tile):
            hits.append(tile)
    return hits

def check_and_resolve_player_map_collisions_x(entity: 'MovingThing', tiles: list[Rect]):
    collisions = get_hits(tiles, entity.rect)
    for tile in collisions:
        resolve_collisions_x(entity, tile)
        break   # Just for now bc I was to lazy to implement tile closest to player,idk...
            
def check_and_resolve_player_map_collisions_y(entity: 'MovingThing', tiles):
    collisions = get_hits(tiles, entity.rect)
    for tile in collisions:
        resolve_collisions_y(entity, tile)
        break   # Just for now bc I was to lazy to implement tile closest to player,idk...

def resolve_collisions_x(moving_thing: 'MovingThing', rect_b: Rect):
    if moving_thing.velocity.x > 0:
        moving_thing.rect.right = rect_b.left
        moving_thing.pos.x = moving_thing.rect.x
    elif moving_thing.velocity.x < 0: 
        moving_thing.rect.left = rect_b.right
        moving_thing.pos.x = moving_thing.rect.x

def resolve_collisions_y(moving_thing: 'MovingThing', rect_b: Rect):
    if moving_thing.velocity.y < 0:
        moving_thing.rect.top = rect_b.bottom
        moving_thing.pos.y = moving_thing.rect.y
    elif moving_thing.velocity.y > 0: 
        moving_thing.rect.bottom = rect_b.top
        moving_thing.pos.y = moving_thing.rect.y

def check_entity_collisions(player: 'Player', creatures: list['AggressiveCreature']):
    creature_hits: list['AggressiveCreature'] = []
    for creature in creatures:
        if player.rect.colliderect(creature.rect):
            player.get_damaged(1)  # The creatures should have a damage attribute that is the one taken here to damage the player

            player_vel_x = ((player.mass - creature.mass)/(player.mass + creature.mass)) * player.velocity
            player_vel_y = ((2 * creature.mass)/(player.mass + creature.mass)) * creature.velocity

            creature_vel_x = ((2 * player.mass)/(player.mass + creature.mass)) * player.velocity
            creature_vel_y = ((creature.mass - player.mass)/(player.mass + creature.mass)) * creature.velocity

            creature.velocity = creature_vel_x + creature_vel_y
            player.velocity = player_vel_x + player_vel_y
    return creature_hits
