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

options = {
    'body': {
        'fellali': {
            'name': 'Fellali',
            'image': 'chassis.png',
            'mass': 3,
            'tyres_fx_offset': 62,
            'tyres_fy_offset': 75,
            'tyres_bx_offset': 65,
            'tyres_by_offset': -90,
            'price': 0
        },
        'blue': {
            'name': 'Blue',
            'image': 'body2.png',
            'mass': 8,
            'tyres_fx_offset': 77,
            'tyres_fy_offset': 75,
            'tyres_bx_offset': 80,
            'tyres_by_offset': -90,
            'price': 100
        }
    },

    'engine': {
        'basic': {
            'name': 'Basic Engine',
            'power': 3,
            'price': 0
        },
        'monster_truck': {
            'name': 'Monster Truck',
            'power': 10,
            'price': 1000
        }
    },

    'tyres': {
        'second_hand': {
            'name': 'Second Hand',
            'image': 'tyre.png',
            'grip': 0.3,
            'price': 0
        }
    }
}

body = options['body']
engine = options['engine']
tyres = options['tyres']
