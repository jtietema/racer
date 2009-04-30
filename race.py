import bisect

from cocos.scene import Scene
from cocos.tiles import ScrollableLayer, ScrollingManager
from cocos import menu
from cocos.layer import ColorLayer, Layer
from cocos.director import director
from pyglet.window import key
import pyglet.clock
from cocos.actions.instant_actions import CallFunc
from cocos.actions.interval_actions import ScaleTo, Delay

from game_state import state
from car import PlayerCar
import util


class RaceException(Exception):
    pass


class Race(Scene):
    def __init__(self, track, cars):
        Scene.__init__(self)
        
        self.finished = False
        
        self.results = None
        
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
                self.player_car = car
            
            self.stats[car] = Stats(car)
            
            # Reset the car's state.
            car.reset()
            
            # Add the track to the car
            car.track = track
        
        assert num_player_cars == 1
        
        self.hud = HUD(self.track.get_laps())
        
        self.add(self.scroller, z=0)
        self.add(self.hud, z=1)
        
        self.schedule(self.update)
        
        self.menu = None
        
        director.window.push_handlers(self.on_key_press)
    
    def on_key_press(self, symbol, modifier):
        if not self.finished and symbol == key.ESCAPE:
            self.menu = MenuLayer(InGameMenu)
            self.add(self.menu, z=100)
            return True
    
    def remove_menu(self):
        if self.menu is not None:
            self.remove(self.menu)
            self.menu = None
        
    def update(self, dt):
        """Updates all the cars."""
        for car in self.cars:
            # update the car
            car.update(dt)
            
            # Create a short-named reference.
            stats = self.stats[car]
            
            # update checkpoints
            checkpoint = self.track.get_checkpoint_at(car.position)
            if checkpoint == 1 and not stats.in_checkpoint:
                stats.pre_checkpoint = True
                stats.in_checkpoint = True
            elif checkpoint == 2 and stats.pre_checkpoint and stats.in_checkpoint:
                stats.pre_checkpoint = False
                stats.checkpoint += 1
                print 'Checkpoint', stats.checkpoint
            elif checkpoint == 2 and not stats.pre_checkpoint and not stats.in_checkpoint:
                stats.in_checkpoint = True
                stats.checkpoint -= 1
                print 'Checkpoint', stats.checkpoint
            elif checkpoint == 0:
                stats.in_checkpoint = False
                stats.pre_checkpoint = False
            
            finished = False
            
            if stats.checkpoint >= 0:
                stats.current_lap_time += dt
            
            # update laps
            if stats.checkpoint == self.track.get_checkpoints():
                # At finish.
                stats.checkpoint = 0
                
                # Store the lap time and reset the current lap time.
                stats.lap_times.append(stats.current_lap_time)
                stats.current_lap_time = 0
                
                if stats.laps >= self.track.get_laps():                    
                    # Stop the car, disabling any controls in the process.
                    print 'Finished'
                    
                    car.stop()
                    
                    finished = True
                else:
                    stats.laps += 1
                    print 'Laps ', stats.laps
                    
            if isinstance(car, PlayerCar) and not self.finished:
                if finished:
                    # The race is over since the player car finished.
                    self.finish()
                else:
                    self.hud.update_laps(stats.laps)
                    self.scroller.set_focus(*car.position)
    
    def finish(self):
        """Displays a message explaining the player that he finished.
           Also automatically progresses to the results screen."""
        self.finished = True
        
        self.results = self.calculate_results()
        
        state.cup.set_results_for_current_track(self.results)
        
        player_position = self.results.index(self.stats[self.player_car]) + 1
        if player_position == 1:
            finished_text = 'You won!'
        elif player_position == len(self.results):
            finished_text = 'You became last'
        else:
            finished_text = 'You finished %s' % (util.ordinal(player_position),)
        
        label = util.Label(text=finished_text, anchor_y='bottom', font_size=40,
            background=(0, 0, 0, 125))
        
        label.transform_anchor_x = label.width / 2
        label.x = director.window.width / 2 - label.width / 2
        label.y = director.window.height / 2
        self.add(label, z=100)
        
        label.scale = 0
        label.do(ScaleTo(1, 0.75) + Delay(3) + ScaleTo(0, 0.75)
            + CallFunc(self.remove, label) + CallFunc(self.show_results))
    
    def calculate_results(self):
        """Returns a list with all the Stats instances sorted ascendingly
           by total lap time. This method throws an exception if the race
           is not finished yet."""
        if not self.finished:
            raise RaceException("Race not finished yet.")
        
        results = []
        for stats in self.stats.values():
            bisect.insort(results, stats)
        
        return results
    
    def show_results(self):
        if state.cup.has_next_track():
            self.menu = MenuLayer(ResultsMenu)
            self.add(self.menu, z=100)

            self.menu.scale = 0
            self.menu.do(ScaleTo(1, 1))
        else:
            print state.cup.total_ranking


class Stats():
    def __init__(self, car):
        self.car = car
        self.current_lap_time = 0
        self.lap_times = []
        self.laps = 1
        self.checkpoint = -1
        self.pre_checkpoint = False
        self.in_checkpoint = False
    
    def __cmp__(self, other):
        return self.total_time > other.total_time
    
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

        items = []

        items.append(menu.MenuItem('Next race', self.on_next_race))
        items.append(menu.MenuItem('Back to Main Menu', self.on_back))

        self.create_menu(items, menu.shake(), menu.shake_back())

    def on_next_race(self):
        race = Race(state.cup.next_track(), [state.profile.car])
        director.replace(race)

    def on_back(self):
        director.pop()
    
    def on_quit(self):
        pass
