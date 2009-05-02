import bisect
import os

import pygame.mixer
from cocos.cocosnode import CocosNode
from cocos.scene import Scene
from cocos.tiles import ScrollableLayer, ScrollingManager
from cocos import menu
from cocos.layer import ColorLayer, Layer
from cocos.director import director
from cocos.sprite import Sprite
from pyglet.window import key
from cocos.actions.instant_actions import CallFunc
from cocos.actions.interval_actions import ScaleTo, Delay, MoveTo, AccelDeccel
import pyglet.media

from game_state import state
from car import PlayerCar, ComputerCar
from podium import Podium
import util


SHORT_BEEP_SOUND = pyglet.media.load(os.path.join('sound', 'short_beep.wav'), streaming=False)
SHORT_BEEP_SOUND.volume = 0.2
LONG_BEEP_SOUND = pyglet.media.load(os.path.join('sound', 'long_beep.wav'), streaming=False)
LONG_BEEP_SOUND.volume = 0.2


class RaceException(Exception):
    pass


class Race(Scene):
    def __init__(self, track, cars):
        Scene.__init__(self)
        
        # This is set to true once countdown is complete.
        self.started = False
        
        self.player_finished = False
        
        self.results = []
        
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
        
        # define start grid
        i = 0
        grid = track.get_start()
        for car in self.cars:
            # Add the car to the cars layer.
            self.cars_layer.add(car)
            
            # Reset the car's state.
            car.reset()
            
            car.resume()
            
            # Set the car's position.
            car.position = grid[i][0]
            car.rotation = grid[i][1]
            i += 1
            
            # Add the track to the car
            car.track = track
            
            if isinstance(car, PlayerCar):
                num_player_cars += 1
                self.scroller.set_focus(*car.position)
                self.player_car = car
            
            self.stats[car] = Stats(car)
        
        assert num_player_cars == 1
        
        self.hud = HUD(self.track.get_laps())
        
        self.add(self.scroller, z=0)
        self.add(self.hud, z=1)
        
        self.menu = None
        
        self.add_traffic_lights()
        
        self.scroller.is_event_handler = True
        self.scroller.on_key_press = self.on_key_press
    
    def on_key_press(self, symbol, modifier):
        if not self.player_finished and symbol == key.ESCAPE:
            self.menu = MenuLayer(InGameMenu)
            self.add(self.menu, z=100)
            return True
    
    def remove_menu(self):
        if self.menu is not None:
            self.remove(self.menu)
            self.menu = None
        
    def add_traffic_lights(self):
        lights = TrafficLights()
        
        lights.image_anchor_y = 0
        lights.x = director.window.width / 2
        
        origin_y = director.window.height
        target_y = director.window.height - lights.image.height
        
        lights.y = origin_y
        
        self.add(lights, name='traffic_lights', z=100)
        
        lights.do(
            AccelDeccel(MoveTo((lights.x, target_y), 2))
            + (Delay(1) + CallFunc(lights.shift_overlay)) * TrafficLights.NUM_LIGHTS
            + CallFunc(self.start)
            + Delay(1.5)
            + MoveTo((lights.x, origin_y), 0.3)
            + CallFunc(self.remove, lights)
        )
        
    def update(self, dt):
        """Updates all the cars once the race has started."""        
        for car in self.cars:
            # update the car
            car.update(dt)
            
            if car is not self.player_car:
                # Change engine sound accordingly.
                car.move_sound_relative(self.player_car.position)
            
            # Create a short-named reference.
            stats = self.stats[car]
            
            # update checkpoints
            checkpoint_stage = self.track.get_checkpoint_stage_at(car.position)
            next_checkpoint_stage = (stats.last_checkpoint_stage + 1) % 3
            
            if checkpoint_stage == next_checkpoint_stage:
                # Car changed checkpoint stage and is driving in the right
                # direction.
                if checkpoint_stage == 2:
                    stats.checkpoints += 1
                    print car, 'Checkpoint', stats.checkpoints
            elif checkpoint_stage <> stats.last_checkpoint_stage and stats.last_checkpoint_stage > -1:
                # Car changed checkpoint stage and is driving the wrong way.
                print car, 'WRONG WAY!', stats.last_checkpoint_stage, checkpoint_stage
                if checkpoint_stage == 1:
                    stats.checkpoints -= 1
                    print car, 'Checkpoint', stats.checkpoints
            
            stats.last_checkpoint_stage = checkpoint_stage
            
            stats.current_lap_time += dt
            
            # update laps
            if stats.checkpoints == self.track.get_checkpoints():
                # At finish.
                stats.checkpoints = 0
                
                # Store the lap time and reset the current lap time.
                stats.lap_times.append(stats.current_lap_time)
                stats.current_lap_time = 0
                
                if stats.laps >= self.track.get_laps():                    
                    # Stop the car, disabling any controls in the process.
                    print car, 'Finished'
                    
                    car.stop()
                    
                    stats.finished = True
                    self.add_result(stats)
                else:
                    stats.laps += 1
                    print car, 'Laps ', stats.laps
                    
            if isinstance(car, PlayerCar) and not self.player_finished:
                if stats.finished:
                    # The race is over since the player car finished.
                    self.finish()
                else:
                    self.hud.update_laps(stats.laps)
                    self.scroller.set_focus(*car.position)
        
        # do collision detection
        
        # make a copy of cars list to prevent duplicate collision checks
        cars = self.cars[:]
        # iterate over all cars
        for car in self.cars:
            # remove car from the te list to prevent detecting collision with self
            cars.remove(car)
            # iterate over remaining cars
            for othercar in cars:
                polygon = car.get_polygon()
                other_polygon = othercar.get_polygon()
                if polygon.intersects(other_polygon):
                    self.resolve_collision(car, othercar)
                    
    def resolve_collision(self, car1, car2):
        diff_x = abs(car1.x - car2.x)
        diff_y = abs(car1.y - car2.y)
        collision = True
        while collision:
            if diff_y > diff_x:
                # resolve collision in y axis
                if car1.y > car2.y:
                    car1.y += 1
                    car2.y -= 1
                else:
                    car1.y -= 1
                    car2.y += 1
            else:
                # resolve collision in x axis
                if car1.x > car2.x:
                    car1.x += 1
                    car2.x -= 1
                else:
                    car1.x -= 1
                    car2.x += 1
            
            poly1 = car1.get_polygon()
            poly2 = car2.get_polygon()
            collision = poly1.intersects(poly2)
    
    def add_result(self, stats):
        """Returns a list with all the Stats instances sorted ascendingly
           by total lap time."""
        assert stats not in self.results

        self.results.append(stats)

        print 'RESULTS', self.results

    def autocomplete_results(self):
        """Automatically fills in a custom time for all cars that did not
           finish yet."""
        for stats in self.stats.values():
            if not stats.finished:
                assert stats not in self.results

                stats.total_time = self.results[-1].total_time + 30
                stats.finished = True
                self.results.append(stats)

        print 'RESULTS', self.results
    
    def start(self):
        self.started = True
        
        self.schedule(self.update)
    
    def finish(self):
        """Displays a message explaining the player that he finished.
           Also automatically progresses to the results screen."""
        self.player_finished = True
        
        # state.cup.set_results_for_current_track(self.results)
        
        player_position = self.results.index(self.stats[self.player_car]) + 1
        if player_position == 1:
            finished_text = 'You won!'
        elif player_position == len(self.stats):
            finished_text = 'You finished last'
        else:
            finished_text = 'You finished %s' % (util.ordinal(player_position),)
        
        label = util.Label(text=finished_text, anchor_y='bottom', font_size=40,
            background=(0, 0, 0, 125))
        
        label.transform_anchor_x = label.width / 2
        label.x = director.window.width / 2 - label.width / 2
        label.y = director.window.height / 2
        self.add(label, z=100)
        
        label.scale = 0
        label.do(
            ScaleTo(1, 0.75)
            + Delay(3)
            + ScaleTo(0, 0.75)
            + CallFunc(self.remove, label)
            + CallFunc(self.show_results)
        )
    
    def show_results(self):
        self.menu = MenuLayer(ResultsMenu)
        self.add(self.menu, z=100)

        self.menu.scale = 0
        self.menu.do(ScaleTo(1, 1))
    
    def save_results(self):
        """Autocompletes this race's results and stores them on the cup
           object."""
        self.autocomplete_results()
        
        state.cup.set_results_for_current_track(self.results)
    
    def on_exit(self):
        super(Race, self).on_exit()
        
        for car in self.cars:
            car.pause()
        
        self.track.stop_music()


