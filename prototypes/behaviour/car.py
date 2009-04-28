from cocos.sprite import Sprite
from cocos.director import director
from pyglet.window import key
import math

# Convenience constants.
FORWARD = RIGHT = 1
REVERSE = LEFT = -1
STILL = 0

# Multipliers used to increase the effect of acceleration.
ACCEL_MULTIPLIERS = {
    FORWARD:    1000,
    STILL:      0,
    REVERSE:    500 
}

# The speed at which the car can rotate.
ROTATION_SPEED = 150

# Friction constants for different terrain types. These influence the
# maximum speed, the acceleration time and the brake time of the car.
# The value should be between 0 and 1.
TERRAIN_FRICTIONS = {
    'asphalt': 0.5
}

# The friction of the tyres of the car. See terrain friction constants
# comments for an explanation on which properties are influenced by
# this value. A value between 0 and 1.
TYRE_FRICTION = 0.5

# The mass of the car. A value between 1 and 10.
MASS = 5

# The power of the car's engine. A value between 1 and 10.
POWER = 5


def signum(number):
    """This should be in Python's standard library."""
    if number > 0: return 1
    elif number < 0: return -1
    return number


class Car(Sprite):
    def __init__(self, id, pos):
        Sprite.__init__(self, 'car.png', pos)
        
        self.scale = 0.3
        
        # Unique identifier that this car should use for network
        # communication.
        self.id = id
        
        # Car has no initial speed.
        self.speed = 0
        
        # The direction in which we are accelerating.
        self.accel_dir = 0
        
        # The direction in which we are rotating.
        self.rot_dir = 0
        
        self.set_part_dependant_properties()
        
        # Make sure we update the car every frame.
        self.schedule(self.update)
    
    def set_part_dependant_properties(self):
        """Sets properties that depend on the car's parts. These mainly
           relate to physical properties."""
        self.friction_multiplier = (1.0/MASS) * TYRE_FRICTION
        
        # Multiplier used in calculation of maximum speed and acceleration.
        self.accel_multiplier = self.friction_multiplier * POWER
        
        # Braking depends on the friction, as well as the mass of the car.
        self.brake_multiplier = self.friction_multiplier * (10 - MASS)
        
    def update(self, dt):
        terrain = 'asphalt'
        
        self.speed = self.calculate_speed(dt, terrain)
        
        if self.speed <> 0:
            rot_factor = min(1, abs(self.speed) / 200)
            self.rotation = (self.rotation + (rot_factor * ROTATION_SPEED * self.rot_dir * dt)) % 360
        
        r = math.radians(self.rotation)
        s = dt * self.speed
        
        target_x = self.x + math.sin(r) * s
        target_y = self.y + math.cos(r) * s
        
        if self.is_valid_move((target_x, target_y)):
            self.x = target_x
            self.y = target_y
    
    def calculate_speed(self, dt, terrain):
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
            speed_multiplier = accel_multiplier * TERRAIN_FRICTIONS[terrain]
            
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
                # We want to apply brake power.
                slow_down_multiplier = self.brake_multiplier * abs(self.accel_dir)
            
            # We use a large constant in the calculation to increase the effect
            # of slowing down.
            speed -= speed_sig * slow_down_multiplier * 2000 * TERRAIN_FRICTIONS[terrain] * dt
            
            # Cap the speed.
            if speed * speed_sig < 0:
                speed = 0
        
        return speed
    
    def is_valid_move(self, (target_x, target_y)):
        return True


class PlayerCar(Car):
    def __init__(self, *args):
        self.keyboard = key.KeyStateHandler()
        director.window.push_handlers(self.keyboard)
        
        Car.__init__(self, *args)
        
    def update(self, dt):
        self.rot_dir = self.keyboard[key.RIGHT] - self.keyboard[key.LEFT]
        self.accel_dir = self.keyboard[key.UP] - self.keyboard[key.DOWN]
        
        Car.update(self, dt)
