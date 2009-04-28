from cocos.director import director
import pyglet
import rabbyt

from menu import MenuScene
from cup import Cup
import profiles
from game_state import state

director.init(width=1024, height=768, caption='RCr')

pyglet.resource.path = ['img']
pyglet.resource.reindex()

state.profile = profiles.load('maik')
state.cup = Cup('garden')

rabbyt.set_default_attribs()

menu_scene = MenuScene()

director.run(menu_scene)
