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

from cocos.director import director
import pyglet
import pymunk

from menu import MenuScene
from cups import Cup
import profiles
from game_state import state

director.init(width=1024, height=768, caption='RCr: Larry\'s Lawn')

pyglet.resource.path = ['img', os.path.join('cups', 'garden')]
pyglet.resource.reindex()

pymunk.init_pymunk()

state.cup = Cup('garden')

menu_scene = MenuScene()

director.run(menu_scene)
