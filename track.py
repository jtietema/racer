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
import ConfigParser

import cocos
import pyglet
import pyglet.info
from pyglet.image.codecs.png import PNGImageDecoder


CHECKPOINT_STAGE_TYPES = 3


class Track(cocos.layer.Layer):
    TEXTURE_SIZE = 1000
    
    def __init__(self, cup, track):
        super(Track, self).__init__()
        self.name = track
        self.cup = cup
        
        self.track_image = None
        self.overlay_data = None
        self.size = None
        self.partition_list = None
        
        # load the tracks config file
        self.cp = cp = ConfigParser.ConfigParser()
        cp.read(os.path.join('cups', cup, 'tracks.ini'))
        # check if the track is there
        if not cp.has_section(track):
            raise Exception('Track not found')
        
        # set starting grid
        self.start = []
        for i in range(1, 9):
            sx = cp.getint(track, 'start' + str(i) + 'x')
            sy = cp.getint(track, 'start' + str(i) + 'y')
            sr = cp.getint(track, 'start' + str(i) + 'r')
            self.start.append(((sx, sy), sr))
        
        # set number of checkpoints
        self.checkpoints = cp.getint(track, 'checkpoints')
        
        # set number of laps
        self.laps = cp.getint(track, 'laps')
        
    def load_images(self):
        '''load the track image(s)'''
        track_image_name = self.cp.get(self.name, 'track_image')
        self.track_image = pyglet.image.load(os.path.join('cups', self.cup,track_image_name))
        
        width, height = self.track_image.width, self.track_image.height
        
        # partition the image in multiple sprites
        number_x = width / self.TEXTURE_SIZE
        number_y = height / self.TEXTURE_SIZE
        self.partition_list = []
        for x in range(number_x):
            for y in range(number_y):
                self.partition_list.append((x * self.TEXTURE_SIZE, y * self.TEXTURE_SIZE))
        
        self.size = (width, height)
    
    def load_overlay(self):
        '''Load the overlay'''
        overlay_file = self.cp.get(self.name, 'overlay_image')
        # set the encode explicitly otherwise we get in trouble with the image_data format
        overlay_image = pyglet.image.load(os.path.join('cups', self.cup, overlay_file), decoder=PNGImageDecoder())
        image_data = overlay_image.get_image_data()
        data = image_data.get_data('RGBA', image_data.pitch)
        self.overlay_data = map(ord, list(data))
    
    def load_partitions(self):
        x, y = self.partition_list.pop(0)
        part_image = self.track_image.get_region(x, y, self.TEXTURE_SIZE, self.TEXTURE_SIZE)
        sprite = cocos.sprite.Sprite(part_image)
        sprite.position = (x + self.TEXTURE_SIZE / 2, y + self.TEXTURE_SIZE / 2)
        self.add(sprite)
        partitions_left = len(self.partition_list)
        if partitions_left == 0:
            self.track_image = None # release image for garbage collection
        return partitions_left
    
    def load_music(self):
        '''Load the track music'''
        if self.cp.has_option(self.name, 'music'):
            music_file = self.cp.get(self.name, 'music')
            music_source = pyglet.media.load(os.path.join('music', music_file))
            
            self.music = pyglet.media.Player()
            self.music.queue(music_source)
            
            if self.cp.has_option(self.name, 'music_volume'):
                self.music.volume = self.cp.getfloat(self.name, 'music_volume')
            
            self.music.eos_action = pyglet.media.Player.EOS_LOOP
            
            self.music.play()
        else:
            self.music = None
    
    def get_overlay_pixel(self, (x,y)):
        overlay_y = int((self.size[1] - y) / 4)
        overlay_x = int(x / 4)
        rows = ((overlay_y-1) * 4 * int(self.size[0] / 4))
        pos = int(rows + (overlay_x - 1) * 4)
        pixel = self.overlay_data[pos:pos+4]
        return pixel
    
    def get_friction_at(self, (x,y)):
        if 0 < x < self.size[0] and 0 < y < self.size[1]:
            pixel = self.get_overlay_pixel((x,y))
            return pixel[2]
        return 25
    
    def get_path_at(self, (x,y)):
        if 0 < x < self.size[0] and 0 < y < self.size[1]:
            pixel = self.get_overlay_pixel((x,y))
            return pixel[0]
        return 0
    
    def get_checkpoint_stage_at(self, (x,y)):
        if 0 < x < self.size[0] and 0 < y < self.size[1]:
            pixel = self.get_overlay_pixel((x,y))
            if 10 < pixel[1] < 100:
                return 1
            elif pixel[1] > 125:
                return 2
        return 0
    
    def stop_music(self):
        if self.music is not None:
            self.music.pause()
    
    def get_start(self):
        return self.start
    
    def get_checkpoints(self):
        return self.checkpoints
    
    def get_size(self):
        return self.size
    
    def get_laps(self):
        return self.laps
    
    
