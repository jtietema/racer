import os

import cocos
import rabbyt
import pyglet

import util
import parts

class Shop(cocos.scene.Scene):
    def __init__(self):
        super( Shop, self ).__init__()
        color_layer = cocos.layer.util_layers.ColorLayer(0, 255, 255, 0)
        color_layer.position = 1024/2, 768/2
        self.add(color_layer)
        self.add(ShopBackground())

class ShopBackground(util.RabbytLayer):
    def __init__(self):
        super(ShopBackground, self).__init__()
        
        
        font = pyglet.font.load('Sans', 16)
        text = util.SpriteText(font, "test", xy=(320,240))
        
        background = rabbyt.Sprite(os.path.join('img','shop_background.png'))
        background.xy = 1024/2, 768/2
        self.add(background)
        
        car = rabbyt.Sprite(os.path.join('img','car.png'))
        car.xy = 300, 500
        self.add(car)
        
        font = pyglet.font.load('Sans', 16)
        text = util.SpriteText(font, "test", xy=(320,240), rgb=(0,0,0))
        self.add(text)
        
        options = OptionsWidget()
        cocos.layer.Layer.add(self,options)

class OptionsWidget(util.RabbytLayer):
    '''Widget on the right side of the screen showing all the parts you can buy
    '''
    def __init__(self):
        super(OptionsWidget, self).__init__()
        
        self.font = pyglet.font.load('Sans', 16)
        arrow_left = util.SpriteText(self.font, "<", xy=(725,700), rgb=(0,0,0))
        arrow_right = util.SpriteText(self.font, ">", xy=(925,700), rgb=(0,0,0))
        self.add(arrow_left)
        self.add(arrow_right)
        self.controls = [arrow_left, arrow_right]
        cocos.director.director.window.push_handlers(self.on_mouse_press)
        
        self.options = self.options_to_sprites(parts.options['tyres'])
        self.index = 0
        self.option_name = util.SpriteText(self.font, 'Tyres', 
            xy=(750, 700), rgb=(0,0,0))
        self.add_options()
        
    def on_mouse_press(self, x, y, button, modifiers):
        '''Mouse key pressed event
        '''
        # check if controls on spinner box are clicked
        collisions = rabbyt.collisions.collide_single((x,y, 15), self.controls)
        if len(collisions) != 0:
            # remove all options
            self.remove_options()
            # manipulate the index of the spinner box
            if collisions[0] is self.controls[0]:
                self.index += 1
            elif collisions[0] is self.controls[1]:
                self.index -= 1
            # normalize index
            self.index = self.index % parts.mod
            # repopulate spinnerbox
            self.options = self.options_to_sprites(
                parts.options[parts.index[self.index]])
            self.option_name = util.SpriteText(self.font, 
                parts.index[self.index], xy=(750, 700), rgb=(0,0,0))
            self.add_options()
    
    def options_to_sprites(self, options):
        '''Converts options to SpriteText objects
        '''
        sprites = []
        y = 675
        for option in options:
            sprites.append(util.SpriteText(self.font, 
                option['name'], xy=(750, y), rgb=(0,0,0)))
            y -= 25
        return sprites
    
    def add_options(self):
        '''Add all options to the layer'''
        self.add(self.option_name)
        for option in self.options:
            self.add(option)
    
    def remove_options(self):
        '''Remove all options to the layer'''
        self.remove(self.option_name)
        for option in self.options:
            self.remove(option)



