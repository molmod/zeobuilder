# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2005 Toon Verstraelen
#
# This file is part of Zeobuilder.
#
# Zeobuilder is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# --


from zeobuilder import context
from zeobuilder.actions.composed import Interactive as InteractiveAction
from zeobuilder.gui import load_image

import gtk.gdk, copy


__all__ = [
    "Interactive", "InteractiveGroup", "InteractiveButton", "InteractiveBar"
]


empty_pixbuf = load_image("no_action.svg", (36, 36))


class InteractiveInfo(object):
    def __init__(self, image_name, mouse=False, keyboard=False, default_position=0, order=None):
        self.image_name = image_name
        self.mouse = mouse
        self.keyboard = keyboard
        self.default_position = default_position
        self.order = order


class InteractiveGroup(object):
    def __init__(self, image_name, description, initial_mask=None, order=None):
        # Gui related stuff
        self.image_name = image_name
        self.pixbuf = load_image(image_name, (36, 36))
        self.description = description
        self.initial_mask = initial_mask
        self.order = order
        # actions
        self.keyboard_actions = []
        self.mouse_actions = []
        self.handler_id = None

    def add_action(self, action):
        if action.interactive_info.keyboard:
            self.keyboard_actions.append(action)
        if action.interactive_info.mouse:
            self.mouse_actions.append(action)

    def get_mouse_candidate(self):
        result = None
        for action in self.mouse_actions:
            if action.cached_analyze_selection():
                return action

    def get_keyboard_candidate(self):
        for action in self.keyboard_actions:
            if action.cached_analyze_selection():
                return action

    def activate(self):
        pass

    def deactivate(self):
        pass


class InteractiveButton(gtk.Button):
    def __init__(self, keys_description, tooltips):
        gtk.Button.__init__(self)
        self.image = gtk.Image()
        self.add(self.image)
        self.keys_description = keys_description
        self.tooltips = tooltips
        self.interactive_group = None
        self.unset_interactive_group()

    def unset_interactive_group(self):
        self.tooltips.set_tip(self, "There are no actions associated with '%s'." % self.keys_description)
        self.image.set_from_pixbuf(empty_pixbuf)
        if self.interactive_group is not None:
            self.interactive_group.deactivate()
            self.interactive_group = None

    def set_interactive_group(self, interactive_group):
        self.tooltips.set_tip(self, interactive_group.description)
        self.image.set_from_pixbuf(interactive_group.pixbuf)
        self.interactive_group = interactive_group
        self.interactive_group.activate()


