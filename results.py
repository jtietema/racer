from cocos.director import director
from cocos.scene import Scene
from cocos import menu

from game_state import state
from race import Race

class Results(Scene):
    def __init__(self):
        super(Results, self).__init__()
        
        self.add(ResultsMenu())
        

class ResultsMenu(menu.Menu):
    def __init__(self):
        super(ResultsMenu, self).__init__('Results')
        
        items = []
        
        if state.cup.has_next_track():
            items.append(menu.MenuItem('Next race', self.on_next_race))
        
        items.append(menu.MenuItem('Back to Main Menu', self.on_back))
        
        self.create_menu(items, menu.shake(), menu.shake_back())
    
    def on_next_race(self):
        race = Race(state.cup.next_track(), [state.profile.car])
        director.replace(race)
    
    def on_back(self):
        director.pop()
        