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

import os
from ConfigParser import ConfigParser

from car import PlayerCar


__all__ = ['list', 'load', 'create']

global config
config = ConfigParser()
config.read(os.path.expanduser('~/.RCr.cfg'))


class Profile(object):
    """Represents a player profile."""    
    def __init__(self, name, car=None, money=None):
        self.name = name
        self.car = (car or PlayerCar.get_default())
        
        assert isinstance(self.car, PlayerCar)
        
        self.money = (money or 0)
    
    def save(self):
        """Writes the profile to disk."""
        if not config.has_section(self.name):
            config.add_section(self.name)
        config.set(self.name, 'money', self.money)
        config.set(self.name, 'body', self.car.body)
        config.set(self.name, 'tyres', self.car.tyres)
        config.set(self.name, 'engine', self.car.engine)
        
        config.write(open(os.path.expanduser('~/.RCr.cfg'), 'w'))


def list():
    """Returns a list of all available usernames that have a profile."""
    return config.sections()


def load(name):
    """Loads a previously stored profile."""
    money = config.getint(name, 'money')
    body = config.get(name, 'body')
    engine = config.get(name, 'engine')
    tyres = config.get(name, 'tyres')
    car = PlayerCar(body=body, engine=engine, tyres=tyres)
    return Profile(name, car, money)


def create(name):
    """Creates a new profile with the supplied name."""
    profile = Profile(name)
    profile.save()
    return profile
