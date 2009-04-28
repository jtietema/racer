import cocos
import pyglet

class Label(cocos.text.Label):
    '''Subclass to make cocos Label sane...'''
    def _get_width(self):
        return self.element.content_width
    width = property(_get_width)
    
    def _get_height(self):
        return self.element.content_height
    height = property(_get_height)

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
    
    def getText(self):
        return self.element._document.text


def collide_single((x,y), objects):
    collisions = []
    for ob in objects:
        if ob.x < x < (ob.x + ob.width):
            if ob.y < y < (ob.y + ob.height):
                collisions.append(ob)
    return collisions

    def render_after_transform(self):
        self._text.color = self.rgba
        self._text.draw()


def signum(number):
    """This should be in Python's standard library."""
    if number > 0: return 1
    elif number < 0: return -1
    return number
