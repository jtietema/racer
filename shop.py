# -*- coding: utf-8 -*-

# This file is part of RCr and copyright (C) Maik Gosenshuis and 
# Jeroen Tietema 2008-09.
#
# RCr is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RCr is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with RCr.  If not, see <http://www.gnu.org/licenses/>.

import os
from string import capwords
import copy

import cocos
from cocos.director import director
from cocos.layer import Layer, ColorLayer, MultiplexLayer
from cocos.scene import Scene
from cocos.sprite import Sprite
import pyglet

import util
import parts
from game_state import state


HEADER_BG_COLOR = (150, 0, 0, 255)
HEADER_FG_COLOR = (255,) * 4


# TODO: show popup when leaving shop after changes have been made.


class Shop(Scene):
    def __init__(self):
        super(Shop, self).__init__()
        
        # Make sure the car's properties set during previous scenes are
        # reset to their initial state.
        state.profile.car.reset()
        
        # Copy original car to calculate price differences.
        self.car = copy.copy(state.profile.car)
        
        self.sub_layers = {
            'preview':  PreviewFrame(self.car),
            'parts':    PartsFrame(self.car),
            'balance':  BalanceLayer(self.car),
            'button':   ButtonLayer(self.car)
        }
        
        for sub_layer in self.sub_layers.values():
            self.add(sub_layer)
        
        # Header
        header_bg = ColorLayer(*(HEADER_BG_COLOR + (director.window.width, 100)))
        header_bg.position = (0, director.window.height - header_bg.height)
        self.add(header_bg, z=1)
        
        header = util.Label('Shop', font_name='Lizzie', font_size=60,
            color=HEADER_FG_COLOR, anchor_y='top', anchor_x='right')
        header.x = director.window.width - 20
        header.y = director.window.height - 5
        self.add(header, z=2)
    
    def reset(self):
        self.car = copy.copy(state.profile.car)
        
        for sub_layer in self.sub_layers.values():
            sub_layer.car = self.car
            sub_layer.reset()
    
    new_balance = property(lambda self: self.sub_layers['balance'].new_balance)
    
    def update(self):
        # Note that the order is significant; button layer requests updated
        # data from balance layer.
        for sub_layer in self.sub_layers.values():
            sub_layer.update()
    
    def commit(self):
        """Commits the changes of the modified car to the profile."""
        assert self.new_balance >= 0
        
        state.profile.money = self.new_balance
        state.profile.car = self.car
        state.profile.save()
        director.pop()
        
    def cancel(self):
        director.pop()


class Frame(Layer):
    """Abstract frame view for usage inside the shop."""

    def __init__(self, (width, height), border_width=5, padding=5,
        border_color=(255, 255, 255, 255), content_bg_color=(0, 0, 0, 255),
        *args, **kwargs):

        super(Frame, self).__init__()
        
        self.padding = padding

        self.border_layer = ColorLayer(*(border_color + (width, height)))
        self.add(self.border_layer, z=-2)

        content_bg_size = (width - border_width * 2, height - border_width * 2)
        content_bg = ColorLayer(*(content_bg_color + content_bg_size))
        content_bg.position = (border_width, border_width)
        self.add(content_bg, z=-1)
        
        self.content_layer = Layer()
        self.content_layer.width = content_bg_size[0] - padding * 2
        self.content_layer.height = content_bg_size[1] - padding * 2
        self.content_layer.position = (padding, padding)
        content_bg.add(self.content_layer)
    
    size = property(lambda self: (self.width, self.height))
    
    content_size = property(lambda self: (self.content_layer.width,
        self.content_layer.height))


