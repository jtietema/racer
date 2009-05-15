import os
from string import capwords

import cocos
from cocos.director import director
from cocos.layer import Layer, ColorLayer, MultiplexLayer
from cocos.scene import Scene
import pyglet

import util
import parts
from game_state import state


class Shop(Scene):
    def __init__(self):
        super(Shop, self).__init__()
        
        # Make sure the car's properties set during previous scenes are
        # reset to their initial state.
        state.profile.car.reset()
        
        self.add(PreviewFrame())
        self.add(PartsFrame())
        self.add(BalanceLayer())


class Frame(Layer):
    """Abstract frame view for usage inside the shop."""

    def __init__(self, (width, height), border_width=5,
        border_color=(255, 255, 255, 255), content_bg_color=(0, 0, 0, 255),
        *args, **kwargs):

        super(Frame, self).__init__()

        self.border_layer = ColorLayer(*(border_color + (width, height)))
        self.add(self.border_layer, z=-2)

        content_size = (width - border_width * 4, height - border_width * 4)
        self.content_layer = ColorLayer(*(content_bg_color + content_size))
        self.content_layer.position = (border_width, border_width)
        self.content_layer.children_anchor = (border_width, border_width)
        self.add(self.content_layer, z=-1)
    
    size = property(lambda self: (self.width, self.height))


class SpinnerFrame(Frame):
    """Abstract specialized frame to display layers in several groups, with
       group navigation at the top."""

    def __init__(self, size, group_titles, layers, *args, **kwargs):
        super(SpinnerFrame, self).__init__(size, *args, **kwargs)

        assert len(group_titles) == len(layers)

        self.current_index = 0
        self.group_titles = group_titles

        # Add the different layers inside a MultiplexLayer, so we can easily
        # and quickly switch between them.
        self.layers = MultiplexLayer(*layers)
        self.content_layer.add(self.layers)

        # Build the navigation panel.
        nav_y = self.content_layer.height - 40
        button_size = (35, 35)
        button_options = {'font_size': 16, 'bold': True}

        left_x = 5
        prev_button = LabelButton('<', button_size, **button_options)
        prev_button.position = (left_x, nav_y)
        prev_button.on_click(self.previous_group)
        self.content_layer.add(prev_button)

        right_x = self.content_layer.width - 40
        next_button = LabelButton('>', button_size, **button_options)
        next_button.position = (right_x, nav_y)
        next_button.on_click(self.next_group)
        self.content_layer.add(next_button)

        center_x = self.content_layer.width / 2
        center_y = nav_y + 15
        group_text = self.group_titles[self.current_index]
        self.group_label = util.Label(group_text, x=center_x, y=center_y,
            width=self.content_layer.width, anchor_x='center',
            anchor_y='center', font_size=16)
        self.content_layer.add(self.group_label)

    def switch_group(self, step):
        index = abs((self.current_index + step) % len(self.group_titles))

        self.layers.switch_to(index)
        self.group_label.text = self.group_titles[index]

        self.current_index = index

    def previous_group(self):
        self.switch_group(-1)

    def next_group(self):
        self.switch_group(1)
    
    # TODO: dynamic
    navbar_size = property(lambda self: (self.content_layer.width, 40))
    def _get_content_size(self):
        return (self.content_layer.width,
            self.content_layer.height - self.navbar_size[1])
    content_size = property(_get_content_size,
        doc="""Returns the size of the actual content area, the area of the
               frame below the navigation elements.""")


class PreviewFrame(Frame):
    """Frame to hold the car's preview representation."""
    
    def __init__(self):
        width, height = 400, 500
        x = 10
        y = director.window.height - height - 10
        
        super(PreviewFrame, self).__init__((width, height),
            content_bg_color=(50, 50, 50, 255))
        
        self.position = (x, y)
        
        # Draw the car.
        state.profile.car.scale = 1
        state.profile.car.x = self.content_layer.width / 2
        state.profile.car.y = self.content_layer.height / 2 - 40
        self.content_layer.add(state.profile.car)
        
        # Add car property bars.
        label_x = 10
        bar_x = 150
        bar_y = self.content_layer.height - 25
        size = (225, 20)
        for bar_type in ('speed','grip','acceleration'):
            # Label
            label_text = capwords(bar_type)
            label = util.Label(label_text, font_size=12)
            label.position = (label_x, bar_y + 4)
            self.content_layer.add(label)
            
            # Bar
            bar = Bar(size)
            bar.position = (bar_x, bar_y)
            self.content_layer.add(bar, name=bar_type)
            
            bar_y -= 25


