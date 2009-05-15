# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 - 2009 Toon Verstraelen <Toon.Verstraelen@UGent.be>, Center
# for Molecular Modeling (CMM), Ghent University, Ghent, Belgium; all rights
# reserved unless otherwise stated.
#
# This file is part of Zeobuilder.
#
# Zeobuilder is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# In addition to the regulations of the GNU General Public License,
# publications and communications based in parts on this program or on
# parts of this program are required to cite the following article:
#
# "ZEOBUILDER: a GUI toolkit for the construction of complex molecules on the
# nanoscale with building blocks", Toon Verstraelen, Veronique Van Speybroeck
# and Michel Waroquier, Journal of Chemical Information and Modeling, Vol. 48
# (7), 1530-1541, 2008
# DOI:10.1021/ci8000748
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


from elementary import Faulty
from mixin import ambiguous, TextViewMixin
import popups

from zeobuilder.conversion import express_measure, eval_measure

import gtk


__all__ = [
    "Entry", "Float", "Int", "MeasureEntry", "Length", "Name", "Password",
    "Filter"
]


class Entry(Faulty):
    Popup = popups.Default

    def create_widgets(self):
        Faulty.create_widgets(self)
        self.entry = gtk.Entry()
        self.entry.connect("changed", self.on_widget_changed)
        self.entry.set_activates_default(True)
        self.data_widget = self.entry

    def destroy_widgets(self):
        self.entry = None
        Faulty.destroy_widgets(self)

    def write_to_widget(self, representation, original=False):
        #print self, representation
        if representation == ambiguous: representation = ""
        self.entry.set_text(representation)
        Faulty.write_to_widget(self, representation, original)

    def read_from_widget(self):
        representation = self.entry.get_text()
        if representation == "":
            return ambiguous
        else:
            return representation

    def convert_to_value(self, representation):
        if not isinstance(representation, str):
            raise ValueError("Please enter something.")


class Float(Entry):
    Popup = popups.Default

    def __init__(self, label_text=None, attribute_name=None, show_popup=True, history_name=None, low=None, high=None, low_inclusive=True, high_inclusive=True, scientific=False, decimals=3):
        Entry.__init__(self, label_text, attribute_name, show_popup, history_name)
        self.low = low
        self.high = high
        self.low_inclusive = low_inclusive
        self.high_inclusive = high_inclusive
        self.scientific = scientific
        self.decimals = decimals

    def convert_to_representation(self, value):
        return ("%.*" + {True: "E", False: "F"}[self.scientific]) % (self.decimals, value)

    def check_ranges(self, value, name):
        if (self.low is not None):
            if self.low_inclusive and value < self.low:
                raise ValueError, "Value out of range. The value you entered (%s) violates %s >= %s." % (self.convert_to_representation(value), name, self.convert_to_representation(self.low))
            if not self.low_inclusive and value <= self.low:
                raise ValueError, "Value out of range. The value you entered (%s) violates %s > %s." % (self.convert_to_representation(value), name, self.convert_to_representation(self.low))
        if (self.high is not None):
            if self.high_inclusive and value > self.high:
                raise ValueError, "Value out of range. The value you entered (%s) violates %s <= %s." % (self.convert_to_representation(value), name, self.convert_to_representation(self.high))
            if not self.high_inclusive and value >= self.high:
                raise ValueError, "Value out of range. The value you entered (%s) violates %s < %s." % (self.convert_to_representation(value), name, self.convert_to_representation(self.high))

    def convert_to_value(self, representation):
        Entry.convert_to_value(self, representation)
        value = float(representation)
        self.check_ranges(value, "float")
        return value


class Int(Entry):
    Popup = popups.Default

    def __init__(self, label_text=None, attribute_name=None, show_popup=True, history_name=None, minimum=None, maximum=None):
        Entry.__init__(self, label_text, attribute_name, show_popup, history_name)
        self.minimum = minimum
        self.maximum = maximum

    def convert_to_representation(self, value):
        return str(value)

    def convert_to_value(self, representation):
        Entry.convert_to_value(self, representation)
        value = int(representation)
        if self.minimum is not None and value < self.minimum:
            raise ValueError, "Value too low. (int >= %i)" % self.minimum
        if self.maximum is not None and value > self.maximum:
            raise ValueError, "Value too high. (int <= %i)" % self.maximum
        return value


class MeasureEntry(Float):
    Popup = popups.Measure

    def __init__(self, measure, label_text=None, attribute_name=None, show_popup=True, history_name=None, low=None, high=None, low_inclusive=True, high_inclusive=True, scientific=False, decimals=3):
        Float.__init__(self, label_text, attribute_name, show_popup, history_name, low, high, low_inclusive, high_inclusive, scientific, decimals)
        self.measure = measure

    def convert_to_representation(self, value):
        return express_measure(value, self.measure, self.decimals, self.scientific)

    def convert_to_value(self, representation):
        Entry.convert_to_value(self, representation)
        value = eval_measure(representation, self.measure)
        self.check_ranges(value, self.measure.lower())
        return value


class Length(MeasureEntry):
    def __init__(self, label_text=None, attribute_name=None, show_popup=True, history_name=None, low=None, high=None, low_inclusive=True, high_inclusive=True, scientific=False, decimals=3):
        MeasureEntry.__init__(self, "Length", label_text, attribute_name, show_popup, history_name, low, high, low_inclusive, high_inclusive, scientific, decimals)


class Name(Entry):
    Popup = popups.Default

    def convert_to_value(self, representation):
        Entry.convert_to_value(self, representation)
        representation.strip()
        if representation == "":
            raise ValueError("A name must contain non white space characters.")
        return representation


class Password(Entry):
    def create_widgets(self):
        Entry.create_widgets(self)
        self.entry.set_property("visibility", False)


class Expression(Faulty, TextViewMixin):
    Popup = popups.Default
    high_widget = True
    reset_representation = "True"

    def __init__(self, label_text=None, attribute_name=None, show_popup=True, history_name=None, width=250, height=300):
        Faulty.__init__(self, label_text, attribute_name, show_popup, history_name)
        TextViewMixin.__init__(self, width, height)

    def create_widgets(self):
        Faulty.create_widgets(self)
        TextViewMixin.create_widgets(self)

    def destroy_widgets(self):
        TextViewMixin.destroy_widgets(self)
        Faulty.destroy_widgets(self)

    def applicable_attribute(self):
        from zeobuilder.expressions import Expression as E
        return isinstance(self.attribute, E)

    def convert_to_representation(self, value):
        return TextViewMixin.convert_to_representation(self, value.code)

    def write_to_widget(self, representation, original=False):
        TextViewMixin.write_to_widget(self, representation)
        Faulty.write_to_widget(self, representation, original)

    def convert_to_value(self, representation):
        from zeobuilder.expressions import Expression as E
        try:
            return E(TextViewMixin.convert_to_value(self, representation))
        except SyntaxError:
            raise ValueError("There is a syntax error in the expression.")

    def read_from_widget(self):
        return TextViewMixin.read_from_widget(self)


