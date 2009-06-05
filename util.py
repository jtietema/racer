# -*- coding: utf-8 -*-

# This file is part of RCr and copyright (C) Maik Gosenshuis and 
# Jeroen Tietema 2008-09.
#
# RCr is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RCr is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with RCr.  If not, see <http://www.gnu.org/licenses/>.

import math

import cocos
import pyglet

from cocos.layer import ColorLayer

from pymunk import Vec2d

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
    

class Vector:
    """Basic vector implementation"""
    def __init__(self, x, y):
        self.x, self.y = x, y
    def dot(self, other):
        """Returns the dot product of self and other (Vector)"""
        return self.x*other.x + self.y*other.y
    def __add__(self, other): # overloads vec1+vec2
        return Vector(self.x+other.x, self.y+other.y)
    def __neg__(self): # overloads -vec
        return Vector(-self.x, -self.y)
    def __sub__(self, other): # overloads vec1-vec2
        return -other + self
    def __mul__(self, scalar): # overloads vec*scalar
        return Vector(self.x*scalar, self.y*scalar)
    __rmul__ = __mul__ # overloads scalar*vec
    def __div__(self, scalar): # overloads vec/scalar
        return 1.0/scalar * self
    def magnitude(self):
        return math.sqrt(self.x*self.x + self.y*self.y)
    def normalize(self):
        """Returns this vector's unit vector (vector of 
        magnitude 1 in the same direction)"""
        inverse_magnitude = 1.0/self.magnitude()
        return Vector(self.x*inverse_magnitude, self.y*inverse_magnitude)
    
    def perpendicular(self):
        """Returns a vector perpendicular to self"""
        return Vector(-self.y, self.x)
 
class Projection:
    """A projection (1d line segment)"""
    def __init__(self, min, max):
        self.min, self.max = min, max
        
    def intersects(self, other):
        """returns whether or not self and other intersect"""
        return self.max > other.min and other.max > self.min
 
class Polygon:
    def __init__(self, points):
        """points is a list of Vectors"""
        self.points = points
        
        # Build a list of the edge vectors
        self.edges = []
        for i in range(len(points)): # equal to Java's for(int i=0; i<points.length; i++)
            point = points[i]
            next_point = points[(i+1)%len(points)]
            self.edges.append(next_point - point)
        
    def project_to_axis(self, axis):
        """axis is the unit vector (vector of magnitude 1) to project the polygon onto"""
        projected_points = []
        for point in self.points:
            # Project point onto axis using the dot operator
            projected_points.append(point.dot(axis))
        return Projection(min(projected_points), max(projected_points))
        
    def intersects(self, other):
        """returns whether or not two polygons intersect"""
        # Create a list of both polygons' edges
        edges = []
        edges.extend(self.edges)
        edges.extend(other.edges)
        
        for edge in edges:
            axis = edge.normalize().perpendicular() # Create the separating axis (see diagrams)
            
            # Project each to the axis
            self_projection = self.project_to_axis(axis)
            other_projection = other.project_to_axis(axis)
            
            # If the projections don't intersect, the polygons don't intersect
            if not self_projection.intersects(other_projection):
                return False
        
        # The projections intersect on all axes, so the polygons are intersecting
        return True

def print_poly(poly):
    for point in poly.points:
        print 'X', point.x, 'Y', point.y


def absolute_position(node):
    """Calculates the absolute position of a CocosNode as virtual
       coordinates."""
    x, y = node.position

    node = node.parent

    while node:
        x += node.x + node.children_anchor_x
        y += node.y + node.children_anchor_y
        node = node.parent

    return x, y

class curry:
    def __init__(self, fun, *args, **kwargs):
        self.fun = fun
        self.pending = args[:]
        self.kwargs = kwargs.copy()

    def __call__(self, *args, **kwargs):
        if kwargs and self.kwargs:
            kw = self.kwargs.copy()
            kw.update(kwargs)
        else:
            kw = kwargs or self.kwargs

        return self.fun(*(self.pending + args), **kw)


def color_from_hex(hex):
    """Converts a color from its hexadecimal representation into a 3-digit
    RGB tuple."""
    import re
    
    match = re.match(r'^#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$', hex, re.I)
    
    if not match:
        raise RuntimeError('Invalid hex format')
    
    return tuple([int(x, 16) for x in match.groups()])

def verts_img(image):
    """Get verts from an image
    
    This function was taken from the cat_mower game: http://www.pyweek.org/e/sweepeur/
    Copyright remains with the original author (Jaber)
    """
    width = image.width/2;
    height = image.height/2
    p1 = Vec2d(-width,-height); p2 = Vec2d(-width,height)
    p3 = Vec2d(width,height);p4 = Vec2d(width,-height)
    return [p1,p2,p3,p4]

class PymunkNode(cocos.cocosnode.CocosNode):
    """A CocosNode that wraps a Pymunk Body"""
    def __init__(self, *args, **kwargs):
        self.pm_body = None
        self.pm_shape = None
        cocos.cocosnode.CocosNode.__init__(self, *args, **kwargs)
    
    # propertie helpers
    
    def _get_position(self):
        if self.pm_body is None: return
        return self.pm_body.position
    
    def _set_position(self, pos):
        if self.pm_body is None: return
        self.pm_body.position = pos
    
    def _get_x(self):
        if self.pm_body is None: return
        return self.pm_body.position[0]
    
    def _set_x(self, x):
        if self.pm_body is None: return
        self.pm_body.position[0] = x
    
    def _get_y(self):
        if self.pm_body is None: return
        return self.pm_body.position[1]
    
    def _set_y(self, y):
        if self.pm_body is None: return
        self.pm_body.position[1] = y
    
    def _get_rotation(self):
        if self.pm_body is None: return
        return math.degrees(self.pm_body.angle)
    
    def _set_rotation(self, rot):
        if self.pm_body is None: return
        self.pm_body.angle = math.radians(rot)
    
    # properties
    position = property(_get_position, _set_position)
    x = property(_get_x, _set_x)
    y = property(_get_y, _set_y)
    rotation = property(_get_rotation, _set_rotation)