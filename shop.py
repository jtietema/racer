import os

import cocos
import pyglet

import util
import parts
from game_state import state

class Shop(cocos.scene.Scene):
    def __init__(self):
        super( Shop, self ).__init__()
        self.add(ShopBackground())

class ShopBackground(cocos.layer.Layer):
    def __init__(self):
        super(ShopBackground, self).__init__()
        
        background = cocos.sprite.Sprite('shop_background.png')
        background.position = 1024/2, 768/2
        self.add(background, z=-1)
        
        car = state.profile.car
        car.position = (300, 500)
        car.scale = 1
        self.add(car)
        
        self.add(OptionsWidget())

class OptionsWidget(cocos.layer.Layer):
    '''Widget on the right side of the screen showing all the parts you can buy
    '''
    def __init__(self):
        super(OptionsWidget, self).__init__()
        
        self.font = ['Sans']
        arrow_left = util.Label("<", position=(725, 700), color=(0,0,0,255), font_name=self.font
            , font_size=16)
        arrow_right = util.Label(">", position=(925, 700), color=(0,0,0,255), font_name=self.font, 
            font_size=16)
        self.add(arrow_left)
        self.add(arrow_right)
        self.controls = [arrow_left, arrow_right]
        self.controls_items = []
        cocos.director.director.window.push_handlers(self.on_mouse_press)
        
        self.options = self.options_to_sprites(parts.options['tyres'])
        self.index = 0
        self.option_name = util.Label('Tyres', 
            position=(750, 700), color=(0,0,0,255), font_name=self.font, 
            font_size=16)
        self.add_options()
        
        self._car_properties = {}
        self.set_car_properties(7,5,6)
        
    def on_mouse_press(self, x, y, button, modifiers):
        '''Mouse key pressed event
        '''
        # check if controls on spinner box are clicked
        collisions = util.collide_single((x,y), self.controls)
        if len(collisions) != 0:
            # remove all options
            self.remove_options()
            # manipulate the index of the spinner box
            if collisions[0] is self.controls[0]:
                self.index += 1
            elif collisions[0] is self.controls[1]:
                self.index -= 1
            # normalize index
            self.index = self.index % len(parts.index)
            # repopulate spinnerbox
            self.options = self.options_to_sprites(
                parts.options[parts.index[self.index]])
            self.option_name = util.Label(parts.index[self.index], 
                position=(750, 700), color=(0,0,0,255), font_name=self.font, 
                font_size=16)
            self.add_options()
        
        # check if one of the items was pressed
        collisions = util.collide_single((x,y), self.controls_items)
        if len(collisions) != 0:
            # check which option was pressed
            option_name = collisions[0].getText()
            print option_name, collisions[0].position
    
    def options_to_sprites(self, options):
        '''Converts options to SpriteText objects
        '''
        sprites = []
        y = 675
        for option in options.values():
            sprites.append(util.Label(option['name'], position=(750, y), 
                color=(0,0,0,255), font_name=self.font, font_size=16))
            y -= 25
        return sprites
    
    def add_options(self):
        '''Add all options to the layer and to the items list
        '''
        self.controls_items = []
        self.add(self.option_name)
        for option in self.options:
            self.add(option)
            self.controls_items.append(option)
    
    def remove_options(self):
        '''Remove all options to the layer'''
        self.remove(self.option_name)
        for option in self.options:
            self.remove(option)
    
    def set_car_properties(self, power, friction, mass):
        '''Set the car stats/properties on the shop display
        '''
        # remove previous properties
        for key, prop in self._car_properties:
            self.remove(prop)
        
        # set new properties
        self._car_properties = {
            'power': util.Label('Power: ' + str(power), position=(100, 200),
                color=(0,0,0,255), font_name=self.font, font_size=16), 
            'friction': util.Label('Friction: ' + str(friction), position=(100, 175),
                color=(0,0,0,255), font_name=self.font, font_size=16),
            'mass': util.Label('Mass: ' + str(mass), position=(100, 150),
                color=(0,0,0,255), font_name=self.font, font_size=16)
        }
        for key, prop in self._car_properties.items():
            self.add(prop)

