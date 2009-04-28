# TODO: list, load and save from real settings files.
from car import PlayerCar


__all__ = ['list', 'load', 'create']


class Profile(object):
    """Represents a player profile."""    
    def __init__(self, name, car=None, money=None):
        self.name = name
        self.car = (car or PlayerCar.get_default())
        
        assert isinstance(self.car, PlayerCar)
        
        self.money = (money or 0)
    
    def save(self):
        """Writes the profile to disk."""
        pass


def list():
    """Returns a list of all available usernames that have a profile."""
    return ['maik']


def load(name):
    """Loads a previously stored profile."""
    return Profile(name)


def create(name):
    """Creates a new profile with the supplied name."""
    profile = Profile(name)
    profile.save()
    return profile
