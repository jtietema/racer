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

from cocos.director import director
from cocos.scene import Scene
from cocos.layer import Layer

from util import Label
from game_state import state
from car import ComputerCar

class LoadTrack(Scene):
    
    def __init__(self, track):
        Scene.__init__(self)
        self.text = 'Loading...'
        self.track = track
        self.layer = Layer()
        self.label = Label(self.text + '0%', position=(100,100))
        self.layer.add(self.label)
        self.add(self.layer)
        
        self.schedule(self.load_track)
        
        self.images_loaded = False
        self.overlay_loaded = False
    
    def load_track(self, dt, *args, **kwargs):
        if not self.images_loaded:
            self.track.load_images()
            self.label.text = self.text + '5%'
            self.total = len(self.track.partition_list)
            self.images_loaded = True
        elif not self.overlay_loaded:
            self.track.load_overlay()
            self.label.text = self.text + '25%'
            self.overlay_loaded = True
        else:
            partitions_left = self.track.load_partitions()
            percent = 25 + int(((self.total - partitions_left) * 1.0 / self.total) * 75)
            self.label.text = self.text + str(percent) + '%'
            if partitions_left == 0:
                # load the music last
                self.track.load_music()
                # hack to prevent circular imports
                from race import Race
                race = Race(self.track, [state.profile.car, ComputerCar.get_default(),
                    ComputerCar.get_default()])
                director.replace(race)
        
    