class Stats():
    def __init__(self, car):
        self.car = car
        
        # Timer for the current lap.
        self.current_lap_time = 0
        
        # A list of lap times.
        self.lap_times = []
        
        # The lap the car is currently in.
        self.laps = 1
        
        # The last checkpoint stage the car was in.
        self.last_checkpoint_stage = -1
        
        # The number of check points passed since the finish. Set to -1
        # initially to compensate for a starting grid before the finish
        # line.
        self.checkpoints = -1
        
        # Reflects if this car finished the race.
        self.finished = False
    
    def __cmp__(self, other):
        return cmp(self.total_time, other.total_time)
    
    total_time = property(lambda self: sum(self.lap_times),
        doc="Returns the sum of all the lap times.")


class HUD(Layer):
    def __init__(self, lap_count):
        Layer.__init__(self)
        
        self.lap_count = lap_count
        
        self.laps_label = util.Label(text=self.get_laps_text(1),
            font_size=25, background=(0, 0, 0, 125),
            anchor_y='bottom')
        self.laps_label.y = director.window.height - self.laps_label.height
                
        self.add(self.laps_label)
    
    def get_laps_text(self, num_laps):
        return "Lap %d/%d" % (num_laps, self.lap_count)
    
    def update_laps(self, num_laps):
        self.laps_label.text = self.get_laps_text(num_laps)


