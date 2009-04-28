from cocos.director import director
from cocos.scene import Scene
import cocos.tiles
import tiled2cocos

from car import Car, PlayerCar

director.init(caption='Car behaviour', width=1024, height=768)

map_layer = tiled2cocos.load_map('map.tmx')
sprites_layer = cocos.tiles.ScrollableLayer()

scroller = cocos.tiles.ScrollingManager()
scroller.add(map_layer)
scroller.add(sprites_layer)

player = PlayerCar(1, (map_layer.px_width // 2, map_layer.px_height // 2))
sprites_layer.add(player)

scroller.set_focus(player.x, player.y)

director.show_FPS = True
director.run(Scene(scroller))
