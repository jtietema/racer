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
        #self.track = cocos.sprite.Sprite(track_image)
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
        #self.overlay = cocos.sprite.Sprite(overlay_file)
        overlay = Image.open(os.path.join('cups', 'garden', overlay_file))
        self.overlay = overlay.load()
    
    def get_grip_at(self, (x,y)):
        pixel = self.overlay[x,self.size[1] - y]
        return pixel[3]
    
    def get_start(self):
        return self.start

