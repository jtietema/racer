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
from cocos.sprite import Sprite
from cocos.particle_systems import Explosion
from pyglet.window import key

from game_state import state
import util


BLOCK_WIDTH = 250
HEIGHTS = [200, 150, 100]
X_DIR = [0, -1, 1]

MONEY = [1000, 500, 250]


# TODO: variable amount of money per cup/track


class Podium(Scene):    
    def __init__(self):
        super(Podium, self).__init__()
        
        self.podium = Layer()
        self.podium.is_event_handler = True
        self.podium.on_key_press = self.on_key_press
        
        center = director.window.width / 2
        
        podium_sprite = Sprite('podium.png')
        podium_sprite.image_anchor_y = 0
        podium_sprite.x = center
        
        self.podium.add(podium_sprite)
        
        top_3 = state.cup.total_ranking[:3]
        
        for index, car in enumerate(top_3):
            label = util.Label(text=car.name, font_size=25, anchor_y='bottom',
                anchor_x='center')
            label.x = center + (X_DIR[index] * BLOCK_WIDTH)
            label.y = HEIGHTS[index] + 20
            self.podium.add(label, z=3)
        
        self.add(self.podium, z=2)
        
        fireworks = Fireworks()
        fireworks.x = center
        fireworks.y = director.window.height / 2 + 100
        self.add(fireworks, z=1)
        
        if state.profile.car in top_3:
            position = top_3.index(state.profile.car)
            earned = MONEY[position]
            head_text = 'You earned $%d!' % (earned,)
            
            state.profile.money += earned
            state.profile.save()
            
            if position == 0:
                head_text = 'Congratulations! ' + head_text
        else:
            head_text = 'Better luck next time!'
        
        head_label = util.Label(text=head_text, font_size=30, anchor_x='center',
            anchor_y='bottom')
        head_label.x = center
        head_label.y = director.window.height - 75
        self.add(head_label, z=3)
    
    def on_key_press(self, symbol, modifier):
        if symbol in [key.ESCAPE, key.RETURN, key.SPACE]:
            director.pop()
        return True


class Fireworks(Explosion):
    duration = -1
    total_particles = 300
