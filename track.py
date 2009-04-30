import os
import ConfigParser
from PIL import Image

import cocos

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
        
        # set starting point
        sx = cp.getint(track, 'startx')
        sy = cp.getint(track, 'starty')
        self.start = sx, sy
        
        # get track overlay
        overlay_file = cp.get(track, 'overlay_image')
        overlay = Image.open(os.path.join('cups', 'garden', overlay_file))
        self.overlay = overlay.load()
        
        # set number of checkpoints
        self.checkpoints = cp.getint(track, 'checkpoints')
        
        # set number of laps
        self.laps = cp.getint(track, 'laps')
    
    def get_friction_at(self, (x,y)):
        if 0 < x < self.size[0] and 0 < y < self.size[1]:
            pixel = self.overlay[x,self.size[1] - y]
            return pixel[3]
        return 25
    
    def get_path_at(self, (x,y)):
        if 0 < x < self.size[0] and 0 < y < self.size[1]:
            pixel = self.overlay[x,self.size[1] - y]
            return pixel[0]
        return 0
    
    def get_checkpoint_at(self, (x,y)):
        if 0 < x < self.size[0] and 0 < y < self.size[1]:
            pixel = self.overlay[x,self.size[1] - y]
            if 10 < pixel[1] < 100:
                return 1
            elif pixel[1] > 125:
                return 2
        return 0
    
    def get_start(self):
        return self.start
    
    def get_checkpoints(self):
        return self.checkpoints
    
    def get_size(self):
        return self.size
    
    def get_laps(self):
        return self.laps
    
