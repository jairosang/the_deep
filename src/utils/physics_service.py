from typing import TYPE_CHECKING
from pygame import Rect
from config import aggresive_creatures as ac_config

# This is to avoid circular imports
if TYPE_CHECKING:
    from things import MovingThing, Creature, Player, Item, Projectile

def get_colliding_tiles(tiles: list[Rect], rect: Rect) -> list[Rect]:
    hits = []
    for tile in tiles:
        if rect.colliderect(tile):
            hits.append(tile)
    return hits

def resolve_map_collision_on_x_axis(entity: 'MovingThing', tiles: list[Rect]):
    collisions = get_colliding_tiles(tiles, entity.rect)
    for tile in collisions:
        resolve_overlap_on_x_axis(entity, tile)
        break   # Just for now bc I was to lazy to implement tile closest to player,idk...
            
def resolve_map_collision_on_y_axis(entity: 'MovingThing', tiles):
    collisions = get_colliding_tiles(tiles, entity.rect)
    for tile in collisions:
        resolve_overlap_on_y_axis(entity, tile)
        break   # Just for now bc I was to lazy to implement tile closest to player,idk...

def resolve_overlap_on_x_axis(moving_thing: 'MovingThing', rect_b: Rect):
    if moving_thing.velocity.x > 0:
        moving_thing.rect.right = rect_b.left
        moving_thing.pos.x = moving_thing.rect.x
    elif moving_thing.velocity.x < 0: 
        moving_thing.rect.left = rect_b.right
        moving_thing.pos.x = moving_thing.rect.x

def resolve_overlap_on_y_axis(moving_thing: 'MovingThing', rect_b: Rect):
    if moving_thing.velocity.y < 0:
        moving_thing.rect.top = rect_b.bottom
        moving_thing.pos.y = moving_thing.rect.y
    elif moving_thing.velocity.y > 0: 
        moving_thing.rect.bottom = rect_b.top
        moving_thing.pos.y = moving_thing.rect.y

def _apply_elastic_collision(a: 'MovingThing', b: 'MovingThing'):
    a_vel = ((a.mass - b.mass) / (a.mass + b.mass)) * a.velocity + ((2 * b.mass) / (a.mass + b.mass)) * b.velocity
    b_vel = ((2 * a.mass) / (a.mass + b.mass)) * a.velocity + ((b.mass - a.mass) / (a.mass + b.mass)) * b.velocity
    a.velocity = a_vel
    b.velocity = b_vel

def _resolve_player_creature_contact(player: 'Player', creature: 'Creature', tiles: list[Rect] | None = None):
    overlap = player.rect.clip(creature.rect)
    if overlap.width <= 0 or overlap.height <= 0:
        return

    # Resolve along the smallest overlap axis, same as map collisions.
    # This pushes the player out even if the creature is pinned to a wall.
    if overlap.width <= overlap.height:
        player_direction = 1 if player.rect.centerx <= creature.rect.centerx else -1
        player_target_rect = player.rect.copy()
        if player_direction > 0:
            player_target_rect.right = creature.rect.left
        else:
            player_target_rect.left = creature.rect.right
        player_push_blocked = tiles is not None and any(player_target_rect.colliderect(tile) for tile in tiles)

        if player_push_blocked:
            creature_direction = -player_direction
            original_vx = creature.velocity.x
            creature.velocity.x = creature_direction
            resolve_overlap_on_x_axis(creature, player.rect)
            creature.velocity.x = original_vx
        else:
            original_vx = player.velocity.x
            player.velocity.x = player_direction
            resolve_overlap_on_x_axis(player, creature.rect)
            player.velocity.x = original_vx
    else:
        player_direction = 1 if player.rect.centery <= creature.rect.centery else -1
        player_target_rect = player.rect.copy()
        if player_direction > 0:
            player_target_rect.top = creature.rect.bottom
        else:
            player_target_rect.bottom = creature.rect.top
        player_push_blocked = tiles is not None and any(player_target_rect.colliderect(tile) for tile in tiles)

        if player_push_blocked:
            creature_direction = -player_direction
            original_vy = creature.velocity.y
            creature.velocity.y = creature_direction
            resolve_overlap_on_y_axis(creature, player.rect)
            creature.velocity.y = original_vy
        else:
            original_vy = player.velocity.y
            player.velocity.y = player_direction
            resolve_overlap_on_y_axis(player, creature.rect)
            player.velocity.y = original_vy

def resolve_player_creature_collisions(player: 'Player', creatures: list['Creature'], tiles: list[Rect] | None = None):
    from things import AggressiveCreature, Item
    
    dead_creatures = []
    dropped_items = []

    for creature in creatures:

        if creature.is_dying:
            if creature.is_dead():
                dead_creatures.append(creature)
                dropped_items.append(Item(creature.rect.topleft, image=creature.image, inventory_image=creature._base_image))
            continue
        
        if player.rect.colliderect(creature.rect):
            _resolve_player_creature_contact(player, creature, tiles)

            if isinstance(creature, AggressiveCreature):
                player.get_damaged(creature.damage)

            _apply_elastic_collision(player, creature)

            if creature.is_dead():
                dead_creatures.append(creature)
                dropped_items.append(Item(creature.rect.topleft, image=creature.image, inventory_image=creature._base_image))

    for creature in dead_creatures:
        creatures.remove(creature)

    return dropped_items

def resolve_player_item_pickups(player: 'Player', items: list['Item'], dt: float) -> list['Item']:
    picked_items = []

    for item in items:
        if item.pickup_timer > 0:
            item.pickup_timer = max(0, item.pickup_timer - dt)
            continue

        if player.rect.colliderect(item.rect):
            player.buffer_inventory.append(item) # each item in its place, no stacking
            picked_items.append(item)

    for item in picked_items:
        items.remove(item)

    return picked_items

def resolve_projectile_creature_collisions(projectiles: list['Projectile'], creatures: list['Creature']):
    from things import Item

    dead_creatures = []
    dropped_items = []
    spent_projectiles = []

    for projectile in projectiles:
        if projectile.is_destroyed:
            spent_projectiles.append(projectile)
            continue

        for creature in creatures:
            if creature.is_dying:
                continue

            if projectile.rect.colliderect(creature.rect):
                creature.get_damaged(projectile.damage)
                _apply_elastic_collision(projectile, creature)
                projectile.destroy()
                spent_projectiles.append(projectile)

                if creature.is_dead():
                    dead_creatures.append(creature)
                    dropped_items.append(Item(creature.rect.topleft, image=creature.image, inventory_image=creature._base_image))
                break

    for creature in dead_creatures:
        if creature in creatures:
            creatures.remove(creature)

    return dropped_items, spent_projectiles