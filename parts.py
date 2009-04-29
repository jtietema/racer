index = [
    'tyres',
    'engine'
]

options = {
    'chassis': {
        'fellali': {
            'name': 'Fellali',
            'image': 'chassis.png',
            'mass': 3,
            'tyres_tx_offset': 62,
            'tyres_ty_offset': 75,
            'tyres_bx_offset': 65,
            'tyres_by_offset': -90,
            'price': 0
        },
        'blue': {
            'name': 'Blue',
            'image': 'body2.png',
            'mass': 4,
            'tyres_tx_offset': 62,
            'tyres_ty_offset': 75,
            'tyres_bx_offset': 65,
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
            'name': 'Monster Truck Engine',
            'power': 8,
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

chassis = options['chassis']
engine = options['engine']
tyres = options['tyres']
