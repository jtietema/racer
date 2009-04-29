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
        config.write(open(os.path.expanduser('~/.RCr.cfg'), 'w'))


def list():
    """Returns a list of all available usernames that have a profile."""
    return config.sections()


def load(name):
    """Loads a previously stored profile."""
    money = config.getint(name, 'money')
    return Profile(name, money=money)


def create(name):
    """Creates a new profile with the supplied name."""
    if not config.has_section(name):
        config.add_section(name)
        config.set(name, 'money', 0)
    profile = Profile(name)
    profile.save()
    return profile