class PartsFrame(SpinnerFrame):
    """Holds all the parts that can be selected for the car. Also highlights
       the currently selected parts."""
    
    def __init__(self):
        width = 598
        height = 500
        x = director.window.width - width - 10
        y = director.window.height - height - 10
        
        content_size = (width - 26, height - 80)
        content_position = (3, 3)
        
        group_titles = ['Body', 'Engine', 'Tyres']
        layers = []
        
        # Body layer        
        body_layer = GridLayer(content_size, 4, 4, padding=2)
        body_layer.position = content_position
        button_size = (body_layer.column_width, body_layer.row_height)
        for part_id, properties in parts.body.items():
            button = LabelButton(properties['name'], button_size)
            body_layer.add(button)
        layers.append(body_layer)
        
        # Engines layer        
        engines_layer = GridLayer(content_size, 4, 4, padding=2)
        engines_layer.position = content_position
        button_size = (engines_layer.column_width, engines_layer.row_height)
        for part_id, properties in parts.engine.items():
            button = LabelButton(properties['name'], button_size)
            engines_layer.add(button)
        layers.append(engines_layer)
        
        # Tyres layer        
        tyres_layer = GridLayer(content_size, 4, 4, padding=2)
        tyres_layer.position = content_position
        button_size = (tyres_layer.column_width, tyres_layer.row_height)
        for part_id, properties in parts.tyres.items():
            button = LabelButton(properties['name'], button_size)
            tyres_layer.add(button)
        layers.append(tyres_layer)
        
        super(PartsFrame, self).__init__((width, height), group_titles,
            layers)
        
        self.position = (x, y)


class BalanceLayer(Layer):
    """Holds the current balance of the player and displays the balance
       after purchase of the selected parts."""
    
    def __init__(self):        
        super(BalanceLayer, self).__init__()
        
        x = 10
        
        self.position = (x, 10)
        self.width = 400
        self.height = 230
        
        heading = util.Label('Balance', font_size=18, x=x)
        heading.y = self.height - heading.height
        self.add(heading)
        
        y = heading.y - 30
        
        money = util.Label(str(state.profile.money), x=x, y=y, font_size=14,
            width=self.width, halign='right')
        self.add(money)
        
        y -= 20
        
        self.cost_label = util.Label('0', x=x, y=y, font_size=14,
            halign='right')
        self.add(self.cost_label)
        
        y -= 30
        
        self.balance_label = util.Label(str(state.profile.money), x=x, y=y,
            font_size=14, halign='right')
        self.add(self.balance_label)
        
    def set_cost(self, cost):
        """Sets the cost of the combined purchases. Updates the cost label
           as well as the balance after purchase label."""
        new_balance = state.profile.money - cost
        self.cost_label.text = str(cost)
        self.balance_label.text = str(new_balance)
    
    new_balance = property(lambda self: int(self.balance_label.text),
        doc="""Returns the new balance for the player after the combined
               purchases have been made. This is based on the value that was
               last passed to set_cost().""")


class LayoutLayer(Layer):
    def __init__(self, (width, height)):
        super(Layer, self).__init__()
        
        self.width = width
        self.height = height
        
        # Keep an internal record of children, as the list that is used by
        # the parent class is ordered by z-index.
        self.layout_children = []
    
    def add(self, child, *args, **kwargs):        
        super(LayoutLayer, self).add(child, *args, **kwargs)
        
        self.layout_children.append(child)
        self.reposition()
        
        # TODO: modify child position here
        
        return self # Don't break the chain.
    
    def _remove(self, child, *args, **kwargs):
        super(LayoutLayer, self).remove(child, *args, **kwargs)
        
        self.layout_children.remove(child)
        self.reposition()
        
        # TODO: modify other child positions here
        
        return self # Don't break the chain.
    
    def reposition(self):
        """Repositions all children to maintain layout."""
        raise NotImplementedError()
    
    # def translate_position(self, node):
    #     """Converts coordinates from bottom-to-top to top-bottom,
    #        turning the top-left corner of the layer into (0, 0)."""
    #     return (node.x, self.height - node.y - node.height)


class FlowLayer(LayoutLayer):
    """A layer that aligns its children like a Java SWING FlowLayout.
       Child elements are aligned from top to bottom, left to right, and
       are juxtaposed until the element that is about the be added would
       overflow its container. In that case, addition will continue on
       the next row.
       
       This layer modifies the position of the child element that is added."""
    
    def __init__(self, size, align='center'):
        super(FlowLayer, self).__init__(size)
        
        self.align = align
        
        raise NotImplementedError()


