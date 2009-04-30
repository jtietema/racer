options = {
    'body': {
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
            'mass': 8,
            'tyres_tx_offset': 77,
            'tyres_ty_offset': 75,
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
            'name': 'Monster Truck Engine',
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
