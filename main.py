import cocos
import pyglet

from shop import Shop

pyglet.resource.path = ['img']
pyglet.resource.reindex()

cocos.director.director.init(width=1024, height=768)

shop_scene = Shop()

cocos.director.director.run(shop_scene)