class InteractiveBar(gtk.Table):
    modifier_labels = [
        (0, "(no key)"),
        (gtk.gdk.SHIFT_MASK, "Shift"),
        (gtk.gdk.CONTROL_MASK, "Ctrl"),
        (gtk.gdk.SHIFT_MASK | gtk.gdk.CONTROL_MASK, "Shift Ctrl")
    ]

    def __init__(self):
        assert context.application.action_manager is not None
        self.start_button = 0
        # Interactive buttons (gui stuff)
        self.buttons = {}
        self.clicked_button = None
        gtk.Table.__init__(self, 2, 4)
        self.set_row_spacings(0)
        self.set_col_spacings(5)
        self.tooltips = gtk.Tooltips()
        for index, (modifier, label) in enumerate(self.modifier_labels):
            button = InteractiveButton(label, self.tooltips)
            button.connect("button-press-event", self.on_interactive_button_press_event)
            self.buttons[modifier] = button
            self.attach(button, index, index+1, 0, 1, xoptions=0, yoptions=0)
            label = gtk.Label("<small>%s</small>" % label)
            label.set_property("use_markup", True)
            self.attach(label, index, index+1, 1, 2, xoptions=0, yoptions=0)
        # Interactive events
        context.application.main.window.connect("key_press_event", self.key_press)
        context.application.main.window.connect("key_release_event", self.key_release)
        main = context.application.main
        main.drawing_area.add_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.BUTTON_MOTION_MASK)
        main.drawing_area.connect("button_press_event", self.button_press)
        main.drawing_area.connect("motion_notify_event", self.button_motion)
        main.drawing_area.connect("button_release_event", self.button_release)
        # Add interactive groups, and populate a dropdown menu
        self.group_menu = gtk.Menu()
        self.interactive_groups = {}
        groups = context.application.plugins.interactive_groups.values()
        groups.sort(key=(lambda g: g.order))
        for group in groups:
            self.interactive_groups[group.image_name] = group
            if group.initial_mask is not None:
                button = self.buttons[group.initial_mask]
                button.set_interactive_group(group)
            menu_item = gtk.ImageMenuItem()
            image = gtk.Image()
            image.set_from_pixbuf(load_image(group.image_name, (36, 36)))
            menu_item.set_image(image)
            label = gtk.Label(group.description)
            label.set_alignment(0.0, 0.5)
            menu_item.add(label)
            menu_item.connect("activate", self.on_menu_activate, group)
            self.group_menu.append(menu_item)
        self.group_menu.show_all()
        # Load the actions
        actions = [
            action
            for action
            in context.application.plugins.actions.itervalues()
            if action.interactive_info is not None
        ]
        actions.sort(key=(lambda a: a.interactive_info.order))
        for action in actions:
            group = self.interactive_groups[action.interactive_info.image_name]
            group.add_action(action)


    #
    # Switching between interactive groups that are assigned to a button
    #

    def on_interactive_button_press_event(self, button, event):
        def top_right(menu):
            xo, yo = button.window.get_origin()
            return (
                xo + button.allocation.x + button.allocation.width,
                yo + button.allocation.y,
                False
            )

        self.group_menu.popup(None, None, top_right, event.button, gtk.get_current_event_time())
        self.clicked_button = button

    def on_menu_activate(self, menu_item, new_group):
        self.clicked_button.unset_interactive_group()
        for button in self.buttons.itervalues():
            if button.interactive_group == new_group:
                button.unset_interactive_group()
        self.clicked_button.set_interactive_group(new_group)
        self.clicked_button = None

    #
    # Interactive events on the drawing area are forwarded to the appropriate
    # action with the following methods.
    #

    def button_press(self, drawing_area, event):
        # make sure there is no action running, else quit.
        current_action = context.application.action_manager.current_action
        if current_action is not None:
            if isinstance(current_action, InteractiveAction):
                # a button_release did'nt happen for some reason
                current_action.finish()
            else:
                return
        # if the user points an object, treat it as if it is the first selected
        # object.
        hit = drawing_area.get_nearest(event.x, event.y)
        nodes = context.application.cache.nodes
        if (hit is not None) and len(nodes) == 0:
            nodes.insert(0, hit)
        # create the action
        interactive_group = self.buttons[event.state & (gtk.gdk.SHIFT_MASK | gtk.gdk.CONTROL_MASK)].interactive_group
        if interactive_group is None: return
        candidate = interactive_group.get_mouse_candidate()
        if candidate is None: return
        current_action = candidate()
        self.start_button = event.button
        if hasattr(current_action, "button_press"):
            current_action.button_press(drawing_area, event)

    def button_motion(self, drawing_area, event):
        current_action = context.application.action_manager.current_action
        if (current_action is not None) and \
           isinstance(current_action, InteractiveAction) and \
           hasattr(current_action, "button_motion"):
            current_action.button_motion(drawing_area, event, self.start_button)

    def button_release(self, drawing_area, event):
        current_action = context.application.action_manager.current_action
        if current_action is not None and \
           isinstance(current_action, InteractiveAction) and \
           hasattr(current_action, "button_release"):
            current_action.button_release(drawing_area, event)
        self.start_button = 0

    def key_press(self, widget, event):
        if event.keyval in [65406, 65505, 65506, 65507, 65508, 65513, 65515]: return False
        current_action = context.application.action_manager.current_action
        if current_action is not None:
            if not isinstance(current_action, InteractiveAction):
                return
        else:
            interactive_group = self.buttons[event.state & (gtk.gdk.SHIFT_MASK | gtk.gdk.CONTROL_MASK)].interactive_group
            if interactive_group is None: return
            candidate = interactive_group.get_keyboard_candidate()
            if (candidate is None) or (event.keyval not in candidate.sensitive_keys): return
            current_action = candidate()

        if hasattr(current_action, "key_press"):
            current_action.key_press(context.application.main.drawing_area, event)
            return True

    def key_release(self, widget, event):
        current_action = context.application.action_manager.current_action
        if current_action is not None and \
           isinstance(current_action, InteractiveAction) and \
           hasattr(current_action, "key_release"):
            current_action.key_release(context.application.main.drawing_area, event)
            return True
