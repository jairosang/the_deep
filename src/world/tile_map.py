from .interactables import Interactable, Exit, Upgrades, Research
import xml.etree.ElementTree as ET
from pathlib import Path
import json
import pygame

# https://doc.mapeditor.org/en/latest/reference/global-tile-ids/ * mic drop *
FLIPPED_HORIZONTALLY_FLAG = 0x80000000
FLIPPED_VERTICALLY_FLAG = 0x40000000
FLIPPED_DIAGONALLY_FLAG = 0x20000000
DIAGONAL_FLIP_FLAG = 0x20000000
ALL_FLIP_FLAGS = (FLIPPED_HORIZONTALLY_FLAG | FLIPPED_VERTICALLY_FLAG | FLIPPED_DIAGONALLY_FLAG | FLIPPED_DIAGONALLY_FLAG)

# Just takes the info from the gid
def normalize_gid(encoded_gid: int) -> tuple[int, bool, bool, bool]:
    base_gid = encoded_gid & ~ALL_FLIP_FLAGS
    flip_h = bool(encoded_gid & FLIPPED_HORIZONTALLY_FLAG)
    flip_v = bool(encoded_gid & FLIPPED_VERTICALLY_FLAG)
    flip_diagonal = bool(encoded_gid & DIAGONAL_FLIP_FLAG)
    return base_gid, flip_h, flip_v, flip_diagonal

class Layer:
    def __init__(self, layer_data: dict) -> None:
        self.name: str = layer_data.get("name", "")
        self.id: int = layer_data.get("id", 0)
        self.opacity: float = layer_data.get("opacity", 1.0)
        self.visible: bool = layer_data.get("visible", True)
        self.type: str = layer_data.get("type", "")

