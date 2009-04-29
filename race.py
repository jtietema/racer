from cocos.scene import Scene
from cocos.tiles import ScrollableLayer, ScrollingManager

from game_state import state
from car import PlayerCar

class Race(Scene):
    def __init__(self, track, cars):
        Scene.__init__(self)
        
        self.track_layer = ScrollableLayer()
        self.track_layer.add(track)
        self.track = track
        
        self.cars = cars
        self.cars_layer = ScrollableLayer()
        
        self.scroller = ScrollingManager()
        self.scroller.add(self.track_layer, z=-1)
        self.scroller.add(self.cars_layer)
        
        num_player_cars = 0
        for car in self.cars:
            # Add the car to the cars layer.
            self.cars_layer.add(car)
            
            # Set the car's position.
            car.position = track.get_start()
            
            if isinstance(car, PlayerCar):
                num_player_cars += 1
                self.scroller.set_focus(*car.position)
            
            # Reset the car's state.
            car.reset()
        
        assert num_player_cars == 1
        
        self.add(self.scroller)
        
        self.schedule(self.update)
        
    def update(self, dt):
        """Updates all the cars."""
        for car in self.cars:
            grip = self.track.get_grip_at(car.position)
            car.update(dt, grip)
            
            if isinstance(car, PlayerCar):
                self.scroller.set_focus(*car.position)
        
