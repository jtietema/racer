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
    
    def getText(self):
        return self.element._document.text

def collide_single((x,y), objects):
    collisions = []
    for ob in objects:
        if ob.x < x < (ob.x + ob.width):
            if ob.y < y < (ob.y + ob.height):
                collisions.append(ob)
    return collisions


