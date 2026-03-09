import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pygame

# https://doc.mapeditor.org/en/latest/reference/global-tile-ids/ * mic drop *
FLIPPED_HORIZONTALLY_FLAG = 0x80000000
FLIPPED_VERTICALLY_FLAG = 0x40000000
FLIPPED_DIAGONALLY_FLAG = 0x20000000
DIAGONAL_FLIP_FLAG = 0x20000000
ALL_FLIP_FLAGS = (FLIPPED_HORIZONTALLY_FLAG | FLIPPED_VERTICALLY_FLAG | FLIPPED_DIAGONALLY_FLAG | FLIPPED_DIAGONALLY_FLAG)

class Layer:
    def __init__(self, layer_data: dict) -> None:
        self.name: str = layer_data.get("name", "")
        self.id: int = layer_data.get("id", 0)
        self.opacity: float = layer_data.get("opacity", 1.0)
        self.visible: bool = layer_data.get("visible", True)
        self.type: str = layer_data.get("type", "")

class TileLayer(Layer):
    def __init__(self, layer: dict) -> None:
        super().__init__(layer)
        self.width: int = layer.get("width", 0)
        self.height: int = layer.get("height", 0)
        self.x: int = layer.get("x", 0)
        self.y: int = layer.get("y", 0)


        self.grid = self.build(layer.get("data", []))

    def build(self, data):
        grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        for i, gid in enumerate(data):
            grid[i // self.width][i % self.width] = gid
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
        self.mid_layer: InfiniteTileLayer | TileLayer
        self.first_gid = 1

        self.parse_from_path(path)

    def parse_from_path(self, path: Path):
        with path.open("r", encoding="utf-8") as f:
            tile_map = json.load(f)
        
        # Someone pls change this latter im begging you it would be nice to have proper errors pls pls pls thanks.
        if tile_map is None:
            return "I like ice cream and the path you gave is wrong womp womp"
        
        # Get em facts from the tiled json file
        self.tile_size = (tile_map["tilewidth"], tile_map["tileheight"])

        mid_layer = next((layer for layer in tile_map["layers"] if layer.get("name") == "Midground"), None)
        if mid_layer is None:
            return "I see another error which need to be raised over here"

        # ===== Building the mid_layer, it can be either finite or infinite
        if tile_map["infinite"] == True:
            self.mid_layer = InfiniteTileLayer(mid_layer)
        else:
            self.mid_layer = TileLayer(mid_layer)

        # Extract the map size
        self.map_size = (
            self.mid_layer.width * self.tile_size[0],
            self.mid_layer.height * self.tile_size[1],
        )

        # Getting the data for the tileset which is the building block for the tilemap, this is like this just for now bc there is only one tileset.
        tileset_data = tile_map["tilesets"][0]
        self.first_gid = int(tileset_data["firstgid"])

        # Just getting the tileset path which is already included in the tilemap
        tsx_path = (path.parent / tileset_data["source"]).resolve()
        atlas_surface, column_count = self._load_tileset_surface_and_columns(tsx_path)
        self.visual_layer = self._build_visual_layer(atlas_surface, column_count)


    def draw(self, world_surface: pygame.Surface, camera_rect: pygame.Rect, position: tuple[int, int] = (0, 0)) -> None:
        if self.visual_layer is not None:
            world_surface.blit(self.visual_layer, camera_rect.topleft, camera_rect)


    def is_tile_solid(self, x, y) -> bool:
        gid = self.get_tile_at_position(x, y)
        # Not implemented because its not my thing. Yet....
        return True


    def get_tile_at_position(self, x, y) -> int:
        # Not implemented because its not my thing. Yet....
        return 1 # It should return the ID, NOT GID of the tile in the middle layer ig
    
    # Gets the tileset and number of columns in the tileset
    def _load_tileset_surface_and_columns(self, tsx_path: Path) -> tuple[pygame.Surface, int]:
        tsx_root = ET.parse(tsx_path).getroot()
        column_count = int(tsx_root.attrib["columns"])

        image_element = tsx_root.find("image")
        if image_element is None:
            raise ValueError(f"Tileset image missing in {tsx_path}")

        atlas_path = (tsx_path.parent / image_element.attrib["source"]).resolve()
        atlas_surface = pygame.image.load(str(atlas_path)).convert_alpha()
        return atlas_surface, column_count

    # Just takes the info from the gid
    def _normalize_gid(self, encoded_gid: int) -> tuple[int, bool, bool, bool]:
        base_gid = encoded_gid & ~ALL_FLIP_FLAGS
        flip_h = bool(encoded_gid & FLIPPED_HORIZONTALLY_FLAG)
        flip_v = bool(encoded_gid & FLIPPED_VERTICALLY_FLAG)
        flip_diagonal = bool(encoded_gid & DIAGONAL_FLIP_FLAG)
        return base_gid, flip_h, flip_v, flip_diagonal

    # We need to change this later prob, rn the whole map is rebuilding always. Would make more sense for only the part inside the camera to be built
    def _build_visual_layer(self, atlas_surface: pygame.Surface, column_count: int) -> pygame.Surface:
        # Create a transparent surface to draw tiles on top of
        tile_width, tile_height = self.tile_size
        visual_layer = pygame.Surface(self.map_size, pygame.SRCALPHA)

        # for every tile in the grid
        for i, row in enumerate(self.mid_layer.grid):
            for j, gid in enumerate(row):
                # Get the tile ID and flip da flags
                base_gid, flip_h, flip_v, flip_diagonal = self._normalize_gid(gid)
                if base_gid == 0:
                    continue

                # Calculate the local tile ID from the tileset (first_gid tells you where the numbers from each tileset start)
                local_tile_id = base_gid - self.first_gid
                if local_tile_id < 0:
                    continue

                # Get the tile image from the atlas
                source_x = (local_tile_id % column_count) * tile_width              # Same thingies as before, moving through the 2d environment of the atlas using a 1 dimensional number.
                source_y = (local_tile_id // column_count) * tile_height            # Column_count can be seen as the width.
                source_rect = pygame.Rect(source_x, source_y, tile_width, tile_height)
                tile_surface = atlas_surface.subsurface(source_rect)

                # Flip the tiles if they were fliped in Tiled
                if flip_diagonal:
                    tile_surface = pygame.transform.rotate(tile_surface, 90) 
                    tile_surface = pygame.transform.flip(tile_surface, False, True)
                if flip_h or flip_v:
                    tile_surface = pygame.transform.flip(tile_surface, flip_h, flip_v)

                # Blit the tile at the right place
                destination = (j * tile_width, i * tile_height)
                visual_layer.blit(tile_surface, destination)

        return visual_layer
