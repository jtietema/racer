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

import pyglet.image
import bisect
import os.path
from ConfigParser import RawConfigParser

from cocos.sprite import Sprite


# Only expose manager singleton instance.
__all__ = ['manager', 'CLASSES']


class PartManager(object):
    """Loads the available parts from config files and converts them to
       appropriate objects."""
    
    def __init__(self):
        self.parts_cache = {}
    
    def get_part_by_id(self, part_type, part_id):
        for part in self.get_parts_by_type(part_type):
            if part.part_id == part_id:
                return part
        
        return None
            
    def get_parts_by_type(self, part_type):
        """Lazily loads in the parts from the config file. Turns the
           config file data into subclasses of Part."""
        if not part_type in self.parts_cache:
            self.parts_cache[part_type] = self.load_parts_by_type(part_type)
        
        return self.parts_cache[part_type]
        
    def load_parts_by_type(self, part_type):
        """Loads the parts from the config file and turns them into
           appropriate objects. This method should never be called directly,
           as it is used internally by get_parts_by_type(), which maintains
           a cache for optimal performance."""
        config = RawConfigParser()
        config.read(os.path.join('parts', part_type + '.cfg'))
        
        parts = []
        part_class = CLASSES[part_type]
        
        for part_id in config.sections():            
            properties = dict(config.items(part_id))            
            part = part_class(part_id, **properties)
            bisect.insort(parts, part)
        
        return parts

# Singleton
manager = PartManager()


class Part(object):
    """Abstract superclass of parts."""
    
    @classmethod
    def load_from_dict(cls, properties):
        if not 'image' in properties:
            properties['image'] = None
        
        return cls(**properties)
    
    @classmethod
    def pretty_name(cls):
        """Returns a human-readable version of the class name."""
        return str(cls)
    
    def __init__(self, part_id, name, image, price):
        self.part_id = part_id
        self.name = name
        self.image = image
    
        self.price = int(price)
        
        self._sprite = None
    
    def __cmp__(self, other):
        # By default, sort by price.
        return cmp(self.price, other.price)
    
    def __eq__(self, other):
        # Compare the part by id by default.
        return self.part_id == other.part_id
    
    def __repr__(self):
        return self.part_id
    
    def _get_sprite(self):
        if self._sprite is None:    
            if self.image is None:
                raise NotImplementedError("Part does not have an image.")
            
            self._sprite = Sprite(self.image)
        
        return self._sprite
    sprite = property(_get_sprite, doc="""Creates a sprite instance for the
        part on the fly. Note that the created object is cached, so later
        calls will return the same instance.""")


class Body(Part):
    def __init__(self, part_id, name, image, price, mass, tyres_fx_offset,
        tyres_fy_offset, tyres_bx_offset, tyres_by_offset):
        
        super(Body, self).__init__(part_id, name, image, price)
        
        self.mass = float(mass)
        
        self.tyres_fx_offset = int(tyres_fx_offset)
        self.tyres_fy_offset = int(tyres_fy_offset)
        self.tyres_bx_offset = int(tyres_bx_offset)
        self.tyres_by_offset = int(tyres_by_offset)


class Engine(Part):
    def __init__(self, part_id, name, price, power):
        super(Engine, self).__init__(part_id, name, None, price)
        
        self.power = float(power)


class Tyres(Part):
    def __init__(self, part_id, name, image, price, grip):
        super(Tyres, self).__init__(part_id, name, image, price)
        
        self.grip = float(grip)


# Used for validation of input parameters, and prevents ugly class lookups
# by string name.
CLASSES = {
    'body': Body,
    'engine': Engine,
    'tyres': Tyres
}
