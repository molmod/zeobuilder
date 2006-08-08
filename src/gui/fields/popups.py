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
from zeobuilder.conversion import express_measure
from zeobuilder.gui.simple import ask_name

from molmod.data import periodic
from molmod.units import measures, units_by_measure
from molmod.transformations import Translation, Rotation

import gtk, numpy


__all__ = ["Base", "Default", "Measure", "Element"]


class Base(object):
    "Base class for popupmenu near each field"

    def __init__(self, field):
        self.field = field
        self.menu = gtk.Menu()

    def add_separator(self):
        if self.row_count > 0 and \
           not isinstance(self.menu.get_children()[-1], gtk.SeparatorMenuItem):
            mi = gtk.SeparatorMenuItem()
            mi.show()
            self.menu.append(mi)
            self.row_count += 1

    def create_item(self, label_text, stock_id, on_activate, *args):
        if len(label_text) > 50:
            label_text = label_text[:47] + "..."
        if stock_id is None:
            mi = gtk.MenuItem(label_text)
        else:
            mi = gtk.ImageMenuItem(stock_id)
            mi.get_child().set_label(label_text)
        if on_activate is None:
            mi.set_sensitive(False)
        else:
            mi.connect("activate", on_activate, *args)
        mi.show()
        return mi

    def add_item(self, label_text, stock_id, on_activate, *args):
        self.menu.append(self.create_item(label_text, stock_id, on_activate, *args))
        self.row_count += 1

    def attach_items(self, descriptions):
        for index, description in enumerate(descriptions):
            label_text = description[0]
            stock_id = description[1]
            on_activate = description[2]
            args = description[3:]
            mi = self.create_item(label_text, stock_id, on_activate, *args)
            self.menu.attach(mi, index, index+1, self.row_count, self.row_count+1)
        self.row_count += 1

    def do_popup(self, button, mouse_button, time):
        for child in self.menu.get_children():
            self.menu.remove(child)
        self.row_count = 0
        self.fill_menu()

        # check whether the menu ends with a separator and remove
        last = self.menu.get_children()[-1]
        if isinstance(last, gtk.SeparatorMenuItem):
            self.menu.remove(last)

        def top_right(menu):
            xo, yo = button.window.get_origin()
            return (
                xo + button.allocation.x + button.allocation.width,
                yo + button.allocation.y,
                False
            )

        self.menu.popup(None, None, top_right, mouse_button, time)

    def fill_menu(self):
        raise NotImplementedError

    def write_to_widget(self, widget, representation):
        self.field.write_to_widget(representation)


class Default(Base):
    "The default popup for a field."

    def fill_menu(self):
        from mixin import insensitive, ambiguous
        if self.field.original != insensitive:
            self.add_item(
                "Revert to '%s'" % str(self.field.original),
                gtk.STOCK_UNDO,
                self.write_to_widget,
                self.field.original,
            )
        if self.field.reset_representation is not None:
            self.add_item(
                "Reset to '%s'" % str(self.field.reset_representation),
                gtk.STOCK_REFRESH,
                self.write_to_widget,
                self.field.reset_representation
            )

        if self.field.history_name is not None:
            self.saved_representations = context.application.configuration.get_saved_representations(self.field.history_name)

            self.add_separator()
            if self.field.read_from_widget() == ambiguous:
                self.add_item(
                    "Store field",
                    gtk.STOCK_ADD,
                    None,
                )
            else:
                store_item = self.add_item(
                    "Store field",
                    gtk.STOCK_ADD,
                    self.on_store_activate,
                    self.field,
                )

            self.add_separator()
            saved_keys = self.saved_representations.keys()
            saved_keys.sort()
            for key in saved_keys:
                representation = self.saved_representations[key]
                self.add_item(
                    "%s: %s" % (key, representation),
                    None,
                    self.write_to_widget,
                    representation,
                )

            self.add_separator()
            for key in saved_keys:
                representation = self.saved_representations[key]
                self.add_item(
                    "Delete '%s'" % key,
                    gtk.STOCK_DELETE,
                    self.on_delete_activated,
                    key,
                )

            history_representations = context.application.configuration.get_history_representations(self.field.history_name)

            self.add_separator()
            for index, representation in enumerate(history_representations):
                self.add_item(
                    "HISTORY %i: %s" % (index, representation),
                    None,
                    self.write_to_widget,
                    representation,
                )

    def unused_name(self):
        template = "NO NAME %i"
        counter = 1
        while True:
            proposal = template % counter
            if proposal not in self.saved_representations:
                return proposal
            counter += 1

    def on_store_activate(self, widget, field):
        name = ask_name()
        if name is None:
            return
        name = name.upper()
        if len(name) == 0:
            name = self.unused_name()
        self.saved_representations[name] = field.read_from_widget()

    def on_delete_activated(self, widget, key):
        del self.saved_representations[key]
        self.menu.popdown()


class Measure(Default):
    "A popup that can also convert to other units"

    def fill_menu(self):
        Default.fill_menu(self)
        representation = self.field.read_from_widget()
        from mixin import ambiguous
        if representation == ambiguous:
            return

        self.add_separator()
        try:
            value = self.field.convert_to_value(representation)
            if isinstance(value, numpy.ndarray):
                value = value.ravel()
            for unit in units_by_measure[self.field.measure]:
                if isinstance(value, numpy.ndarray):
                    alternative_representation = tuple(
                        express_measure(
                            item,
                            self.field.measure,
                            self.field.decimals,
                            self.field.scientific,
                            unit
                        )
                        for item in value
                    )
                else:
                    alternative_representation = express_measure(
                        value,
                        self.field.measure,
                        self.field.decimals,
                        self.field.scientific,
                        unit
                    )
                self.add_item(
                    "Convert to '%s'" % str(alternative_representation),
                    None,
                    self.write_to_widget,
                    alternative_representation
                )
        except ValueError:
            self.add_item(
                "Convert to ... (invalid entries)",
                None,
                None,
            )


class Element(Base):
    def fill_menu(self):
        Base.fill_menu(self)
        from mixin import ambiguous
        if self.field.original == ambiguous:
            str_original = str(self.field.original)
        else:
            str_original = moldata.periodic.symbol[self.field.original]
        self.add_item(
            "Revert to '%s'" % str_original,
            gtk.STOCK_REFRESH,
            self.write_to_widget,
            self.field.original
        )
