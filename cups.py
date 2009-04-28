import os
from glob import glob

import tiled2cocos


__all__ = ['list', 'load']


CUPS_FOLDER = 'cups'


class Cup(object):
    """Holds the information for the currently selected cup. This object
       also takes care of loading the current map."""
    
    def __init__(self, name):
        # TODO: apply sorting
        # TODO: add configuration files
        self.map_files = glob(os.path.join(CUPS_FOLDER, name, '*.tmx'))
        self.current_index = 0
    
    def has_next_map(self):
        """Returns true if the cup has more maps, false otherwise."""
        return self.current_index < len(self.map_files)
    
    def next_map(self):
        """Returns the RectMapLayer instance for the next map, or None
           if no next map was found."""
        if self.has_next_map():
            map_path = self.map_files[self.current_index]
            self.current_index += 1
            return tiled2cocos.load_map(map_path)
        
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