class SpinnerFrame(Frame):
    """Abstract specialized frame to display layers in several groups, with
       group navigation at the top."""

    def __init__(self, size, *args, **kwargs):
        super(SpinnerFrame, self).__init__(size, *args, **kwargs)
        
        self.group_titles = None
        self.layers = None

        # Build the navigation panel.
        button_size = (35, 35)
        button_options = {'font_size': 16, 'bold': True}
        nav_y = self.content_layer.height - button_size[1]

        prev_button = LabelButton('<', button_size, **button_options)
        prev_button.position = (0, nav_y)
        prev_button.on_click(self.previous_group)
        self.content_layer.add(prev_button)

        right_x = self.content_layer.width - button_size[0]
        next_button = LabelButton('>', button_size, **button_options)
        next_button.position = (right_x, nav_y)
        next_button.on_click(self.next_group)
        self.content_layer.add(next_button)

        center_x = self.content_layer.width / 2
        center_y = nav_y + 15
        self.group_label = util.Label('', x=center_x, y=center_y,
            width=self.content_layer.width, anchor_x='center',
            anchor_y='center', font_size=16)
        self.content_layer.add(self.group_label)
    
    def set_groups(self, group_titles, layers):
        assert len(group_titles) == len(layers)
        
        self.current_index = 0
        self.group_titles = group_titles

        # Add the different layers inside a MultiplexLayer, so we can easily
        # and quickly switch between them.
        if self.layers is not None:
            self.content_layer.remove(self.layers)
        self.layers = MultiplexLayer(*layers)
        self.content_layer.add(self.layers)
        
        self.group_label.text = self.group_titles[self.current_index]

    def switch_group(self, step):
        index = abs((self.current_index + step) % len(self.group_titles))

        self.layers.switch_to(index)
        self.group_label.text = self.group_titles[index]

        self.current_index = index

    def previous_group(self, *args, **kwargs):
        self.switch_group(-1)

    def next_group(self, *args, **kwargs):
        self.switch_group(1)
    
    # TODO: dynamic
    navbar_size = property(lambda self: (self.content_layer.width, 35))
    def _get_content_size(self):
        return (self.content_layer.width,
            self.content_layer.height - self.navbar_size[1] - self.padding)
    content_size = property(_get_content_size,
        doc="""Returns the size of the actual content area, the area of the
               frame below the navigation elements.""")


class PreviewFrame(Frame):
    """Frame to hold the car's preview representation."""
    
    def __init__(self, car):
        width, height = 400, 500
        x = 10
        y = director.window.height - height - 110
        
        super(PreviewFrame, self).__init__((width, height),
            content_bg_color=(50, 50, 50, 255))
        
        self.position = (x, y)
        
        self.car = car
        
        # Draw the car.
        self.update_car()
        
        # Add car property bars.
        bar_size = (240, 20)
        bar_x = 140
        bar_y = self.content_layer.height - bar_size[1]
        for bar_type in ('speed','grip','acceleration'):
            # Label
            label_text = capwords(bar_type)
            label = util.Label(label_text, font_size=12)
            label.position = (5, bar_y + 4)
            self.content_layer.add(label)
            
            # Bar
            bar = Bar(bar_size)
            bar.position = (bar_x, bar_y)
            self.content_layer.add(bar, name=bar_type)
            
            bar_y -= 25
        
        self.update()
        
    def update(self):
        # TODO: all properties
        for bar_type in ('grip',):
            self.content_layer.get(bar_type).fill_bar(getattr(self.car, bar_type))
    
    def update_car(self):
        try:
            self.content_layer.remove('car')
        except Exception:
            pass
        
        self.car.scale = 1
        self.car.x = self.content_layer.width / 2
        self.car.y = self.content_layer.height / 2 - 40
        self.content_layer.add(self.car, name='car')
    
    def reset(self):
        self.update_car()
        self.update()        


