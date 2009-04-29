import cocos
import pyglet

class Label(cocos.text.Label):
    '''Subclass to make cocos Label sane...'''
    def __init__(self, *args, **kwargs):
        if 'option_name' in kwargs:
            self.option_name = kwargs.pop('option_name')
        
        cocos.text.Label.__init__(self, *args, **kwargs)
    
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
