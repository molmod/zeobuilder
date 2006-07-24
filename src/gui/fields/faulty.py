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

from elementary import Faulty
from zeobuilder.conversion import express_measure, eval_measure
from molmod.units import LENGTH
import popups

import gtk

__all__ = ["Entry", "Float", "Int", "Length", "Name", "Password"]


class Entry(Faulty):
    Popup = popups.Default
    self_containing = False

    def create_widgets(self):
        Faulty.create_widgets(self)
        self.entry = gtk.Entry()
        self.entry.connect("changed", self.on_widget_changed)
        self.entry.set_activates_default(True)
        self.container = self.entry

    def destroy_widgets(self):
        self.entry = None
        Faulty.destroy_widgets(self)

    def read_from_widget(self):
        representation = self.entry.get_text()
        if representation == "":
            return None
        else:
            return representation

    def write_to_widget(self, representation, original=False):
        if representation == None: representation = ""
        self.entry.set_text(representation)
        Faulty.write_to_widget(self, representation, original)


class Float(Entry):
    Popup = popups.Default

    def __init__(self, invalid_message, label_text=None, attribute=None, show_popup=True, low=None, high=None, low_inclusive=True, high_inclusive=True, scientific=False, decimals=5):
        Entry.__init__(self, invalid_message, label_text, attribute, show_popup)
        self.low = low
        self.high = high
        self.low_inclusive = low_inclusive
        self.high_inclusive = high_inclusive
        self.scientific = scientific
        self.decimals = decimals

    def convert_to_representation(self, value):
        return ("%.*" + {True: "E", False: "F"}[self.scientific]) % (self.decimals, value)

    def check_ranges(self, value, name):
        if (self.low != None):
            if self.low_inclusive and value < self.low:
                raise ValueError, "Value out of range. The value you entered (%s) violates %s >= %s." % (self.convert_to_representation(value), name, self.convert_to_representation(self.low))
            if not self.low_inclusive and value <= self.low:
                raise ValueError, "Value out of range. The value you entered (%s) violates %s > %s." % (self.convert_to_representation(value), name, self.convert_to_representation(self.low))
        if (self.high != None):
            if self.high_inclusive and value > self.high:
                raise ValueError, "Value out of range. The value you entered (%s) violates %s <= %s." % (self.convert_to_representation(value), name, self.convert_to_representation(self.high))
            if not self.high_inclusive and value >= self.high:
                raise ValueError, "Value out of range. The value you entered (%s) violates %s < %s." % (self.convert_to_representation(value), name, self.convert_to_representation(self.high))

    def convert_to_value(self, representation):
        value = float(representation)
        self.check_ranges(value, "float")
        return value


class Int(Entry):
    Popup = popups.Default

    def __init__(self, invalid_message, label_text=None, attribute=None, show_popup=True, minimum=None, maximum=None):
        Entry.__init__(self, invalid_message, label_text, attribute, show_popup)
        self.minimum = minimum
        self.maximum = maximum

    def convert_to_representation(self, value):
        return str(value)

    def convert_to_value(self, representation):
        value = int(representation)
        if self.minimum != None and value < self.minimum:
            raise ValueError, "Value too low. (int >= %i)" % self.minimum
        if self.maximum != None and value > self.maximum:
            raise ValueError, "Value too high. (int <= %i)" % self.maximum
        return value


class Length(Float):
    Popup = popups.Length

    def convert_to_representation(self, value):
        return express_measure(value, LENGTH, self.decimals, self.scientific)

    def convert_to_value(self, representation):
        value = eval_measure(representation, measure=LENGTH)
        self.check_ranges(value, "length")
        return value


class Name(Entry):
    Popup = popups.Default

    def convert_to_value(self, representation):
        representation.strip()
        if representation == "":
            raise ValueError, "A name must contain non white space characters."
        return representation


class Password(Entry):
    def create_widgets(self):
        Entry.create_widgets(self)
        self.entry.set_property("visibility", False)

