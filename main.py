import cocos
import pyglet

from menu import MenuScene

pyglet.resource.path = ['img']
pyglet.resource.reindex()

cocos.director.director.init(width=1024, height=768,
    caption="Racer game with uber cool title")


menu_scene = MenuScene()

cocos.director.director.run(menu_scene)

