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


from elementary import Composed
from faulty import Float, Length, Int
from edit import CheckButton, ComboBox
from mixin import InvalidField
import popups
from zeobuilder.transformations import Translation as MathTranslation, Rotation as MathRotation

from molmod.units import suffices, measures, measure_names

import numpy

import math


__all__ = ["Vector", "Translation", "Rotation", "Box", "Color",
           "CellMatrix", "CellActive"]


class Vector(Composed):
    Popup = popups.Default

    def __init__(self, invalid_message, label_text=None, attribute=None, show_popup=True, low=None, high=None, low_inclusive=True, high_inclusive=True, scientific=False, decimals=5, length=True, vector_name="r", show_field_popups=False, table_border_width=6):
        if length: FieldClass = Length
        else: FieldClass = Float
        fields = [
            FieldClass("Invalid %s.x" % vector_name, "   %s.x" % vector_name, "?", show_field_popups, low, high, low_inclusive, high_inclusive, scientific, decimals),
            FieldClass("Invalid %s.y" % vector_name, "   %s.y" % vector_name, "?", show_field_popups, low, high, low_inclusive, high_inclusive, scientific, decimals),
            FieldClass("Invalid %s.z" % vector_name, "   %s.z" % vector_name, "?", show_field_popups, low, high, low_inclusive, high_inclusive, scientific, decimals)
        ]
        Composed.__init__(self, fields, invalid_message, label_text, attribute, show_popup, show_field_popups, table_border_width)

    def create_widgets(self):
        Composed.create_widgets(self)
        self.tabulate_widgets()

    def applicable_attribute(self, attribute):
        return len(attribute) >= 3

    def read_from_attribute(self, attribute):
        return tuple(attribute[:3])

    def write_to_attribute(self, value, attribute):
        for index, coordinate in enumerate(value):
            attribute[index] = coordinate

class Translation(Vector):
    Popup = popups.Translation

    def __init__(self, invalid_message, label_text=None, attribute=None, show_popup=True, scientific=False, decimals=5, vector_name="t", show_field_popups=False, table_border_width=6):
        Vector.__init__(self, invalid_message, label_text, attribute, show_popup, None, None, True, True, scientific, decimals, True, vector_name, show_field_popups, table_border_width)

    def applicable_attribute(self, attribute):
        return isinstance(attribute, MathTranslation) and Vector.applicable_attribute(self, attribute.translation_vector)

    def read_from_attribute(self, attribute):
        return Vector.read_from_attribute(self, attribute.translation_vector)

    def write_to_attribute(self, value, attribute):
        Vector.write_to_attribute(self, value, attribute.translation_vector)


class Rotation(Composed):
    Popup = popups.Rotation

    def __init__(self, invalid_message, label_text=None, attribute=None, show_popup=True, decimals=5, scientific=False, axis_name="n", show_field_popups=False, table_border_width=6):
        fields = [
            Float("Invalid component for the x-axis rotation.", "   " + axis_name + ".x", "?", show_popup=show_field_popups, decimals=decimals, scientific=scientific),
            Float("Invalid component for the y-axis rotation.", "   " + axis_name + ".y", "?", show_popup=show_field_popups, decimals=decimals, scientific=scientific),
            Float("Invalid component for the z-axis rotation.", "   " + axis_name + ".z", "?", show_popup=show_field_popups, decimals=decimals, scientific=scientific),
            Float("Invalid rotation angle.", "   angle", "?", show_popup=show_field_popups),
            CheckButton("Inversion", "?", show_popup=show_field_popups)
        ]
        Composed.__init__(self, fields, invalid_message, label_text, attribute, show_popup, show_field_popups, table_border_width)

    def create_widgets(self):
        Composed.create_widgets(self)
        self.tabulate_widgets()

    def applicable_attribute(self, attribute):
        return isinstance(attribute, MathRotation)

    def read_from_attribute(self, attribute):
        temp = attribute.get_rotation_properties()
        return (temp[1][0], temp[1][1], temp[1][2], temp[0], temp[2])

    def write_to_attribute(self, value, attribute):
        rotation_axis = numpy.array([float(value[0]), float(value[1]), float(value[2])])
        rotation_angle = float(value[3])
        invert = value[4]
        attribute.set_rotation_properties(rotation_angle, rotation_axis, invert)

    def node_applicable(self, node):
        if not Edit.node_applicable(self, node): return False
        if self.attribute == None:
            Class = node.__class__
        else:
            Class = eval("node." + self.attribute).__class__
        return issubclass(Class, Rotation)


class Box(Vector):
    Popup = popups.Default

    def __init__(self, invalid_message, label_text=None, attribute=None, show_popup=True, scientific=False, decimals=5, show_field_popups=False, table_border_width=6):
        Vector.__init__(self, invalid_message, label_text, attribute, show_popup, None, None, True, True, scientific, decimals, True, "box", show_field_popups, table_border_width)


class Color(Vector):
    Popup = popups.Default

    def __init__(self, invalid_message, label_text=None, attribute=None, show_popup=True, decimals=5, show_field_popups=False, table_border_width=6):
        Vector.__init__(self, invalid_message, label_text, attribute, show_popup, 0.0, 1.0, True, True, False, decimals, False, "color", show_field_popups, table_border_width)


