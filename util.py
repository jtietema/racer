import cocos
import pyglet

class Label(cocos.text.Label):
    '''Subclass to make cocos Label sane...'''
    width   = property(lambda self: self.element.content_width)
    height  = property(lambda self: self.element.content_height)
    text    = property(lambda self: self.element._document.text)


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