class GridLayer(LayoutLayer):
    """LayoutLayer that behaves like a Java SWING GridLayout. The layer is
       divided into equal cells based on the number of rows and columns passed
       to the constructor. Every element is put inside the next column, from
       top to bottom, left to right.
       
       If too many items are added, a RuntimeError is raised."""
    def __init__(self, size, rows, columns, padding=0):
        super(GridLayer, self).__init__(size)
        
        self.rows = rows
        self.columns = columns
        
        self.padding = padding
    
        self.row_height_full = self.height // rows
        self.column_width_full = self.width // columns
        
        self.row_height = self.row_height_full - self.padding * 2
        self.column_width = self.column_width_full - self.padding * 2
    
    def reposition(self):
        col_count = 0
        y = self.height - self.row_height_full
        for child in self.layout_children:
            x = self.column_width_full * col_count + self.padding
            this_y = max(y, y + self.row_height_full - child.height) + self.padding
            child.position = (x, this_y)
            col_count = (col_count + 1) % self.columns
            if col_count == 0:
                y -= self.row_height_full
                
                if y < 0:
                    raise RuntimeError("Too many items added.")


class Button(Layer):
    """Generic button class. This has button has no visual component, but takes
       care of detecting clicks on the button. Event handlers can be registered
       by calling on_click() on instances of this class.
       
       You can easily create a visual component for this Button by adding layers
       to it."""
    
    # Make sure cocos2d registers the on_mouse_press event handler for us
    # once this button is added to a visual layer.
    is_event_handler = True
    
    def __init__(self, (width, height)):
        super(Button, self).__init__()
        
        self.width = width
        self.height = height
        
        # We want to be able to maintain a list of handlers for button
        # clicks.
        self.click_handlers = []
    
    def on_click(self, method):
        """Registers a new on click event handler."""
        if method in self.click_handlers:
           raise RuntimeError("Method already registered.")

        self.click_handlers.append(method)

    def on_mouse_press(self, x, y, buttons, modifiers):
        """Pyglet callback that is automatically called whenever the mouse
           is pressed. This method takes care of checking if any action
           should be taken."""
        if self.collide_point(*director.get_virtual_coordinates(x, y)):
            for method in self.click_handlers:
                method()

    def collide_point(self, x, y):
       """Determines if a certain coordinate is inside the button's area."""
       bx, by = util.absolute_position(self)
       tx = bx + self.width
       ty = by + self.height

       return (x >= bx and y >= by and x <= tx and y <= ty)
      

class LabelButton(Button):
    def __init__(self, caption, (width, height),
       bg_color=(150, 150, 150, 255), fg_color=(0, 0, 0, 255),
       **kwargs):
       """Initializes a new button. Any additional keyword arguments are
          propagated to the label that is rendered on the button,
          enabling you to alter the font properties of the text. See
          the pyglet Label documentation for more information."""

       super(LabelButton, self).__init__((width, height))

       self.bg_layer = ColorLayer(*(bg_color + (width, height)))
       self.add(self.bg_layer, z=0)

       self.label = util.Label(caption, color=fg_color, anchor_x='center',
           anchor_y='center', x=self.width / 2, y=self.height / 2, **kwargs)
       self.add(self.label, z=1)

       self.click_handlers = []


class Bar(Layer):
    """Represents a filled bar, that can be used for progress bars."""

    def __init__(self, size, fill=0, bg_color=(100, 100, 100, 255),
       fill_color=(0, 255, 0, 255), padding=1):

       super(Bar, self).__init__()

       self.bg_layer = ColorLayer(*(bg_color + size))
       self.add(self.bg_layer, z=-2)

       # Determine the maximum amount of pixels the bar can be filled by.
       self.max_fill_width = self.bg_layer.width - padding * 4

       fill_size = (1, self.bg_layer.height - padding * 4)
       self.fill_layer = ColorLayer(*(fill_color + fill_size))
       self.fill_layer.position = (padding, padding)
       self.add(self.fill_layer, z=-1)

       # Set the initial fill.
       self.fill_bar(fill)

    def fill_bar(self, p):
       """Fills up the bar up to a certain percentage. Caps the results
          between sensible values."""
       bar_width = int(self.max_fill_width * min(p, 1))
       self.fill_layer.width = max(1, bar_width)
