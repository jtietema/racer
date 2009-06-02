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


# TODO: show popup when leaving shop after changes have been made.


class Shop(Scene):
    def __init__(self):
        super(Shop, self).__init__()
        
        # Make sure the car's properties set during previous scenes are
        # reset to their initial state.
        state.profile.car.reset()
        
        # Copy original car to calculate price differences.
        self.car = copy.copy(state.profile.car)
        
        self.balance_layer = BalanceLayer(self.car)
        self.button_layer = ButtonLayer()
        
        self.add(PreviewFrame(self.car))
        self.add(PartsFrame(self.car))
        self.add(self.balance_layer)
        self.add(self.button_layer)
    
    new_balance = property(lambda self: self.balance_layer.new_balance)
    
    def update(self):
        # Note that the order is significant; button layer requests updated
        # data from balance layer.
        self.balance_layer.update()
        self.button_layer.update()
    
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

    def previous_group(self, *args, **kwargs):
        self.switch_group(-1)

    def next_group(self, *args, **kwargs):
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
    
    def __init__(self, car):
        width, height = 400, 500
        x = 10
        y = director.window.height - height - 10
        
        super(PreviewFrame, self).__init__((width, height),
            content_bg_color=(50, 50, 50, 255))
        
        self.position = (x, y)
        
        self.car = car
        
        # Draw the car.
        self.car.scale = 1
        self.car.x = self.content_layer.width / 2
        self.car.y = self.content_layer.height / 2 - 40
        self.content_layer.add(self.car)
        
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
    
    def __init__(self, car):
        width = 598
        height = 500
        x = director.window.width - width - 10
        y = director.window.height - height - 10
        
        group_titles = []
        layers = []
        
        self.car = car
        
        # Keep track of the highlighted button per group.
        self.highlighted_buttons = {}
        
        # Body layer        
        group_titles.append('Body')
        layers.append(self.create_parts_layer('body', width, height))
        
        # Engines layer
        group_titles.append('Engine')
        layers.append(self.create_parts_layer('engine', width, height))
        
        # Tyres layer
        group_titles.append('Tyres')
        layers.append(self.create_parts_layer('tyres', width, height))
        
        super(PartsFrame, self).__init__((width, height), group_titles,
            layers)
        
        self.position = (x, y)
    
    def create_parts_layer(self, group_name, width, height):
        layer = GridLayer((width - 26, height - 80), 3, 4, padding=2)
        layer.position = (3, 3)
        button_size = (layer.column_width, layer.row_height)
        for part_id, properties in parts.options[group_name].items():
            button = PartButton(properties.get('image'), properties['name'],
                properties['price'], button_size)

            button.on_click(util.curry(self.select_part, group_name,
                part_id))

            if part_id == getattr(self.car, group_name):
                self.highlighted_buttons[group_name] = button
                button.highlight()

            layer.add(button)
            
        return layer
    
    def select_part(self, group, part_id, button):
        self.highlighted_buttons[group].unhighlight()
        button.highlight()
        self.highlighted_buttons[group] = button
        
        setattr(self.car, group, part_id)
        
        self.parent.update()


class BalanceLayer(Layer):
    """Holds the current balance of the player and displays the balance
       after purchase of the selected parts."""
    
    def __init__(self, car):        
        super(BalanceLayer, self).__init__()
        
        x = 10
        real_x = x + 20
        
        self.position = (x, 10)
        self.width = 400
        self.height = 230
        
        self.car = car
        
        heading = util.Label('Balance', font_size=18, x=x)
        heading.y = self.height - heading.height
        self.add(heading)
        
        y = heading.y - 30
        
        money = util.Label(str(state.profile.money), x=real_x, y=y, font_size=14,
            width=self.width, halign='right')
        self.add(money)
        
        y -= 20
        
        self.cost_label = util.Label('0', x=real_x, y=y, font_size=14,
            halign='right')
        self.add(self.cost_label)
        
        minus_label = util.Label('-', x=x, y=y, font_size=14, halign='left')
        self.add(minus_label)
        
        y -= 30
        
        self.balance_label = util.Label(str(state.profile.money), x=real_x, y=y,
            font_size=14, halign='right')
        self.add(self.balance_label)
        
    def set_cost(self, cost):
        """Sets the cost of the combined purchases. Updates the cost label
           as well as the balance after purchase label."""
        new_balance = state.profile.money - cost
        self.cost_label.text = str(cost)
        self.balance_label.text = str(new_balance)
    
    def update(self):
        """Updates the layer based on the car's state."""
        self.set_cost(self.car.cost)
    
    new_balance = property(lambda self: int(self.balance_label.text),
        doc="""Returns the new balance for the player after the combined
               purchases have been made. This is based on the value that was
               last passed to set_cost().""")


class ButtonLayer(Layer):
    def __init__(self):
        super(ButtonLayer, self).__init__()
        
        self.width = 598
        self.height = 230
        self.x = director.window.width - self.width - 10
        self.y = 10
        
        button_size = (100, 50)
        bg_color = util.color_from_hex('#FF892E') + (255,)
        
        cancel_button = LabelButton('Cancel', button_size, bg_color=bg_color)
        cancel_button.position = (self.width - cancel_button.width, 0)
        cancel_button.on_click(self.cancel)
        self.add(cancel_button)
        
        self.ok_button = LabelButton('OK', button_size, bg_color=bg_color)
        self.ok_button.position = (cancel_button.x - self.ok_button.width - 20, 0)
        self.ok_button.on_click(self.ok)
        self.add(self.ok_button)
    
    def ok(self, *args, **kwargs):
        self.parent.commit()
    
    def cancel(self, *args, **kwargs):
        self.parent.cancel()
    
    def update(self):
        if self.parent.new_balance < 0:
            self.ok_button.enabled = False

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
        disabled_opacity=0.5, **kwargs):
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
        
        self.enabled_opacity = bg_color[3]
        self.disabled_bg_color = int(bg_color[3] * disabled_opacity)
        
        self._enabled = True
        self.enabled = property(lambda self: self._enabled, self._set_enabled)
    
    def _set_enabled(self, enabled):
        self._enabled = enabled
        
        if enabled:
            self.bg_layer.opacity = self.enabled_opacity
        else:
            self.bg_layer.opacity = self.disabled_opacity


class PartButton(Button):
    HIGHLIGHT_BG_COLOR = (50, 50, 50, 255)
    
    def __init__(self, image, caption, price, (width, height)):
        super(PartButton, self).__init__((width, height))
        
        center_x = self.width / 2
        label_top_margin = 10
        
        price_label = util.Label(str(price), color=(255,) * 4, anchor_x='center',
           anchor_y='bottom', x=center_x, y=0)
        self.add(price_label, z=1) 
        
        name_label = util.Label(caption, color=(255,) * 4, anchor_x='center',
           anchor_y='bottom', x=center_x, y=price_label.height + 3)
        self.add(name_label, z=1)
        
        # Part image
        if image is not None:
            img = pyglet.image.load('img/' + image)
        
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
