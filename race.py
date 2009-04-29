from cocos.scene import Scene
from cocos.tiles import ScrollableLayer, ScrollingManager

from game_state import state
from car import PlayerCar

class Race(Scene):
    def __init__(self, track, cars):
        Scene.__init__(self)
        
        self.track_layer = ScrollableLayer()
        self.track_layer.px_width = track.get_size()[0]
        self.track_layer.px_height = track.get_size()[1]
        self.track_layer.add(track)
        self.track = track
        
        self.cars = cars
        self.cars_layer = ScrollableLayer()
        
        self.scroller = ScrollingManager()
        self.scroller.add(self.track_layer, z=-1)
        self.scroller.add(self.cars_layer)
        
        num_player_cars = 0
        self.stats = {}
        for car in self.cars:
            # Add the car to the cars layer.
            self.cars_layer.add(car)
            
            # Set the car's position.
            car.position = track.get_start()
            
            if isinstance(car, PlayerCar):
                num_player_cars += 1
                self.scroller.set_focus(*car.position)
            
            self.stats[car] = Stats()
            
            # Reset the car's state.
            car.reset()
        
        assert num_player_cars == 1
        
        self.add(self.scroller)
        
        self.schedule(self.update)
        
    def update(self, dt):
        """Updates all the cars."""
        for car in self.cars:
            # update the car
            grip = self.track.get_grip_at(car.position)
            car.update(dt, grip)
            
            # update checkpoints
            checkpoint = self.track.get_checkpoint_at(car.position)
            if checkpoint == 1 and not self.stats[car].in_checkpoint:
                self.stats[car].pre_checkpoint = True
                self.stats[car].in_checkpoint = True
            elif checkpoint == 2 and self.stats[car].pre_checkpoint and self.stats[car].in_checkpoint:
                self.stats[car].pre_checkpoint = False
                self.stats[car].checkpoint += 1
                print 'Checkpoint', self.stats[car].checkpoint
            elif checkpoint == 2 and not self.stats[car].pre_checkpoint and not self.stats[car].in_checkpoint:
                self.stats[car].in_checkpoint = True
                self.stats[car].checkpoint -= 1
                print 'Checkpoint', self.stats[car].checkpoint
            elif checkpoint == 0:
                self.stats[car].in_checkpoint = False
                self.stats[car].pre_checkpoint = False
            
            # update laps
            if self.stats[car].checkpoint == self.track.get_checkpoints():
                self.stats[car].checkpoint = 0
                self.stats[car].laps += 1
                print 'Laps ', self.stats[car].laps
                if self.stats[car].laps == self.track.get_laps():
                    print 'Finished'
            
            if isinstance(car, PlayerCar):
                self.scroller.set_focus(*car.position)
        
class Stats():
    def __init__(self):
        self.laps = 0
        self.checkpoint = -1
        self.pre_checkpoint = False
        self.in_checkpoint = False
        
