import os
from typing import List
import pygame
import pytmx
from client.layerList import Layer


class MapBackground:
    def __init__(self, tmx_path, x=0, y=0, world_layer: int | Layer = Layer.OVERWORLD):
        if tmx_path is None or tmx_path == "":
            tmx_path = os.path.normpath(
                os.path.join(
                    os.path.dirname(__file__), "..", "tiles", "maps", "main.tmx"
                )
            )
        self.tmx_map = pytmx.load_pygame(tmx_path, pixelalpha=True)
        self.map_image = self.renderWholeTMXMapToSurface(self.tmx_map)

        self.x = x
        self.y = y
        self.x -= self.map_image.get_width() / 2
        self.y -= self.map_image.get_height() / 2
        self.world_layer = (
            world_layer.value if isinstance(world_layer, Layer) else int(world_layer)
        )

    def hexToColour(self, hash_colour):
        red = int(hash_colour[1:3], 16)
        green = int(hash_colour[3:5], 16)
        blue = int(hash_colour[5:7], 16)
        return (red, green, blue)

    def renderWholeTMXMapToSurface(self, tmx_map):
        width = tmx_map.tilewidth * tmx_map.width
        height = tmx_map.tileheight * tmx_map.height

        # This surface could be huge
        surface = pygame.Surface((width, height))

        # Some maps define a base-colour, if so, fill the background with it
        if tmx_map.background_color:
            colour = tmx_map.background_color
            if type(colour) == str and colour[0].startswith("#"):
                colour = self.hexToColour(colour)
                surface.fill(colour)
            else:
                print("ERROR: Background-colour of [" + str(colour) + "] not handled")

        # For every layer defined in the map
        for layer in tmx_map.visible_layers:
            # if the Layer is a grid of tiles
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile_bitmap = tmx_map.get_tile_image_by_gid(gid)
                    if tile_bitmap:
                        surface.blit(
                            tile_bitmap, (x * tmx_map.tilewidth, y * tmx_map.tileheight)
                        )
            # if the Layer is a big(?) image
            elif isinstance(layer, pytmx.TiledImageLayer):
                image = tmx_map.get_tile_image_by_gid(layer.gid)
                if image:
                    surface.blit(image, (0, 0))
            # Layer is a tiled group (woah!)
            elif isinstance(layer, pytmx.TiledObjectGroup):
                print("ERROR: Object Group not handled")

        return surface

    def draw(self, surface: pygame.Surface, offset=(0, 0)):
        x = self.x + offset[0]
        y = self.y + offset[1]
        surface.blit(self.map_image, (x, y))

    @staticmethod
    def draw_all(
        surface,
        offset: tuple[float, float],
        maps: List["MapBackground"],
        active_world_layer: int | None = None,
    ):
        """
        Dessine tout les murs
        """
        if maps:
            if isinstance(maps, list):
                for map in maps:
                    if (
                        active_world_layer is not None
                        and map.world_layer != active_world_layer
                    ):
                        continue
                    map.draw(surface, offset)
            else:
                maps.draw(surface, offset)
