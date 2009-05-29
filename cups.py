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

import cocos

from track import Track
import util


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
                
        # Swap keys and values
        ranking = util.flip_dict(ranking)
        
        # Sort the keys.
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
