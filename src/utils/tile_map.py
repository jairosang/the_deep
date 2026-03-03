from pygame import Surface
from pathlib import Path
import json

class Layer:
    def __init__(self, layer_data: dict) -> None:
        self.name: str = layer_data.get("name", "")
        self.id: int = layer_data.get("id", 0)
        self.opacity: float = layer_data.get("opacity", 1.0)
        self.visible: bool = layer_data.get("visible", True)
        self.offset_x: float = layer_data.get("offsetx", 0)
        self.offset_y: float = layer_data.get("offsety", 0)
        self.type: str = layer_data.get("type", "")


class TileLayer(Layer):
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
            # The position is not starting from zero which is not nice because an index cant be negative in an array yk so I fixed it
            norm_x = chunk["x"] - self.start_x
            norm_y = chunk["y"] - self.start_y
            
            # This guy just transferst the i horizontal movement accross the chunk array into 2d array for the grid and assigns the corresponding chunk_data 
            chunk_data = chunk["data"]
            for i, el in enumerate(chunk_data):
                grid[norm_y + (i // chunk["height"])][norm_x + (i % chunk["width"])] = chunk_data[i]

        return grid





class ImageLayer(Layer):
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
        self.visual_layer: Surface
        self.collision_layer: list[list[int]]
        self.tile_size: tuple[int,int]
        self.map_size: tuple[int,int]

    # Not done
    def parse_from_path(self, path: Path):

        path = Path("./assets/tilemap/underwater_tilemap.tmj")
        with path.open("r", encoding="utf-8") as f:
            tile_map = json.load(f)
        
        # Someone pls change this latter im begging you it would be nice to have proper errors pls pls pls thanks.
        if tile_map == None:
            return "I like ice cream and the path you gave is wrong womp womp"
        

        # Get em facts from the tiled json file
        self.tile_size = (tile_map["tilewidth"], tile_map["tileheight"])

        # Missing error handling if name midground is not there
        mid_layer = [l for l in tile_map["layers"] if l.get("name") == "Midground"][0]
        self.mid_layer = TileLayer(mid_layer)
        


    


    
    # Not done
    def get_visual_layer(self) -> Surface:
        return self.visual_layer

    # Not done
    def is_tile_solid(self, x, y) -> bool:
        return True
    
    # Not done
    def get_tile_at_position(self, x, y):
        pass