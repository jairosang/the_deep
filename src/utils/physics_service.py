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
            entity.pos.x = tile.left - entity.rect.w
            entity.rect.x = entity.pos.x
        elif entity.velocity.x < 0: 
            entity.pos.x = tile.right
            entity.rect.x = entity.pos.x

def check_collisions_y(entity: Entity, tiles):
    collisions = get_hits(tiles, entity.rect)
    for tile in collisions:
        if entity.velocity.y > 0:
            entity.pos.y = tile.top - entity.rect.h
            entity.rect.y = entity.pos.y
        elif entity.velocity.y < 0: 
            entity.pos.y = tile.bottom
            entity.rect.y = entity.pos.y