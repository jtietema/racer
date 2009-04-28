import cocos
import pyglet
import rabbyt

from menu import MenuScene

pyglet.resource.path = ['img']
pyglet.resource.reindex()

cocos.director.director.init(width=1024, height=768,
    caption="Racer game with uber cool title")

rabbyt.set_default_attribs()


menu_scene = MenuScene()

cocos.director.director.run(menu_scene)

