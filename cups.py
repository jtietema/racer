import os
from glob import glob

import cocos

from track import Track


__all__ = ['list', 'load']


CUPS_FOLDER = 'cups'


class Cup(object):
    """Holds the information for the currently selected cup. This object
       also takes care of loading the current track."""
    
    def __init__(self, name):
        f = open(os.path.join(CUPS_FOLDER, name, 'tracklist.txt'), 'r')
        tracklist = f.read()
        self.track_names = tracklist.split('\n')
        self.track_names = filter(None, [s.strip() for s in self.track_names])
        self.current_index = 0
        self.name = name
    
    def has_next_track(self):
        """Returns true if the cup has more tracks, false otherwise."""
        return self.current_index < len(self.track_names)
    
    def next_track(self):
        """Returns the Track instance for the next track, or None
           if no next track was found."""
        if self.has_next_track():
            track_name = self.track_names[self.current_index]
            self.current_index += 1
            return Track(self.name, track_name)
        return None 


def is_valid_cup(name):
    """Checks if a cup with the supplied name exists."""
    return os.path.isdir(os.path.join(CUPS_FOLDER, name))


def list():
    """Lists the available cups."""
    return filter(is_valid_cup, os.listdir(CUPS_FOLDER))


def load(name):
    """Loads the cup specified by the name. Returns the created object."""
    return Cup(name)
