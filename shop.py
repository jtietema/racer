import os
from string import capwords

import cocos
from cocos.director import director
from cocos.layer import Layer
from cocos.scene import Scene
import pyglet

import util
import parts
from game_state import state

class Shop(Scene):
    def __init__(self):
        super( Shop, self ).__init__()
        self.add(ShopBackground())

class ShopBackground(Layer):
    def __init__(self):
        super(ShopBackground, self).__init__()
        
        background = cocos.sprite.Sprite('shop_background.png')
        background.position = 1024/2, 768/2
        self.add(background, z=-1)
        
        car = state.profile.car
        car.position = (300, 500)
        car.scale = 1
        self.add(car)
        
        self.add(OptionsWidget(parts.options))

class OptionsWidget(Layer):
    '''Widget on the right side of the screen showing all the parts you can buy
    '''
    def __init__(self, options):
        super(OptionsWidget, self).__init__()
        
        self.font = ['Sans']
        
        self.build_panel()
        
        self.options = options
        
        self.groups = options.keys()
        self.group_index = 0
        
        self.option_sprites = []
        self.load_options(self.groups[self.group_index])
        
        director.window.push_handlers(self.on_mouse_press)
        
        # self._car_properties = {}
        # self.set_car_properties(7,5,6)
    
    def build_panel(self):
        arrow_left = util.Label("<", position=(725, 700), color=(0,0,0,255), font_name=self.font
            , font_size=16)
        arrow_right = util.Label(">", position=(925, 700), color=(0,0,0,255), font_name=self.font, 
            font_size=16)
        self.add(arrow_left)
        self.add(arrow_right)
        self.controls = [arrow_left, arrow_right]
        
        self.group_caption = util.Label('', 
            position=(750, 700), color=(0,0,0,255), font_name=self.font, 
            font_size=16)
        self.add(self.group_caption)
    
    def clear_options(self):
        """Removes all the options that are currently added. Also clears
           the group caption label."""
        for option in self.option_sprites:
            self.remove(option)
        self.option_sprites = []
        self.group_caption.text = ''
    
    def load_options(self, group_name):
        """Loads in new options based on the group name. Also sets the
           group caption label by capitalizing all words in the group
           identifier."""
        y = 675
        for option_name, properties in self.options[group_name].items():
            label = util.Label(properties['name'],
                position=(750, y), color=(0,0,0,255), font_name=self.font,
                font_size=16, option_name=option_name)
            self.add(label)
            self.option_sprites.append(label)
            y -= 25
        
        self.group_caption.text = capwords(group_name)
        
    def on_mouse_press(self, x, y, button, modifiers):
        """Called when the user clicks."""
        
        # Test for clicks on one of the spinner controls.
        collisions = util.collide_single((x,y), self.controls)
        if len(collisions) > 0:
            self.clear_options()
            
            if collisions[0] is self.controls[0]:
                self.group_index += 1
            elif collisions[0] is self.controls[1]:
                self.group_index -= 1
            
            # Normalize the index.
            self.group_index = self.group_index % len(self.groups)
            
            # Repopulate spinnerbox.
            self.load_options(self.groups[self.group_index])
            
            # If we have clicked one of the spinner controls, we can be
            # sure that no options has been clicked. No point in continuing.
            return
        
        # Check if one of the items was pressed.
        collisions = util.collide_single((x,y), self.option_sprites)
        if len(collisions) > 0:
            option_name = collisions[0].option_name
            setattr(state.profile.car, self.groups[self.group_index], option_name)
            
            return
    
    # def set_car_properties(self, power, friction, mass):
    #     '''Set the car stats/properties on the shop display
    #     '''
    #     # remove previous properties
    #     for key, prop in self._car_properties:
    #         self.remove(prop)
    #     
    #     # set new properties
    #     self._car_properties = {
    #         'power': util.Label('Power: ' + str(power), position=(100, 200),
    #             color=(0,0,0,255), font_name=self.font, font_size=16), 
    #         'friction': util.Label('Friction: ' + str(friction), position=(100, 175),
    #             color=(0,0,0,255), font_name=self.font, font_size=16),
    #         'mass': util.Label('Mass: ' + str(mass), position=(100, 150),
    #             color=(0,0,0,255), font_name=self.font, font_size=16)
    #     }
    #     for key, prop in self._car_properties.items():
    #         self.add(prop)