class PartsFrame(SpinnerFrame):
    """Holds all the parts that can be selected for the car. Also highlights
       the currently selected parts."""
    
    def __init__(self, car):
        width = 598
        height = 500
        x = director.window.width - width - 10
        y = director.window.height - height - 110
        
        super(PartsFrame, self).__init__((width, height))
        
        self.position = (x, y)
        
        self.car = car
        
        self.part_types = ('body','engine','tyres')
        
        # Set up the layers.
        group_titles = []
        layers = []
        
        # Keep track of the highlighted button per group.
        self.highlighted_buttons = {}
        
        for part_type in self.part_types:
            group_titles.append(capwords(part_type))
            layers.append(self.create_parts_layer(part_type))
        
        self.set_groups(group_titles, layers)
        
        self.set_initial_highlights()
    
    def create_parts_layer(self, part_type):
        layer = GridLayer(self.content_size, 3, 4, spacing=4)
        button_size = (layer.column_width, layer.row_height)
        for part in parts.manager.get_parts_by_type(part_type):                
            button = PartButton(part, button_size)

            button.on_click(util.curry(self.select_part, part_type,
                part))

            layer.add(button)
            
        return layer
    
    def set_initial_highlights(self):
        for index, layer in enumerate(self.layers.layers):
            try:
                layer.current_part_button.remove('current_bg')
            except Exception:
                pass
            
            part_type = self.part_types[index]
            
            for button in layer.layout_children:
                button.unhighlight()
                
                if button.part == getattr(self.car, part_type):                    
                    layer.current_part_button = button
                    button.add(ColorLayer(50, 50, 50, 100, button.width,
                        button.height), z=-1, name='current_bg')
                    self.highlighted_buttons[part_type] = button
                    button.highlight()
    
    def select_part(self, part_type, part_id, button):
        self.highlighted_buttons[part_type].unhighlight()
        button.highlight()
        self.highlighted_buttons[part_type] = button
        
        setattr(self.car, part_type, part_id)
        
        self.parent.update()
    
    def update(self):
        pass
    
    def reset(self):
        self.set_initial_highlights()


class BalanceLayer(Layer):
    """Holds the current balance of the player and displays the balance
       after purchase of the selected parts."""
    
    def __init__(self, car):        
        super(BalanceLayer, self).__init__()
        
        x = 10
        minus_x = x + 80
        real_x = x + 100
        
        self.position = (x, 10)
        self.width = 400
        self.height = 130
        
        self.car = car
        
        # Heading
        heading = util.Label('Balance', font_size=18, x=x)
        heading.y = self.height - heading.height
        self.add(heading)
        
        # Current money
        y = heading.y - 30
        
        money_label = util.Label('Money:', x=x, y=y, font_size=12, width=100)
        self.add(money_label)
        
        money = util.Label(str(state.profile.money), x=real_x, y=y, font_size=14,
            width=self.width, halign='right')
        self.add(money)
        
        # Cost
        y -= 20
        
        cost_label_label = util.Label('Cost:', x=x, y=y, font_size=12, width=100)
        self.add(cost_label_label)
        
        self.cost_label = util.Label('0', x=real_x, y=y, font_size=14,
            width=self.width, halign='right')
        self.add(self.cost_label)
        
        # Separator line
        y -= 15
        line = cocos.draw.Line((x, y), (self.width - 10, y),
            (255, 255, 255, 255))
        self.add(line)
        
        # Balance after purchase
        y -= 25
        
        balance_label_label = util.Label('Balance:', x=x, y=y,
            width=100, font_size=12)
        self.add(balance_label_label)
        
        self.balance_label = util.Label(str(state.profile.money), x=real_x, y=y,
            width=self.width, font_size=14, halign='right')
        self.add(self.balance_label)
        
        self.balance_minus_label = util.Label('-', x=minus_x, y=y, font_size=14,
            halign='left', color=(255, 0, 0, 255))
        
    def set_cost(self, cost):
        """Sets the cost of the combined purchases. Updates the cost label
           as well as the balance after purchase label."""
        self.cost_label.text = str(cost)
        new_balance = self.new_balance
        
        self.balance_label.text = str(abs(new_balance))
        contains_minus = self.balance_minus_label in self
        if new_balance < 0:
            if not contains_minus:
                self.add(self.balance_minus_label)
            
            self.balance_label.color = (255, 0, 0, 255)
        else:
            if contains_minus:
                self.remove(self.balance_minus_label)
            
            self.balance_label.color = (255, 255, 255, 255)            
    
    def update(self):
        """Updates the layer based on the car's state."""
        current_car = state.profile.car
        cost = 0
        for part_type, part in self.car.parts.items():
            # Only add the price of the item if the player does not own the
            # part currently.
            if not getattr(current_car, part_type) == part:
                cost += part.price
        
        self.set_cost(cost)
    
    def reset(self):
        self.set_cost(0)
    
    new_balance = property(lambda self: state.profile.money - int(self.cost_label.text),
        doc="""Returns the new balance for the player after the combined
               purchases have been made. This is based on the value that was
               last passed to set_cost().""")