class TrafficLights(CocosNode):
    NUM_LIGHTS = 4
    
    image = property(lambda self: self.image_sprite.image)
    
    def __init__(self):
        super(TrafficLights, self).__init__()
        
        self.image_sprite = Sprite('traffic_lights.png')
        self.image_sprite.image_anchor_y = 0
        self.add(self.image_sprite, z=1)
        
        self.draw_overlays()
    
    def draw_overlays(self):
        """Draws black, semi-transparent overlays over the lights to simulate
           a light that is turned off."""
        self.overlays = []
        
        width = self.image.width / TrafficLights.NUM_LIGHTS
        height = self.image.height
        
        for i in range(-2, TrafficLights.NUM_LIGHTS / 2):
            overlay = ColorLayer(0, 0, 0, 125, width, height)
            overlay.x = (i * width) / 2
            self.add(overlay, z=2)
            self.overlays.append(overlay)
    
    def shift_overlay(self):
        """Removes one overlay, making the next light from the left light up.
           Raises an exception if all overlays have already been removed."""
        if len(self.overlays) == 1:
            LONG_BEEP_SOUND.play()
        else:
            SHORT_BEEP_SOUND.play()
        self.remove(self.overlays.pop(0))
        

class MenuLayer(Layer):
    def __init__(self, klass):
        Layer.__init__(self)
        
        self.add(ColorLayer(0, 0, 0, 100), z=0)
        self.add(klass(), z=1)


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


class ResultsMenu(menu.Menu):
    def __init__(self):
        super(ResultsMenu, self).__init__('Results')

        if state.cup.has_next_track():
            items = [
                menu.MenuItem('Next race', self.on_next_race),
                menu.MenuItem('Back to Main Menu', self.on_back)
            ]
        else:
            items = [
                menu.MenuItem('Proceed', self.on_proceed)
            ]

        self.create_menu(items, menu.shake(), menu.shake_back())
    
    def on_proceed(self):
        self.get_ancestor(Race).save_results()
        director.replace(Podium())

    def on_next_race(self):
        self.get_ancestor(Race).save_results()
        race = Race(state.cup.next_track(), [state.profile.car, ComputerCar.get_default(), ComputerCar.get_default(), ComputerCar.get_default()])
        director.replace(race)

    def on_back(self):
        state.cup = None
        director.pop()
    
    def on_quit(self):
        pass
