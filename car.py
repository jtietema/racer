# TODO: collision detection

import math
import os
from random import randint

from cocos.cocosnode import CocosNode
from cocos.sprite import Sprite
from cocos.director import director
from pyglet.window import key
import pyglet.resource
from cocos.particle import ParticleSystem, Color
from cocos.euclid import Point2

import parts
from util import signum
from game_state import state

# Convenience constants.
FORWARD = RIGHT = 1
REVERSE = LEFT = -1
STILL = 0

# Multipliers used to increase the effect of acceleration.
ACCEL_MULTIPLIERS = {
    FORWARD:    2000,
    STILL:      0,
    REVERSE:    1000 
}

# The speed at which the car can rotate.
ROTATION_SPEED = 150

# Friction constants for different terrain types. These influence the
# maximum speed, the acceleration time and the brake time of the car.
# The value should be between 0 and 1.
FRICTIONS = {
    'asphalt': 0.5
}

TYRE_NAMES = ['tyre_tl','tyre_tr','tyre_bl','tyre_br']

MAX_TYRE_ROTATION = 30

COMPUTER_NAMES = [
    'Brutus',
    'Rufus',
    'Gunther',
    'Grossini'
]


class Car(CocosNode):
    @classmethod
    def get_default(cls):
        """Returns an instance of Car with default configuration."""
        return cls(body='fellali', engine='basic', tyres='second_hand')
    
    def __init__(self, **kwargs):
        CocosNode.__init__(self)
        
        self.reset()
        
        # Set the car's parts.
        for group in parts.options.keys():
            # We use the special add-methods because we don't want to set
            # the part dependant types again. for every part the first time.
            getattr(self, '_add_' + group)(kwargs[group])
        
        # Set the part dependant parts only once.
        self.set_part_dependant_properties()
        
        self.align_tyres()
        
        self.track = None
        
        self.dirt = Dirt()
        self.add(self.dirt)
        
        # TODO: calculate these properties bases on the children
        self.width = 100
        self.height = 100
    
    def reset(self, rotation=0):
        """Resets some properties of the car, such as rotation and speed.
           This is useful when switching races."""
        self.scale = 0.3
           
        self.speed = 0
        self.rotation = rotation
        
        # The direction in which we are accelerating.
        self.accel_dir = 0
        
        # The direction in which we are rotating.
        self.rot_dir = 0
        
        self.stopping = False
        
        self.track = None
    
    def set_part_dependant_properties(self):
        """Sets properties that depend on the car's parts. These mainly
           relate to physical properties."""
        self.friction_multiplier = (1.0/self.mass) * self.grip
        
        # Multiplier used in calculation of maximum speed and acceleration.
        self.accel_multiplier = self.friction_multiplier * self.power
        
        # Braking depends on the friction, as well as the mass of the car.
        self.brake_multiplier = self.friction_multiplier * (10 - self.mass)
        
    def update(self, dt):
        """Update the car's state."""
        friction = self.track.get_friction_at(self.position)
        self.speed = self.calculate_speed(dt, friction)
        
        rot_factor = min(1, abs(self.speed) / 200)
        self.rotation = (self.rotation + (rot_factor * ROTATION_SPEED * self.rot_dir * signum(self.speed) * dt)) % 360
        
        tyre_rotation = MAX_TYRE_ROTATION * self.rot_dir
        for tyre in self.top_tyres:
            tyre.rotation = tyre_rotation
        
        # Change dirt properties.
        self.dirt.speed = self.speed
        
        
        r = math.radians(self.rotation)
        s = dt * self.speed
        
        target_x = self.x + math.sin(r) * s
        target_y = self.y + math.cos(r) * s
        
        if self.is_valid_move((target_x, target_y)):
            self.x = target_x
            self.y = target_y
    
    def calculate_speed(self, dt, friction):
        """Calculates the car's new speed based on its current speed, the
           amount of time passed and physical properties like the friction
           and the car's mass."""
        
        # Work with a copy of the speed, since we don't want to alter the
        # state directly.
        speed = self.speed
        
        accel_sig = signum(self.accel_dir)
        speed_sig = signum(speed)
        
        if speed_sig == 0 and accel_sig == 0:
            # Standing still and not accelerating.
            return 0
        elif accel_sig == speed_sig or speed_sig == 0:
            # We are accelerating in the same direction as we are currently
            # heading. Use a multiplier per direction, since we can accelerate
            # forward more quickly than we can in reverse.
            accel_multiplier = self.accel_multiplier * self.accel_dir * ACCEL_MULTIPLIERS[accel_sig]
            
            # The terrain friction will be used in the calculation.
            speed_multiplier = accel_multiplier * (friction / 255.0)
            
            speed += speed_multiplier * dt
            
            # Cap the speed.
            max_speed = speed_multiplier
            if abs(speed) > abs(max_speed):
                speed = max_speed
        else:            
            if accel_sig == 0:
                # Let the friction slow down the car.
                slow_down_multiplier = self.friction_multiplier
            else:
                # We want to apply brake power, but correct it with the amount
                # of brake power applied by the player. Make sure it doesn't
                # get below the friction multiplier; there is no brake that
                # negatively influences physical friction.
                slow_down_multiplier = max(self.friction_multiplier, self.brake_multiplier * abs(self.accel_dir))
            
            # We use a large constant in the calculation to increase the effect
            # of slowing down.
            speed -= speed_sig * slow_down_multiplier * 2000 * (friction / 255.0) * dt
            
            # Cap the speed.
            if speed * speed_sig < 0:
                speed = 0
                
                if self.stopping:
                    self.accel_dir = 0
        
        return speed
    
    def is_valid_move(self, (target_x, target_y)):
        return True
    
    def disable_controls(self):
        pass
    
    def stop(self):
        self.disable_controls()
        self.accel_dir = -1
        self.stopping = True
    
    mass    = property(lambda self: self.body_properties['mass'])
    power   = property(lambda self: self.engine_properties['power'])
    grip    = property(lambda self: self.tyres_properties['grip'])
    
    def _add_engine(self, engine_name):
        self.engine_name = engine_name
    def _set_engine(self, engine_name):
        self._add_engine(engine_name)
        self.set_part_dependant_properties()
    engine = property(lambda self: self.engine_name, _set_engine)
    engine_properties = property(lambda self: parts.engine[self.engine_name])
    
    def _add_body(self, body_name):
        self.body_name = body_name
        image_file = parts.body[self.body_name]['image']
        self.add(Sprite(image_file), name='body', z=10)
    def _set_body(self, body_name):
        self.try_remove('body')
        self._add_body(body_name)
        self.set_part_dependant_properties()
        self.align_tyres()
    body = property(lambda self: self.body_name, _set_body)
    body_properties = property(lambda self: parts.body[self.body_name],
        doc='Returns the properties of the tyres, as defined in the parts config.')
    
    def _add_tyres(self, tyres_name):
        self.tyres_name = tyres_name
        image = parts.tyres[self.tyres_name]['image']
        for tyre_name in TYRE_NAMES:
            self.add(Sprite(image), name=tyre_name, z=9)
    def _set_tyres(self, tyres_name):
        for tyre_name in TYRE_NAMES:
            self.try_remove(tyre_name)
        self._add_tyres(tyres_name)
        self.set_part_dependant_properties()
        self.align_tyres()
    tyres = property(lambda self: self.tyres_name, _set_tyres)
    tyres_properties = property(lambda self: parts.tyres[self.tyres_name],
        doc='Returns the properties of the tyres, as defined in the parts config.')
    top_tyres = property(lambda self: (self.get('tyre_tl'), self.get('tyre_tr')),
        doc='Returns the top two tyre Sprites.')
    bottom_tyres = property(lambda self: (self.get('tyre_bl'), self.get('tyre_br')),
        doc='Returns the bottom two tyre Sprites.')
    
    def align_tyres(self):
        """Aligns the tyres with the body."""
        for tyre_name in TYRE_NAMES:
            # Fetch the corresponding Sprite object.
            tyre = self.get(tyre_name)
            
            # Determine if this tyre is to be aligned at the top or the
            # bottom.
            tb = tyre_name[-2]
            
            x = self.body_properties['tyres_' + tb + 'x_offset']
            y = self.body_properties['tyres_' + tb + 'y_offset']
            
            # If the tyre is to be aligned on the left, flip the x offset.
            if tyre_name[-1] == 'l':
                x *= -1
            
            tyre.position = (x, y)
    
    def try_remove(self, obj):
        """Tries to remove an object from the node's children. Catches any
           exceptions that are generated in the process."""
        try:
            self.remove(obj)
        except Exception:
            pass