class ButtonLayer(Layer):
    def __init__(self, car):
        super(ButtonLayer, self).__init__()
        
        self.car = car
        
        self.width = 598
        self.height = 130
        self.x = director.window.width - self.width - 10
        self.y = 10
        
        button_size = (175, 50)
        
        y = self.height - button_size[1] - 10
        
        common_properties = {
            'bg_color': HEADER_BG_COLOR,
            'fg_color': HEADER_FG_COLOR,
            'bold': True,
            'font_size': 20,
            'font_name': 'Lizzie'
        }
        
        cancel_button = LabelButton('Cancel', button_size, **common_properties)
        cancel_button.position = (self.width - cancel_button.width, y - button_size[1] - 10)
        cancel_button.on_click(self.on_cancel)
        self.add(cancel_button)
        
        self.reset_button = LabelButton('Reset', button_size, enabled=False,
            **common_properties)
        self.reset_button.position = (self.width - cancel_button.width, y)
        self.reset_button.on_click(self.on_reset)
        self.add(self.reset_button)
        
        self.ok_button = LabelButton('Buy', button_size, enabled=False,
            **common_properties)
        self.ok_button.position = (self.reset_button.x - self.ok_button.width - 10, y)
        self.ok_button.on_click(self.on_ok)
        self.add(self.ok_button)
    
    def on_ok(self, *args, **kwargs):
        self.parent.commit()
    
    def on_reset(self, *args, **kwargs):
        self.parent.reset()
    
    def on_cancel(self, *args, **kwargs):
        self.parent.cancel()
    
    def reset(self):
        self.reset_button.enabled = False
    
    def update(self):
        different_config = not self.car.has_same_configuration_as(state.profile.car)
        self.ok_button.enabled = (self.parent.new_balance >= 0 and different_config)
        self.reset_button.enabled = different_config
        

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
        
        return self # Don't break the chain.
    
    def _remove(self, child, *args, **kwargs):
        super(LayoutLayer, self).remove(child, *args, **kwargs)
        
        self.layout_children.remove(child)
        self.reposition()
        
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
    def __init__(self, size, rows, columns, spacing=0):
        super(GridLayer, self).__init__(size)
        
        self.rows = rows
        self.columns = columns
        
        self.spacing = spacing
        
        self.row_height = (self.height - ((rows - 1) * self.spacing)) // rows
        self.column_width = (self.width - ((columns - 1) * self.spacing)) // columns
    
    def reposition(self):
        col_count = 0
        y = self.height - self.row_height
        for child in self.layout_children:
            x = (self.column_width + self.spacing) * col_count
            child.position = (x, y)
            col_count = (col_count + 1) % self.columns
            if col_count == 0:
                y -= self.row_height + self.spacing
                
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
        
        self.enabled = True
    
    def on_click(self, method):
        """Registers a new on click event handler."""        
        if method in self.click_handlers:
           raise RuntimeError("Method already registered.")

        self.click_handlers.append(method)

    def on_mouse_press(self, x, y, buttons, modifiers):
        """Pyglet callback that is automatically called whenever the mouse
           is pressed. This method takes care of checking if any action
           should be taken."""
        if self.enabled and self.collide_point(*director.get_virtual_coordinates(x, y)):
            for method in self.click_handlers:
                method(self)

    def collide_point(self, x, y):
       """Determines if a certain coordinate is inside the button's area."""
       bx, by = util.absolute_position(self)
       tx = bx + self.width
       ty = by + self.height

       return (x >= bx and y >= by and x <= tx and y <= ty)
      

