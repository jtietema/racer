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
        self.results = {}
    
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
    
    def set_results_for_current_track(self, results):
        self.results[self.current_index] = results
    
    def _get_total_ranking(self):
        """Calculates the total ranking of the cup based on the results
           that have thus far been added."""
        ranking = {}
        for results in self.results.values():
            for pos, stats in enumerate(results):
                ranking[stats.car] = ranking.get(stats.car, 0) + (pos * stats.total_time)
                
        ranking = dict([(v, k) for (k, v) in ranking.iteritems()])
        scores = ranking.keys()
        scores.sort()
                
        return [ranking[score] for score in scores]
    total_ranking = property(_get_total_ranking)


def is_valid_cup(name):
    """Checks if a cup with the supplied name exists."""
    return os.path.isdir(os.path.join(CUPS_FOLDER, name))


def list():
    """Lists the available cups."""
    return filter(is_valid_cup, os.listdir(CUPS_FOLDER))


def load(name):
    """Loads the cup specified by the name. Returns the created object."""
    return Cup(name)
