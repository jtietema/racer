# -*- coding: utf-8 -*-
# TODO: improve visually

import sys

from cocos.director import director
from cocos.menu import *
from cocos.scene import Scene
from cocos.layer import MultiplexLayer

from shop import Shop
from race import Race
import cups
from game_state import state
from car import ComputerCar
import profiles


class MenuScene(Scene):
    def __init__(self):
        super(MenuScene, self).__init__()
        
        self.add(MultiplexLayer(
            ProfileMenu(),
            CreateProfileMenu(),
            MainMenu()
        ))

        
class ProfileMenu(Menu):
    def __init__(self):
        super(ProfileMenu, self).__init__('Select a profile')
        
        items = []
        
        self.profiles = profiles.list()
        
        for username in self.profiles:
            items.append(MenuItem(username, self.on_select_profile))
        
        items.append(MenuItem('Create new', self.on_create_profile))
        
        self.create_menu(items, shake(), shake_back())
    
    def on_select_profile(self):
        state.profile = profiles.load(self.profiles[self.selected_index])
        self.parent.switch_to(2)
    
    def on_create_profile(self):
        self.parent.switch_to(1)
    
    def on_quit(self):
        sys.exit()


class CreateProfileMenu(Menu):
    def __init__(self):
        super(CreateProfileMenu, self).__init__('Select a profile')
        
        items = [
            EntryMenuItem('Name', self.on_edit_name, ''),
            MenuItem('Create', self.on_create),
            MenuItem('Cancel', self.on_quit)
        ]
        
        self.value = ''
        
        self.create_menu(items, shake(), shake_back())
    
    def on_edit_name(self, value):
        self.value = value
    
    def on_create(self):
        state.profile = profiles.create(self.value)
        
        # Switch to main menu
        self.parent.switch_to(2)
    
    def on_quit(self):
        self.parent.switch_to(0)


class MainMenu(Menu):
    def __init__(self):
        super(MainMenu, self).__init__('RCr')
        
        items = [
            MenuItem('New game', self.on_new_game),
            MenuItem('Shop', self.on_shop),
            MenuItem('Options', None),
            MenuItem('Quit', sys.exit)
        ]
        
        self.create_menu(items, shake(), shake_back())
    
    def on_new_game(self):
        state.cup = cups.load(cups.list()[0])
        race = Race(state.cup.next_track(), [state.profile.car, ComputerCar.get_default(), ComputerCar.get_default()])
        director.push(race)
    
    def on_shop(self):
        director.push(Shop())
    
    def on_quit(self):
        """Called when the user presses escape."""
        pass