class PlayerCar(Car):
    def __init__(self, *args, **kwargs):
        self.keyboard = key.KeyStateHandler()
        director.window.push_handlers(self.keyboard)
        
        Car.__init__(self, *args, **kwargs)
        
    def reset(self, *args, **kwargs):
        super(PlayerCar, self).reset(*args, **kwargs)
        
        self.controls_enabled = True
    
    def disable_controls(self):
        self.controls_enabled = False
        
    def update(self, dt):
        if self.controls_enabled:
            self.rot_dir = self.keyboard[key.RIGHT] - self.keyboard[key.LEFT]
            self.accel_dir = self.keyboard[key.UP] - self.keyboard[key.DOWN]
        
        Car.update(self, dt)
    
    name = property(lambda self: state.profile.name)


class ComputerCar(Car):
    def __init__(self, *args, **kwargs):
        Car.__init__(self, *args, **kwargs)
        
        # TODO: prevent a name to be taken twice.
        self.name = COMPUTER_NAMES[randint(0, len(COMPUTER_NAMES) - 1)]
    
    def update(self, dt):
        if not self.stopping:
            rotation_left = (self.rotation - 45) % 360
            rotation_right = (self.rotation + 45) % 360
        
        
            left_sensor = self.calc_sensor_pos(rotation_left)
            right_sensor = self.calc_sensor_pos(rotation_right)
            center_sensor = self.calc_sensor_pos(self.rotation)
        
            left_friction = self.track.get_path_at(left_sensor)
            right_friction = self.track.get_path_at(right_sensor)
            center_friction = self.track.get_path_at(center_sensor)
        
            if (left_friction > right_friction and left_friction > center_friction):
                self.rot_dir = -1
            elif (left_friction < right_friction and center_friction < right_friction):
                self.rot_dir = 1
            else:
                self.rot_dir = 0
        
            self.accel_dir = 1
        
        Car.update(self, dt)
    
    def calc_sensor_pos(self, rotation):
        r = math.radians(rotation)
        
        target_x = self.x + math.sin(r) * (self.height/2 +10)
        target_y = self.y + math.cos(r) * (self.height/2 +10)
        return (target_x, target_y)
        

class Dirt(ParticleSystem):
    # total particles
    total_particles = 75

    # duration
    duration = -1

    # gravity
    gravity = Point2(0,0)

    # angle
    angle = -90
    angle_var = 20

    # radial
    radial_accel = 200
    radial_accel_var = 0

    # speed of particles
    speed = 800
    speed_var = 50

    # emitter variable position
    pos_var = Point2(0,0)

    # life of particles
    life = 0.3
    life_var = 0.1

    # emits per frame
    emission_rate = total_particles / life

    # color of particles
    start_color = Color(0.5,0.5,0.5,1.0)
    start_color_var = Color(0.5, 0.5, 0.5, 1.0)
    end_color = Color(0.1,0.1,0.1,0.2)
    end_color_var = Color(0.1,0.1,0.1,0.2)

    # size, in pixels
    size = 10.0
    size_var = 2.0

    # blend additive
    blend_additive = False

    # color modulate
    color_modulate = True
    