class LabelButton(Button):
    def __init__(self, caption, (width, height),
        bg_color=(150, 150, 150, 255), fg_color=(0, 0, 0, 255),
        disabled_opacity=0.5, enabled=True, **kwargs):
        """Initializes a new button. Any additional keyword arguments are
           propagated to the label that is rendered on the button,
           enabling you to alter the font properties of the text. See
           the pyglet Label documentation for more information."""
        
        self.enabled_opacity = bg_color[3]
        self.disabled_opacity = int(bg_color[3] * disabled_opacity)
        
        super(LabelButton, self).__init__((width, height))
        
        if not enabled:
            bg_color = bg_color[:3] + (self.disabled_opacity,)

        self.bg_layer = ColorLayer(*(bg_color + (width, height)))
        self.add(self.bg_layer, z=0)

        if not enabled:
            fg_color = fg_color[:3] + (self.disabled_opacity,)
            
        self.label = util.Label(caption, color=fg_color, anchor_x='center',
           anchor_y='center', x=self.width / 2, y=self.height / 2, **kwargs)
        self.add(self.label, z=1)

        self.click_handlers = []
    
    def _set_enabled(self, enabled):
        self._enabled = enabled
        
        # Bah.
        if hasattr(self, 'bg_layer'):
            if enabled:
                self.bg_layer.opacity = self.enabled_opacity
                self.label.opacity = self.enabled_opacity
            else:
                self.bg_layer.opacity = self.disabled_opacity
                self.label.opacity = self.disabled_opacity
    enabled = property(lambda self: self._enabled, _set_enabled,
        doc="""Disables any on_click callbacks and decreases the button's
            background opacity to visualize it being enabled. Note that it is
            impossible to change the enabled property on the
            LabelButton before it is actually visible in a Scene. If you want
            to set the button's initial state, use the 'enabled' keyword
            argument in the init method.""")


class PartButton(Button):
    HIGHLIGHT_BG_COLOR = (50, 50, 50, 255)
    
    def __init__(self, part, (width, height),
        price_color=(255,) * 4, name_color=(255,) * 4):
        super(PartButton, self).__init__((width, height))
        
        self.part = part
        
        center_x = self.width / 2
        label_top_margin = 10
        
        price_label = util.Label(str(part.price), color=price_color, anchor_x='center',
           anchor_y='bottom', x=center_x, y=0)
        self.add(price_label, z=1) 
        
        name_label = util.Label(part.name, color=name_color, anchor_x='center',
           anchor_y='bottom', x=center_x, y=price_label.height + 3)
        self.add(name_label, z=1)
        
        # Part image
        if part.image is not None:
            img = pyglet.image.load('img/' + part.image)
        
            # The total height the label area of the button occupies.
            labels_height = name_label.element.y + name_label.height + label_top_margin
        
            max_width = width * 1.0
            max_height = (height - labels_height - 5) * 1.0
            scale = min([max_width / img.width, max_height / img.height, 1])
        
            image_y = labels_height + (max_height / 2)
            self.image = Sprite(img, scale=scale,
                position=(center_x, image_y))
            self.add(self.image, z=1)
        
        self.bg_layer = None
    
    def highlight(self):
        """Highlights this part, meaning it is selected as the current part."""
        if self.bg_layer:
            return
        
        self.bg_layer = ColorLayer(*(PartButton.HIGHLIGHT_BG_COLOR
            + (self.width, self.height)))
        self.add(self.bg_layer, z=0)
    
    def unhighlight(self):
        """Removes the highlight for this button (if any)."""
        if self.bg_layer:
            self.remove(self.bg_layer)
            self.bg_layer = None
    

class Bar(Layer):
    """Represents a filled bar, that can be used for progress bars."""

    def __init__(self, size, fill=0, bg_color=(100, 100, 100, 255),
        fill_color=(0, 255, 0, 255), padding=2):

        super(Bar, self).__init__()
        
        self.padding = padding
        self.fill_color = fill_color
        
        assert self.padding * 2 < size[1]

        self.bg_layer = ColorLayer(*(bg_color + size))
        self.add(self.bg_layer, z=-2)

        # Determine the maximum amount of pixels the bar can be filled by.
        self.max_fill_width = self.bg_layer.width - padding * 2

        # Set the initial fill.
        self.fill_bar(fill)

    def fill_bar(self, p):
        """Fills up the bar up to a certain percentage. Caps the results
           between sensible values."""
        try:
            self.remove('fill')
        except Exception:
            pass
        
        fill_width = max(1, int(self.max_fill_width * min(p, 1)))
        fill_size = (fill_width, self.bg_layer.height - self.padding * 2)
        self.fill_layer = ColorLayer(*(self.fill_color + fill_size))
        self.fill_layer.position = (self.padding,) * 2
        self.add(self.fill_layer, z=-1, name='fill')
