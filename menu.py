import sys

import cocos
from cocos.menu import *

from shop import Shop

class MenuScene(cocos.scene.Scene):
    def __init__(self):
        super(MenuScene, self).__init__()
        
        self.add(MainMenu())

class MainMenu(cocos.menu.Menu):
    def __init__(self):
        super(MainMenu, self).__init__('Main Menu')
        
        items = [
            MenuItem('New game', self.new_game),
            MenuItem('Shop', self.shop),
            MenuItem('Options', None),
            MenuItem('Quit', sys.exit)
        ]
        self.create_menu(items, zoom_in(), zoom_out())
    
    def new_game(self):
        pass
    
    def shop(self):
        cocos.director.director.replace(Shop())
