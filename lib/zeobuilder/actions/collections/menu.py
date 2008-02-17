# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 - 2008 Toon Verstraelen <Toon.Verstraelen@UGent.be>
#
# This file is part of Zeobuilder.
#
# Zeobuilder is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# Zeobuilder is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
# --


from zeobuilder import context
from zeobuilder.actions.composed import Action
from zeobuilder.gui import load_image

import gtk.gdk

import copy, os


__all__ = ["Menu", "MenuInfo", "MenuInfoBase"]


class MenuInfoBase(object):
    def __init__(self, path, accel_key=None, accel_control=True, accel_shift=False, image_name=None, order=(99999,)):
        self.path = path
        self.accel_key = accel_key
        self.accel_control = accel_control
        self.accel_shift = accel_shift
        self.image_name = image_name
        self.order = order

    def get_label(self):
        raise NotImplementedError


class MenuInfo(MenuInfoBase):
    def __init__(self, path, label="*", accel_key=None, accel_control=True, accel_shift=False, image_name=None, order=(99999,)):
        self.label = label
        MenuInfoBase.__init__(self, path, accel_key, accel_control, accel_shift, image_name, order)

    def get_label(self):
        return self.label


def reduce_path(path, separator):
    slash_index = int(path.find(separator))
    if slash_index < 0:
        first = path
        rest = ""
    else:
        first = path[:slash_index]
        rest = path[slash_index+1:]
    return first, rest


class MenuActionContainer(object):
    def __init__(self):
        self.items = []
        self.mapped_items = {}
        parent = None

    def add_item(self, name, item):
        assert name not in self.mapped_items
        if isinstance(item, MenuActionContainer):
            item.parent = self
        self.mapped_items[name] = item
        self.items.append((name, item))

    def get_item(self, name):
        result = self.mapped_items.get(name)
        if result is None:
            result = self.create_default_item()
            self.add_item(name, result)
        return result

    def create_default_item(self):
        raise NotImplementedError

    def get_item_by_path(self, path, separator):
        if path == "":
            return self
        first, rest = reduce_path(path, separator)
        return self.get_item(first).get_item_by_path(rest)


class SubMenu(MenuActionContainer):
    def create_default_item(self):
        return Place()

    def get_item_by_path(self, path):
        return MenuActionContainer.get_item_by_path(self, path, "/")

    def fill_menu(self, menu, on_activate, on_expose, accel_group, only_show_applicable=True):
        former_added = None
        something_added = False
        separator = None
        for name, item in self.items:
            former_added = item.fill_menu(menu, on_activate, on_expose, accel_group, only_show_applicable)
            if former_added:
                separator = gtk.SeparatorMenuItem()
                menu.append(separator)
            something_added |= former_added
        if separator is not None:
            separator.destroy()
        return something_added


class Place(MenuActionContainer):
    def add_action(self, name, action):
        self.add_item(name, action)

    def create_default_item(self):
        return SubMenu()

    def get_item_by_path(self, path):
        return MenuActionContainer.get_item_by_path(self, path, ":")

    def fill_menu(self, menu, on_activate, on_expose, accel_group, only_show_applicable=True):
        something_added = False
        for name, item in self.items:
            if isinstance(item, SubMenu):
                new_menu = gtk.Menu()
                former_added = item.fill_menu(new_menu, on_activate, on_expose, accel_group, only_show_applicable)
                if not former_added and only_show_applicable:
                    new_menu.destroy()
                else:
                    something_added = True
                    menu_item = gtk.MenuItem(name)
                    menu.append(menu_item)
                    menu_item.set_submenu(new_menu)
            elif issubclass(item, Action):
                if not only_show_applicable or item.cached_analyze_selection():
                    something_added = True
                    if item.menu_info.image_name is not None:
                        if gtk.stock_lookup(item.menu_info.image_name) is not None:
                            menu_item = gtk.ImageMenuItem(item.menu_info.image_name)
                            menu_item.get_child().set_label(name)
                        else:
                            menu_item = gtk.ImageMenuItem(name)
                            menu_item.get_image().set_from_pixbuf(
                                load_image(item.menu_info.image_name, (18, 18))
                            )
                    else:
                        menu_item = gtk.MenuItem(name)
                    if item.menu_info.accel_key is not None:
                        menu_item.add_accelerator(
                            "activate",
                            accel_group,
                            item.menu_info.accel_key,
                            (gtk.gdk.CONTROL_MASK*item.menu_info.accel_control) | (gtk.gdk.SHIFT_MASK*item.menu_info.accel_shift),
                            gtk.ACCEL_VISIBLE | gtk.ACCEL_LOCKED
                        )
                    menu.append(menu_item)
                    menu_item.connect("activate", on_activate, item)
                    if on_expose is not None:
                        menu_item.connect("expose-event", on_expose, item)
            else:
                raise AssertionError
        return something_added


class Menu(object):
    def __init__(self):
        self.main_menu = SubMenu()

        self.accel_group = gtk.AccelGroup()
        context.application.main.window.add_accel_group(self.accel_group)
        self.accel_group.connect("accel-activate", self.set_all_menu_items_sensitive)
        self.all_menu_items_sensitive = False

        self.load_actions()

    def load_actions(self):
        """Runs over all the actions plugins and selects those with a MenuInfo."""

        actions = []
        for action in context.application.plugins.actions.itervalues():
            if action.menu_info is not None:
                actions.append(action)
        actions.sort(key=(lambda a: a.menu_info.order))
        for action in actions:
            self.add_action(action)

    def add_place(self, path, place_name):
        submenu = self.main_menu.get_item_by_path(path)
        submenu.add_place(place_name)

    def add_submenu(self, path, submenu_name):
        place = self.main_menu.get_item_by_path(path)
        place.add_submenu(submenu_name)

    def add_action(self, action):
        place = self.main_menu.get_item_by_path(action.menu_info.path)
        place.add_action(action.menu_info.get_label(), action)

    def fill_menubar(self, menubar):
        self.fill_menu(menubar, self.on_analyse, False)
        self.menubar = menubar

    def popup(self, event_button, event_time):
        popup_menu = gtk.Menu()
        self.fill_menu(popup_menu, None, True)
        if len(popup_menu.get_children()) > 0:
            popup_menu.show_all()
            popup_menu.connect("selection-done", self.kill_menu)
            popup_menu.popup(None, None, None, event_button, event_time)

    def fill_menu(self, menu, on_expose, only_show_applicable):
        self.main_menu.fill_menu(menu, self.on_activate, on_expose, self.accel_group, only_show_applicable)

    def kill_menu(self, widget):
        widget.destroy()

    def on_activate(self, widget, action):
        if self.all_menu_items_sensitive:
            if not action.analyze_selection(): return False
        action()

    def on_analyse(self, widget, event, action):
        if event.count == 0:
            widget.set_sensitive(action.cached_analyze_selection())
            # Only change label if needed, or else you'll get an infinite stream of expose events
            if widget.get_child().get_label() != action.menu_info.get_label():
                widget.get_child().set_label(action.menu_info.get_label())
            self.all_menu_items_sensitive = False

    def set_all_menu_items_sensitive(self, accel_group, acceleratable, accel_key, accel_mods):
        def set_all_sensitive(menu):
            for menu_item in menu.get_children():
                menu_item.set_sensitive(True)
                submenu = menu_item.get_submenu()
                if submenu is not None:
                    set_all_sensitive(submenu)

        if not self.all_menu_items_sensitive:
            set_all_sensitive(self.menubar)
            self.all_menu_items_sensitive = True




