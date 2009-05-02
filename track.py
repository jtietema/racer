import os
import ConfigParser
from PIL import Image

import cocos
import pyglet.media


CHECKPOINT_STAGE_TYPES = 3


class Track(cocos.sprite.Sprite):
    def __init__(self, cup, track):
        # load the tracks config file
        cp = ConfigParser.ConfigParser()
        cp.read(os.path.join('cups', cup, 'tracks.ini'))
        # check if the track is there
        if not cp.has_section(track):
            raise Exception('Track not found')
        # load the track image
        track_image = cp.get(track, 'track_image')
        super(Track, self).__init__(track_image)
        height = cp.getint(track, 'height')
        width = cp.getint(track, 'width')
        self.size = (width, height)
        self.position = (width / 2, height / 2)
        
        # set starting grid
        self.start = []
        for i in range(1, 9):
            sx = cp.getint(track, 'start' + str(i) + 'x')
            sy = cp.getint(track, 'start' + str(i) + 'y')
            sr = cp.getint(track, 'start' + str(i) + 'r')
            self.start.append(((sx, sy), sr))
        
        # get track overlay
        overlay_file = cp.get(track, 'overlay_image')
        overlay = Image.open(os.path.join('cups', 'garden', overlay_file))
        self.overlay = overlay.load()
        
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
    
    def get_friction_at(self, (x,y)):
        if 0 < x < self.size[0] and 0 < y < self.size[1]:
            pixel = self.overlay[x/4,(self.size[1] - y) / 4]
            return pixel[2]
        return 25
    
    def get_path_at(self, (x,y)):
        if 0 < x < self.size[0] and 0 < y < self.size[1]:
            pixel = self.overlay[x/4,(self.size[1] - y) / 4]
            return pixel[0]
        return 0
    
    def get_checkpoint_stage_at(self, (x,y)):
        if 0 < x < self.size[0] and 0 < y < self.size[1]:
            pixel = self.overlay[x/4,(self.size[1] - y) / 4]
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
    
    