class TileLayer(Layer):
    def __init__(self, layer: dict, tile_size: tuple[int, int]) -> None:
        super().__init__(layer)
        self.width: int = layer.get("width", 0)
        self.height: int = layer.get("height", 0)
        self.x: int = layer.get("x", 0)
        self.y: int = layer.get("y", 0)
        self.tile_width: int = tile_size[0]
        self.tile_height: int = tile_size[1]


        self.grid = self._build(layer.get("data", []))
        self.collisions_grid: list[list[pygame.Rect | None]] = self._build_collisions()

    def _build(self, data):
        grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        for i, gid in enumerate(data):
            grid[i // self.width][i % self.width] = gid
        return grid

    def _build_collisions(self):
        grid: list[list[pygame.Rect | None]] = [[None for _ in range(self.width)] for _ in range(self.height)]
        for row_index, row in enumerate(self.grid):
            for column_index, gid in enumerate(row):
                normalized_gid, _, _, _ = normalize_gid(gid)
                if normalized_gid != 0:
                    grid[row_index][column_index] = pygame.Rect(
                        self.x + column_index * self.tile_width,
                        self.y + row_index * self.tile_height,
                        self.tile_width,
                        self.tile_height,
                    )
        return grid

class InfiniteLayer(Layer):

    def __init__(self, layer_data: dict) -> None:
        super().__init__(layer_data)
        self.width: int = layer_data.get("width", 0)
        self.height: int = layer_data.get("height", 0)
        self.offset_x: float = layer_data.get("offsetx", 0)
        self.offset_y: float = layer_data.get("offsety", 0)


class InfiniteTileLayer(InfiniteLayer):
    def __init__(self, layer_data: dict) -> None:
        super().__init__(layer_data)
        self.width: int = layer_data.get("width", 0)
        self.height: int = layer_data.get("height", 0)
        self.start_x: int = layer_data.get("startx", 0)
        self.start_y: int = layer_data.get("starty", 0)

        self.grid = self.build_from_chunks(layer_data.get("chunks", []))

    def build_from_chunks(self, chunks):
        grid = [[0 for _ in range(self.width)] for _ in range(self.height)]

        for chunk in chunks:
            norm_x = chunk["x"] - self.start_x
            norm_y = chunk["y"] - self.start_y
            
            # This guy just transferst the i horizontal movement accross the chunk array into 2d array for the grid and assigns the corresponding chunk_data 
            chunk_data = chunk["data"]
            for i, el in enumerate(chunk_data):
                grid[norm_y + (i // chunk["width"])][norm_x + (i % chunk["width"])] = chunk_data[i]

        return grid
    
class InfiniteImageLayer(InfiniteLayer):
    def __init__(self, layer_data: dict) -> None:
        super().__init__(layer_data)
        self.image: str = layer_data.get("image", "")
        self.image_width: int = layer_data.get("imagewidth", 0)
        self.image_height: int = layer_data.get("imageheight", 0)
        self.repeat_x: bool = layer_data.get("repeatx", False)
        self.repeat_y: bool = layer_data.get("repeaty", False)
        self.parallax_x: float = layer_data.get("parallaxx", 1.0)
        self.parallax_y: float = layer_data.get("parallaxy", 1.0)

    
    
class TileMap:
    def __init__(self, path: Path) -> None:
        self.visual_layer: pygame.Surface | None = None
        self.tile_size: tuple[int, int] = (0, 0)
        self.map_size: tuple[int, int] = (0, 0)
        self.tile_layers: dict[str,TileLayer | InfiniteTileLayer] = {}
        self.mid_layer: TileLayer | InfiniteTileLayer | None
        self.background_assets_layer: InfiniteTileLayer | TileLayer
        self.background_tiles_layer: InfiniteTileLayer | TileLayer
        self.interactables: list[Interactable]
        self.tilesets: list[tuple[int, pygame.Surface | dict, int]] = []  # (firstgid, atlas, columns) sorted descending

        self.parse_from_path(path)

    def parse_from_path(self, path: Path):
        with path.open("r", encoding="utf-8") as f:
            tile_map = json.load(f)
        
        # Someone pls change this latter im begging you it would be nice to have proper errors pls pls pls thanks.
        if tile_map is None:
            return "I like ice cream and the path you gave is wrong womp womp"
        
        # Get em facts from the tiled json file
        self.tile_size = (tile_map["tilewidth"], tile_map["tileheight"])

        # ==== Buffer for the name of layer and the data ======
        # Tile layers
        tile_layer_buffer = {layer.get("name"):layer for layer in tile_map["layers"] if layer.get("type") == "tilelayer"}
        if tile_layer_buffer.get("Midground") is None:           # These are not errors they just wont be built
            print("Couldn't find a layer called 'Midground' in your map")
        if tile_layer_buffer.get("Background_tiles") is None:
            print("Couldn't find a layer called 'Background_tiles' in your map")
        if tile_layer_buffer.get("Background_assets") is None:
            print("Couldn't find a layer called 'Background_assets' in your map")

        # Object groups
        object_groups_buffer = [layer for layer in tile_map["layers"] if layer.get("type") == "objectgroup"]
        
        # Interactable layer
        interactable_layer = None
        for group in object_groups_buffer:
            if group.get("name") == "Interactables":
                interactable_layer = group
        if interactable_layer is None:
            print("Couldn't find a layer called 'Interactables' in your map")

        # Building the tile layers, they can be either finite or infinite
        if tile_map["infinite"] == True:
            for layer in tile_layer_buffer.keys():
                self.tile_layers[layer] = InfiniteTileLayer(tile_layer_buffer[layer])
        else:
            for layer in tile_layer_buffer.keys():
                self.tile_layers[layer] = TileLayer(tile_layer_buffer[layer], self.tile_size)
                
        # Extract the map size
        if "Midground" in self.tile_layers:
            self.mid_layer = self.tile_layers.get("Midground")
            self.map_size = (
                self.tile_layers["Midground"].width * self.tile_size[0],
                self.tile_layers["Midground"].height * self.tile_size[1],
            )

        for tileset_data in tile_map["tilesets"]:
            firstgid = int(tileset_data["firstgid"])
            tsx_path = (path.parent / tileset_data["source"]).resolve()
            atlas_surface, column_count = self._load_tileset_surface_and_columns(tsx_path)
            self.tilesets.append((firstgid, atlas_surface, column_count))
        self.tilesets.sort(key=lambda t: t[0], reverse=True)

        self.visual_surface = self._build_tile_layers()
        self.interactables = self._load_interactables(interactable_layer)


    def draw(self, world_surface: pygame.Surface, camera_rect: pygame.Rect, position: tuple[int, int] = (0, 0)) -> None:
        if self.visual_surface is not None:
            # Blit the map into the world, but only the things inside the camera
            world_surface.blit(self.visual_surface, camera_rect.topleft, camera_rect)


    def is_tile_solid(self, x, y) -> bool:
        normalized_gID, _, _, _ = self.get_tile_at_position(x, y)
        return normalized_gID != 0
    
        # Not implemented because its not my thing. Yet....

    def get_tiles_at_area(self, x, y, size: tuple[int,int]) -> list[pygame.Rect]:
        if self.mid_layer is None:
            raise LookupError("Map contains no mid_layer bro")

        tile_width, tile_height = self.tile_size
        tiles: list[pygame.Rect] = []

        center_column = int(x // tile_width)
        center_row = int(y // tile_height)
        half_columns = size[0] // 2
        half_rows = size[1] // 2

        start_column = max(0, center_column - half_columns)
        end_column = min(self.mid_layer.width - 1, center_column + half_columns)
        start_row = max(0, center_row - half_rows)
        end_row = min(self.mid_layer.height - 1, center_row + half_rows)

        if start_column > end_column or start_row > end_row:
            return tiles

        for row in range(start_row, end_row + 1):
            for column in range(start_column, end_column + 1):
                tile_id, _, _, _ = self.get_tile_at_position(column * tile_width, row * tile_height)
                if tile_id == 0:
                    continue

                tiles.append(
                    pygame.Rect(
                        column * tile_width,
                        row * tile_height,
                        tile_width,
                        tile_height,
                    )
                )

        return tiles

    def get_tile_at_position(self, x, y):
        if self.mid_layer is None:
            raise LookupError("Map contains no mid_layer bro")
        
        tile_width, tile_height = self.tile_size    # cuz its a tuple

        column = int(x // tile_width)  # going from pixels to tiles
        row  = int(y // tile_height)

        if row < 0 or  column < 0 or row >= self.mid_layer.height or column >= self.mid_layer.width:
    
            return 0, None, 0, 0  # no tile
        
        gID = self.mid_layer.grid[row][column]

        normalized_gID, _, _, _ = normalize_gid(gID) # we only want the first of 4 values returned, not sure this normalizing is strictly necessary though...
        center_tile_rect = None
        if isinstance(self.mid_layer, TileLayer):
            center_tile_rect = self.mid_layer.collisions_grid[row][column]

        return normalized_gID, center_tile_rect , column, row
        # Not implemented because its not my thing. Yet....
        # It should return the ID, NOT GID of the tile in the middle layer ig
    
    # Get the closest interactable from a position in the map
    def get_closest_interactable(self, x, y, max_distance_px: int) -> Interactable | None:
        closest_interactable = None
        closest_distance_sq = max_distance_px * max_distance_px

        for interactable in self.interactables:
            dist_x = interactable.rect.centerx - x
            dist_y = interactable.rect.centery - y
            distance_sq = (dist_x * dist_x) + (dist_y * dist_y)

            if distance_sq <= closest_distance_sq:
                closest_distance_sq = distance_sq
                closest_interactable = interactable

        return closest_interactable



    def _load_interactables(self, interactables_layer: dict | None) -> list[Interactable]:
        if interactables_layer is None:
            return []

        objects = interactables_layer.get("objects", [])
        interactables = []  

        # Parse each object and create appropriate Interactable instance
        for obj in objects:
            name = obj.get("name", "").lower()
            x = obj.get("x", 0)
            y = obj.get("y", 0)
            width = obj.get("width", 0)
            height = obj.get("height", 0)
            
            # Create the appropriate interactable based on the name
            if name == "exit":
                interactables.append(Exit(x, y, width, height))
            elif name == "upgrades":
                interactables.append(Upgrades(x, y, width, height))
            elif name == "research":
                interactables.append(Research(x, y, width, height))

        return interactables

    # Gets the tileset and number of columns in the tileset
    def _load_tileset_surface_and_columns(self, tsx_path: Path) -> tuple[pygame.Surface, int] | tuple[dict, int]:
        tsx_root = ET.parse(tsx_path).getroot()
        column_count = int(tsx_root.attrib["columns"])
        
        # If the tileset is an image collection I want a dictionary with col count instead of the atlas surface
        if column_count == 0:
            image_dict = {}
            for tile_element in tsx_root.findall("tile"):
                tile_id = int(tile_element.attrib["id"])
                image_element = tile_element.find("image")
                if image_element is not None:
                    image_path = (tsx_path.parent / image_element.attrib["source"]).resolve()
                    image_dict[tile_id] = (str(image_path), (image_element.attrib["width"], image_element.attrib["height"]))
            return image_dict, column_count
        
        # Return the atlas surface of the atlas
        else:
            image_element = tsx_root.find("image")
            if image_element is None:
                raise ValueError(f"Tileset image missing in {tsx_path}")
            
            atlas_path = (tsx_path.parent / image_element.attrib["source"]).resolve()
            atlas_surface = pygame.image.load(str(atlas_path)).convert_alpha()
            return atlas_surface, column_count
        


    # We need to change this later prob, rn the whole map is rebuilding always. Would make more sense for only the part inside the camera to be built
    def _build_tile_layers(self) -> pygame.Surface:
        visual_surface = pygame.Surface(self.map_size, pygame.SRCALPHA)
        for layer in self.tile_layers.values():
            visual_surface = self._add_tile_layer_to_surface(layer, visual_surface)
        return visual_surface

        
    
    def _add_tile_layer_to_surface(self, layer: TileLayer | InfiniteTileLayer, dest: pygame.Surface):
        map_tile_width, map_tile_height = self.tile_size
        # for every tile in the grid
        for i, row in enumerate(layer.grid):
            for j, gid in enumerate(row):
                # Get the tile ID and flip da flags
                base_gid, flip_h, flip_v, flip_diagonal = normalize_gid(gid)
                if base_gid == 0:
                    continue

                # Find the tileset this gid belongs to (we sorted the list before descending by firstgid)
                tileset_entry = None
                for firstgid, atlas, columns in self.tilesets:
                    if base_gid >= firstgid:
                        tileset_entry = (firstgid, atlas, columns)
                        break
                if tileset_entry is None:
                    continue

                firstgid, atlas_surface, column_count = tileset_entry
                local_tile_id = base_gid - firstgid

                tile_surface = None
                destination = (j * map_tile_width, i * map_tile_height)
                if isinstance(atlas_surface, pygame.Surface):     # The case where the tileset is an actual atlas
                    # Get the tile image from the atlas
                    source_x = (local_tile_id % column_count) * map_tile_width              # Same thingies as before, moving through the 2d environment of the atlas using a 1 dimensional number.
                    source_y = (local_tile_id // column_count) * map_tile_height            # Column_count can be seen as the width.
                    source_rect = pygame.Rect(source_x, source_y, map_tile_width, map_tile_height)
                    tile_surface = atlas_surface.subsurface(source_rect)

                elif isinstance(atlas_surface, dict):             # The case where the tileset is an image collection
                    tile_width, tile_height = atlas_surface[local_tile_id][1]
                    tile_image_path = Path(atlas_surface[local_tile_id][0])
                    tile_surface = pygame.image.load(str(tile_image_path)).convert_alpha()
                    
                    destination = (destination[0] + map_tile_width - int(tile_width), destination[1] + map_tile_height - int(tile_height))
                    

                if tile_surface is None:
                    raise UnboundLocalError("Something is weird with the tileset and I couldnt get a tile_surface womp womp")
                    
                # Flip the tiles if they were fliped in Tiled
                if flip_diagonal:
                    tile_surface = pygame.transform.rotate(tile_surface, 90) 
                    tile_surface = pygame.transform.flip(tile_surface, False, True)
                if flip_h or flip_v:
                    tile_surface = pygame.transform.flip(tile_surface, flip_h, flip_v)

                # Blit the tile at the right place
                dest.blit(tile_surface, destination)
        return dest