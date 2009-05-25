# -*- coding: utf-8 -*-
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
        # load the tracks config file
        cp = ConfigParser.ConfigParser()
        cp.read(os.path.join('cups', cup, 'tracks.ini'))
        # check if the track is there
        if not cp.has_section(track):
            raise Exception('Track not found')
        # load the track image(s)
        track_image_name = cp.get(track, 'track_image')
        track_image = pyglet.image.load(os.path.join('cups', cup,track_image_name))
        
        width, height = track_image.width, track_image.height
        
        # partition the image in multiple sprites
        number_x = width / self.TEXTURE_SIZE
        print number_x
        for x in range(number_x):
            number_y = height / self.TEXTURE_SIZE
            print number_y
            for y in range(number_y):
                part_image = track_image.get_region(x * self.TEXTURE_SIZE, y * self.TEXTURE_SIZE, self.TEXTURE_SIZE, self.TEXTURE_SIZE)
                sprite = cocos.sprite.Sprite(part_image)
                sprite.position = (x * self.TEXTURE_SIZE + self.TEXTURE_SIZE / 2, y * self.TEXTURE_SIZE + self.TEXTURE_SIZE / 2)
                self.add(sprite)
        
        self.size = (width, height)
        
        # set starting grid
        self.start = []
        for i in range(1, 9):
            sx = cp.getint(track, 'start' + str(i) + 'x')
            sy = cp.getint(track, 'start' + str(i) + 'y')
            sr = cp.getint(track, 'start' + str(i) + 'r')
            self.start.append(((sx, sy), sr))
        
        # get track overlay
        overlay_file = cp.get(track, 'overlay_image')
        # set the encode explicitly otherwise we get in trouble with the image_data format
        overlay_image = pyglet.image.load(os.path.join('cups', cup, overlay_file), decoder=PNGImageDecoder())
        image_data = overlay_image.get_image_data()
        data = image_data.get_data('RGBA', image_data.pitch)
        self.overlay_data = map(ord, list(data))
        
        # set number of checkpoints
        self.checkpoints = cp.getint(track, 'checkpoints')
        
        # set number of laps
        self.laps = cp.getint(track, 'laps')
        
        if cp.has_option(track, 'music'):
            music_file = cp.get(track, 'music')
            music_source = pyglet.media.load(os.path.join('music', music_file))
            
            self.music = pyglet.media.Player()
            self.music.queue(music_source)
            
            if cp.has_option(track, 'music_volume'):
                self.music.volume = cp.getfloat(track, 'music_volume')
            
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
    
    
