import sys

import cocos
from cocos.director import director
from cocos.menu import *

from shop import Shop
from race import Race
import cups
from game_state import state

class MenuScene(cocos.scene.Scene):
    def __init__(self):
        super(MenuScene, self).__init__()
        
        self.add(MainMenu())

class MainMenu(Menu):
    def __init__(self):
        super(MainMenu, self).__init__('Main Menu')
        
        items = [
            MenuItem('New game', self.on_new_game),
            MenuItem('Shop', self.on_shop),
            MenuItem('Options', None),
            MenuItem('Quit', self.on_quit)
        ]
        
        self.create_menu(items, shake(), shake_back())
    
    def on_new_game(self):
        state.cup = cups.load(cups.list()[0])
        race = Race(state.cup.next_map(), [state.profile.car])
        director.replace(race)
    
    def on_shop(self):
        director.replace(Shop())
    
    def on_quit(self):
        """Called when the user presses escape."""
        sys.exit()
