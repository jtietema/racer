from cocos.scene import Scene
from cocos.tiles import ScrollableLayer, ScrollingManager
from cocos import menu
from cocos.director import director
from pyglet.window import key

from game_state import state
from car import PlayerCar

class Race(Scene):    
    def __init__(self, map_layer, cars):
        Scene.__init__(self)
        
        self.map_layer = map_layer
        
        self.cars = cars
        self.cars_layer = ScrollableLayer()
        
        self.scroller = ScrollingManager()
        self.scroller.add(self.map_layer)
        self.scroller.add(self.cars_layer)
        
        num_player_cars = 0
        for car in self.cars:
            # Add the car to the cars layer.
            self.cars_layer.add(car)
            
            # Set the car's position.
            # TODO: valid position
            car.x = self.map_layer.px_width // 2
            car.y = self.map_layer.px_height // 2
            
            if isinstance(car, PlayerCar):
                num_player_cars += 1
                self.scroller.set_focus(*car.position)
            
            # Reset the car's state.
            car.reset()
        
        assert num_player_cars == 1
        
        self.add(self.scroller)
        
        self.schedule(self.update)
        
        self.menu = None
        
    def update(self, dt):
        """Updates all the cars."""
        for car in self.cars:
            car.update(dt)
            
            if isinstance(car, PlayerCar):
                self.scroller.set_focus(*car.position)


class InGameMenu(menu.Menu):
    def __init__(self):
        menu.Menu.__init__('Game menu')
        
        items = [
            MenuItem('Resume game', self.on_resume),
            MenuItem('Leave race', director.pop)
        ]
        
        self.create_menu(items, shake(), shake_back())
    
    def on_resume(self):
        self.parent.remove(self)
    
    def on_quit(self):
        self.on_resume()
