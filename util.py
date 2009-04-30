import cocos
import pyglet
from cocos.layer import ColorLayer

class Label(cocos.text.Label):
    '''Subclass to make cocos Label sane...'''
    def __init__(self, *args, **kwargs):
        # Properties can be used to store additional data on the label.
        if 'properties' in kwargs:
            self.properties = kwargs.pop('properties')
        else:
            self.properties = {}
        
        # An optional background can be rendered behind the label.
        has_bg = ('background' in kwargs)
        if has_bg:
            bg = kwargs.pop('background')
        
        cocos.text.Label.__init__(self, *args, **kwargs)
        
        if has_bg:
            bg_layer = ColorLayer(*bg, **{'width': self.width, 'height': self.height})
            self.add(bg_layer, z=-1)
    
    width   = property(lambda self: self.element.content_width)
    height  = property(lambda self: self.element.content_height)
    
    def _set_text(self, txt):
        self.element._document.text = txt
    text    = property(lambda self: self.element._document.text, _set_text)


def collide_single((x,y), objects):
    collisions = []
    for ob in objects:
        if ob.x < x < (ob.x + ob.width):
            if ob.y < y < (ob.y + ob.height):
                collisions.append(ob)
    return collisions


def signum(number):
    """This should be in Python's standard library."""
    if number > 0: return 1
    elif number < 0: return -1
    return number


def ordinal(n):
    """Converts a number into an ordinal numbers"""
    return str(n) + {1 : 'st', 2 : 'nd', 3 : 'rd'}.get(n % 10, 'th')


def flip_dict(d):
    """Flips the keys and the values of a dictionary."""
    return dict([(v, k) for (k, v) in d.iteritems()])
