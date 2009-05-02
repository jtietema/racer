import os

from cocos.director import director
import pyglet

from menu import MenuScene
from cups import Cup
import profiles
from game_state import state

director.init(width=1024, height=768, caption='RCr: Larry\'s Lawn')

pyglet.resource.path = ['img', os.path.join('cups', 'garden')]
pyglet.resource.reindex()

state.cup = Cup('garden')

menu_scene = MenuScene()

director.run(menu_scene)
