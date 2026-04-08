from src.utils.tile_map import TileMap
from src.entities.base_entity import Entity
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