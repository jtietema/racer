import cocos
import rabbyt
import pyglet

class RabbytLayer(cocos.layer.Layer):
    '''Class for transparent rendering of rabbyt sprites in cocos2d'''
    def __init__(self):
        super(RabbytLayer, self).__init__()
        
        self.rabbyt_sprites = []
    
    def add(self, sprite):
        self.rabbyt_sprites.append(sprite)
    
    def remove(self, sprite):
        self.rabbyt_sprites.remove(sprite)
    
    def draw(self):
        for sprite in self.rabbyt_sprites:
            sprite.render()

class SpriteText(rabbyt.BaseSprite):
    def __init__(self, ft, text="", *args, **kwargs):
        rabbyt.BaseSprite.__init__(self, *args, **kwargs)
        self._text = pyglet.font.Text(ft, text)

    def setText(self, text):
        self._text.text = text

    def render_after_transform(self):
        self._text.color = self.rgba
        self._text.draw()
