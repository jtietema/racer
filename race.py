from cocos.scene import Scene
from cocos.tiles import ScrollableLayer, ScrollingManager
from cocos import menu
from cocos.layer import ColorLayer, Layer
from cocos.director import director
from cocos.text import RichLabel
from pyglet.window import key

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
        
        self.hud = HUD()
        
        self.add(self.scroller, z=0)
        self.add(self.hud, z=1)
        
        self.schedule(self.update)
        
        self.menu = None
        
        director.window.push_handlers(self.on_key_press)
    
    def on_key_press(self, symbol, modifier):
        if symbol == key.ESCAPE:
            self.menu = MenuLayer()
            self.add(self.menu, z=100)
            return True
    
    def remove_menu(self):
        if self.menu is not None:
            self.remove(self.menu)
            self.menu = None
        
    def update(self, dt):
        """Updates all the cars."""
        for car in self.cars:
            grip = self.track.get_grip_at(car.position)
            car.update(dt, grip)
            
            if isinstance(car, PlayerCar):
                self.scroller.set_focus(*car.position)


class HUD(Layer):
    def __init__(self):
        Layer.__init__(self)
        
        self.laps_label = RichLabel(text='1 / 3', anchor_x='left')
                
        self.add(self.laps_label)


class MenuLayer(Layer):
    def __init__(self):
        Layer.__init__(self)
        
        self.add(ColorLayer(0, 0, 0, 100), z=0)
        self.add(InGameMenu(), z=1)


class InGameMenu(menu.Menu):
    def __init__(self):
        menu.Menu.__init__(self, 'Paused')
        
        items = [
            menu.MenuItem('Resume game', self.on_resume),
            menu.MenuItem('Leave race', director.pop)
        ]
        
        self.create_menu(items, menu.shake(), menu.shake_back())
    
    def on_resume(self):
        self.get_ancestor(Race).remove_menu()
    
    def on_quit(self):
        self.on_resume()
