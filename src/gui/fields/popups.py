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

from zeobuilder.transformations import Translation, Rotation
from molmod.data import periodic
from zeobuilder.conversion import express_measure
from molmod.units import suffices, LENGTH, measures

import gtk

__all__ = ["Base", "Default", "Length", "Translation", "Rotation", "Element"]



class Base(object):
    "Base class for popupmenu near each field"
    def __init__(self, field, parent_window):
        self.menu = gtk.Menu()
        self.field = field
        self.parent_window = parent_window

    def add_separator(self):
        mi = gtk.SeparatorMenuItem()
        mi.show()
        self.menu.append(mi)

    def add_item(self, label, on_activate, *args):
        "Adds a new menuitem with the corresponding event_handler"
        mi = gtk.MenuItem(label)
        if on_activate is None:
            mi.set_sensitive(False)
        else:
            mi.connect("activate", on_activate, *args)
        mi.show()
        self.menu.append(mi)

    def popup(self, button, time):
        if len(self.menu.get_children()) > 0:
            self.menu.popup(None, None, None, button, time)

    def write_to_widget(self, widget, representation):
        self.field.write_to_widget(representation)

class Default(Base):
    "The default popup for a field, only has a revert function"
    def __init__(self, field, parent_window):
        Base.__init__(self, field, parent_window)
        from mixin import insensitive
        if field.original != insensitive:
            self.add_item("Revert to %s" % str(field.original), self.write_to_widget, field.original)


class Length(Default):
    "A popup that can convert lengths to other unit systems"
    def __init__(self, field, parent_window):
        Default.__init__(self, field, parent_window)
        representation = self.field.read_from_widget()
        if representation == ambiguous: return
        self.add_separator()
        try:
            length = self.field.convert_to_value(representation)
            for UNIT in measures[LENGTH]:
                unit_suffix = suffices[UNIT]
                alternative_representation = express_measure(length, measure=LENGTH, unit=UNIT)
                self.add_item("Convert to %s (%f)" % (unit_suffix, alternative_representation), self.write_to_widget, alternative_representation)
        except ValueError:
            self.add_item("Convert to ... (invalid entries)", None)


class Translation(Default):
    def __init__(self, field, parent_window):
        Default.__init__(self, field, parent_window)
        self.add_item("Reset", self.write_to_widget, ('0.0', '0.0', '0.0'))
        representation = self.field.read_from_widget()
        if representation == ambiguous: return


class Rotation(Default):
    def __init__(self, field, parent_window):
        Default.__init__(self, field, parent_window)
        self.add_item("Reset", self.write_to_widget, ('0.0', '0.0', '1.0', '0.0', False))
        representation = self.field.read_from_widget()
        if representation == ambiguous: return


class Element(Base):
    def __init__(self, field, parent_window):
        Base.__init__(self, field, parent_window)
        if field.original == ambiguous:
            str_original = str(field.original)
        else:
            str_original = moldata.periodic.symbol[field.original]
        self.add_item("Revert to %s" % str_original, self.write_to_widget, field.original)