class CellMatrix(Composed):
    Popup = popups.Default

    def __init__(self, invalid_message, label_text=None, attribute=None, show_popup=True, scientific=False, decimals=5, show_field_popups=False, table_border_width=6):
        fields = [
            Vector("A component of ridge A has a wrong syntax.", "Ridge A", "?", show_popup, None, None, True, True, scientific, decimals, True, "A", show_field_popups, table_border_width),
            Vector("A component of ridge B has a wrong syntax.", "Ridge B", "?", show_popup, None, None, True, True, scientific, decimals, True, "B", show_field_popups, table_border_width),
            Vector("A component of ridge C has a wrong syntax.", "Ridge C", "?", show_popup, None, None, True, True, scientific, decimals, True, "C", show_field_popups, table_border_width)
        ]
        Composed.__init__(self, fields, invalid_message, label_text, attribute, show_popup, show_field_popups, table_border_width, False)

    def create_widgets(self):
        Composed.create_widgets(self)
        self.tabulate_widgets()

    def applicable_attribute(self, attribute):
        return attribute.shape == (3,3)

    def read_from_attribute(self, attribute):
        return tuple(numpy.transpose(attribute))

    def write_to_attribute(self, value, attribute):
        for index, coordinate in enumerate(value):
            attribute[:,index] = coordinate

    def check(self):
        Composed.check(self)
        if self.get_active() and self.changed():
            matrix = numpy.zeros((3, 3), float)
            self.write_to_attribute(
                self.convert_to_value(self.read_from_widget()),
                matrix
            )
            for col, name in enumerate(["A", "B", "C"]):
                norm = math.sqrt(numpy.dot(matrix[:,col], matrix[:,col]))
                if norm < 1e-6:
                    invalid_field = InvalidField(self, "The length of ridge %s is (nearly) zero." % name)
                    invalid_field.prepend_message(self.invalid_message)
                    raise invalid_field
                matrix[:,col] /= norm
            if abs(numpy.linalg.det(matrix)) < 1e-6:
                invalid_field = InvalidField(self, "The ridges of the unit cell are (nearly) linearly dependent vectors!")
                invalid_field.prepend_message(self.invalid_message)
                raise invalid_field


class CellActive(Composed):
    Popup = popups.Default

    def __init__(self, invalid_message, label_text=None, attribute=None, show_popup=True, show_field_popups=False, table_border_width=6):
        fields = [
            CheckButton("Active in A direction", "?", show_field_popups),
            CheckButton("Active in B direction", "?", show_field_popups),
            CheckButton("Active in C direction", "?", show_field_popups)
        ]
        Composed.__init__(self, fields, invalid_message, label_text, attribute, show_popup, show_field_popups, table_border_width)

    def create_widgets(self):
        Composed.create_widgets(self)
        self.tabulate_widgets()

    def applicable_attribute(self, attribute):
        return len(attribute) == 3

    def read_from_attribute(self, attribute):
        return tuple(attribute)

    def write_to_attribute(self, value, attribute):
        for index, coordinate in enumerate(value):
            attribute[index] = coordinate


class Repetitions(Composed):
    Popup = popups.Default

    def __init__(self, invalid_message, label_text=None, attribute=None, show_popup=True, show_field_popups=False, table_border_width=6):
        fields = [
            Int("Please enter a vilad repetition value along A.", "A", "?", show_field_popups, minimum=1),
            Int("Please enter a vilad repetition value along B.", "B", "?", show_field_popups, minimum=1),
            Int("Please enter a vilad repetition value along C.", "C", "?", show_field_popups, minimum=1)
        ]
        Composed.__init__(self, fields, invalid_message, label_text, attribute, show_popup, show_field_popups, table_border_width)

    def create_widgets(self):
        Composed.create_widgets(self)
        self.tabulate_widgets()

    def applicable_attribute(self, attribute):
        return len(attribute) == 3

    def read_from_attribute(self, attribute):
        return tuple(attribute)

    def write_to_attribute(self, value, attribute):
        for index, coordinate in enumerate(value):
            attribute[index] = coordinate


class Units(Composed):
    Popup = popups.Translation

    def __init__(self, label_text=None, attribute=None, show_popup=True, show_field_popups=False, table_border_width=6):
        fields = [
            ComboBox(
                [(UNIT, suffices[UNIT]) for UNIT in measures[measure]],
                measure_name,
                "?",
                show_popup=show_field_popups
            ) for measure, measure_name
            in measure_names.iteritems()
        ]
        Composed.__init__(
            self, fields, "", label_text, attribute, show_popup,
            show_field_popups, table_border_width
        )

    def create_widgets(self):
        Composed.create_widgets(self)
        self.tabulate_widgets()

    def applicable_attribute(self, attribute):
        if not isinstance(attribute, dict): return False
        if not len(attribute) == len(measures): return False
        for measure in attribute:
            if not measure in measures: return False
        return True

    def read_from_attribute(self, attribute):
        return tuple([attribute[measure] for measure in measure_names])

    def write_to_attribute(self, value, attribute):
        for index, measure in enumerate(measure_names):
            attribute[measure] = value[index]

