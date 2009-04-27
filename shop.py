import os

import cocos

class Shop(cocos.scene.Scene):
    def __init__(self):
        super( Shop, self ).__init__()
        color_layer = cocos.layer.util_layers.ColorLayer(0, 255, 255, 0)
        color_layer.position = 1024/2, 768/2
        self.add(color_layer)
        self.add(ShopBackground())

class ShopBackground(cocos.layer.Layer):
    def __init__(self):
        super( ShopBackground, self ).__init__()
        
        background = cocos.sprite.Sprite('shop_background.png')
        background.position = 1024/2, 768/2
        self.add(background)
        
        car = cocos.sprite.Sprite('car.png')
        car.position = 300, 500
        self.add(car)


