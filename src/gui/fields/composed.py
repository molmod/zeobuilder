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


from elementary import TabulateComposed
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


class Vector(TabulateComposed):
    Popup = popups.Default

    def __init__(self, label_text=None, border_width=6, attribute_name=None, show_popup=True, history_name=None, invalid_message=None, show_field_popups=False, low=None, high=None, low_inclusive=True, high_inclusive=True, scientific=False, decimals=5, length=True, vector_name="r"):
        if length: FieldClass = Length
        else: FieldClass = Float
        fields = [
            FieldClass(
                label_text="%s.%s" % (vector_name, suffix),
                invalid_message="Invalid %s.%s" % (vector_name, suffix),
                low=low,
                high=high,
                low_inclusive=low_inclusive,
                high_inclusive=high_inclusive,
                scientific=scientific,
                decimals=decimals
            ) for suffix in ["x", "y", "z"]
        ]
        TabulateComposed.__init__(
            self,
            fields,
            label_text=label_text,
            border_width=border_width,
            attribute_name=attribute_name,
            show_popup=show_popup,
            history_name=history_name,
            invalid_message=invalid_message,
            show_field_popups=show_field_popups
        )

    def applicable_attribute(self):
        return isinstance(self.attribute, numpy.ndarray) and self.attribute.shape == (3,)

    def read_from_attribute(self):
        return tuple(self.attribute)

    def write_to_attribute(self, value):
        self.attribute = numpy.array(value)


class Translation(Vector):
    Popup = popups.Translation

    def __init__(self, label_text=None, border_width=6, attribute_name=None, show_popup=True, history_name=None, invalid_message=None, show_field_popups=False, scientific=False, decimals=5, vector_name="t"):
        Vector.__init__(
            self,
            label_text=label_text,
            border_width=border_width,
            attribute_name=attribute_name,
            show_popup=show_popup,
            history_name=history_name,
            invalid_message=invalid_message,
            show_field_popups=show_field_popups,
            scientific=scientific,
            decimals=decimals,
            length=True,
            vector_name=vector_name
        )

    def applicable_attribute(self):
        return isinstance(self.attribute, MathTranslation)

    def read_from_attribute(self):
        return tuple(self.attribute.translation_vector)

    def write_to_attribute(self, value):
        self.attribute.translation_vector = numpy.array(value)


class Rotation(TabulateComposed):
    Popup = popups.Rotation

    def __init__(self, label_text=None, border_width=6, attribute_name=None, show_popup=True, history_name=None, invalid_message=None, show_field_popups=False, decimals=5, scientific=False, axis_name="n"):
        fields = [
            Float(
                label_text="%s.%s" % (axis_name, suffix),
                invalid_message="Invalid component for the %s-axis rotation." % suffix,
                decimals=decimals,
                scientific=scientific,
            ) for suffix in ["x", "y", "z"]
        ] + [
            Float(
                label_text="Angle",
                invalid_message="Invalid rotation angle.",
            ), CheckButton(
                label_text="Inversion",
            )
        ]
        TabulateComposed.__init__(
            self,
            fields,
            label_text=label_text,
            border_width=border_width,
            attribute_name=attribute_name,
            show_popup=show_popup,
            history_name=history_name,
            invalid_message=invalid_message,
            show_field_popups=show_field_popups
        )

    def applicable_attribute(self):
        return isinstance(self.attribute, MathRotation)

    def read_from_attribute(self):
        temp = self.attribute.get_rotation_properties()
        return (temp[1][0], temp[1][1], temp[1][2], temp[0], temp[2])

    def write_to_attribute(self, value):
        rotation_axis = numpy.array([float(value[0]), float(value[1]), float(value[2])])
        rotation_angle = float(value[3])
        invert = value[4]
        self.attribute.set_rotation_properties(rotation_angle, rotation_axis, invert)


class BoxSize(Vector):
    Popup = popups.Default

    def __init__(self, label_text=None, border_width=6, attribute_name=None, show_popup=True, history_name=None, invalid_message=None, show_field_popups=False, scientific=False, decimals=5):
        Vector.__init__(
            self,
            label_text=label_text,
            border_width=border_width,
            attribute_name=attribute_name,
            show_popup=show_popup,
            history_name=history_name,
            invalid_message=invalid_message,
            show_field_popups=show_field_popups,
            scientific=scientific,
            decimals=decimals,
            length=True,
            vector_name="size",
        )


class Color(Vector):
    Popup = popups.Default

    def __init__(self, label_text=None, border_width=6, attribute_name=None, show_popup=True, history_name=None, invalid_message=None, show_field_popups=False, decimals=5):
        Vector.__init__(
            self,
            label_text=label_text,
            border_width=border_width,
            attribute_name=attribute_name,
            show_popup=show_popup,
            history_name=history_name,
            invalid_message=invalid_message,
            show_field_popups=show_field_popups,
            low=0.0,
            high=1.0,
            scientific=False,
            decimals=decimals,
            length=False,
            vector_name="color"
        )


class BoxRegion(TabulateComposed):
    Popup = popups.Default

    def __init__(self, label_text=None, border_width=6, attribute_name=None, show_popup=True, history_name=None, invalid_message=None, show_field_popups=False, low=None, high=None, low_inclusive=True, high_inclusive=True, scientific=False, decimals=5, length=True):
        fields = [
            Vector(
                border_width=border_width,
                low=low,
                high=high,
                low_inclusive=low_inclusive,
                high_inclusive=high_inclusive,
                scientific=scientific,
                decimals=decimals,
                length=length,
                name=name,
            )
            for name in ["low", "high"]
        ]
        TabulateComposed.__init__(
            self,
            fields,
            label_text=label_text,
            border_width=border_width,
            attribute_name=attribute_name,
            show_popup=show_popup,
            history_name=history_name,
            invalid_message=invalid_message,
            show_field_popups=show_field_popups,
            vertical=False,
        )

    def applicable_attribute(self):
        return isinstance(self.attribute, numpy.ndarray) and self.attribute.shape == (2,3)

    def read_from_attribute(self):
        return tuple(self.attribute)

    def write_to_attribute(self, value):
        self.attribute = numpy.array(value)


class Interval(TabulateComposed):
    Popup = popups.Default

    def __init__(self, label_text=None, border_width=6, attribute_name=None, show_popup=True, history_name=None, invalid_message=None, show_field_popups=False, low=None, high=None, low_inclusive=True, high_inclusive=True, scientific=False, decimals=5, length=True, interval_name="x"):
        if length: FieldClass = Length
        else: FieldClass = Float
        fields = [
            FieldClass(
                label_text="%s.%s" % (interval_name, suffix),
                border_width=border_width,
                invalid_message="Invalid %s.%s" % (interval_name, suffix),
                low=low,
                high=high,
                low_inclusive=low_inclusive,
                high_inclusive=high_inclusive,
                scientific=scientific,
                decimals=decimals,
            )
            for suffix in ["min", "max"]
        ]
        TabulateComposed.__init__(
            self,
            fields,
            label_text=label_text,
            border_width=border_width,
            attribute_name=attribute_name,
            show_popup=show_popup,
            history_name=history_name,
            invalid_message=invalid_message,
            show_field_popups=show_field_popups,
            vertical=False,
            horizontal_flat=True,
        )

    def applicable_attribute(self):
        return isinstance(self.attribute, numpy.ndarray) and self.attribute.shape == (2,)

    def read_from_attribute(self):
        return tuple(self.attribute)

    def write_to_attribute(self, value):
        self.attribute = numpy.array(value)


class CellMatrix(TabulateComposed):
    Popup = popups.Default

    def __init__(self, label_text=None, border_width=6, attribute_name=None, show_popup=True, history_name=None, invalid_message=None, show_field_popups=False, scientific=False, decimals=5):
        fields = [
            Vector(
                label_text="Ridge %s" % ridge,
                border_width=border_width,
                invalid_message="A component of ridge %s has a wrong syntax." % ridge,
                scientific=scientific,
                decimals=decimals,
                length=True,
                vector_name=ridge,
            ) for ridge in ["A", "B", "C"]
        ]
        TabulateComposed.__init__(
            self,
            fields,
            label_text=label_text,
            border_width=border_width,
            attribute_name=attribute_name,
            show_popup=show_popup,
            history_name=history_name,
            invalid_message=invalid_message,
            show_field_popups=show_field_popups,
            vertical=False,
        )

    def applicable_attribute(self):
        return isinstance(self.attribute, numpy.ndarray) and self.attribute.shape == (3,3)

    def read_from_attribute(self):
        return tuple(numpy.transpose(self.attribute))

    def write_to_attribute(self, value):
        self.attribute = numpy.array(value).transpose()

    def check(self):
        TabulateComposed.check(self)
        if self.get_active() and self.changed():
            matrix = numpy.array(self.convert_to_value_wrap(self.read_from_widget())).transpose()
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


class CellActive(TabulateComposed):
    Popup = popups.Default

    def __init__(self, label_text=None, border_width=6, attribute_name=None, show_popup=True, history_name=None, invalid_message=None, show_field_popups=False):
        fields = [
            CheckButton(
                label_text="Active in %s direction" % ridge,
            ) for ridge in ["A", "B", "C"]
        ]
        TabulateComposed.__init__(
            self,
            fields,
            label_text=label_text,
            border_width=border_width,
            attribute_name=attribute_name,
            show_popup=show_popup,
            history_name=history_name,
            invalid_message=invalid_message,
            show_field_popups=show_field_popups,
        )

    def applicable_attribute(self):
        return isinstance(self.attribute, numpy.ndarray) and self.attribute.shape == (3,)

    def read_from_attribute(self):
        return tuple(self.attribute)

    def write_to_attribute(self, value):
        self.attribute = numpy.array(value)


class Repetitions(TabulateComposed):
    Popup = popups.Default

    def __init__(self, label_text=None, border_width=6, attribute_name=None, show_popup=True, history_name=None, invalid_message=None, show_field_popups=False):
        fields = [
            Int(
                label_text=ridge,
                invalid_message="Please enter a vilad repetition value along %s." % ridge,
                minimum=1
            ) for ridge in ["A", "B", "C"]
        ]
        TabulateComposed.__init__(
            self,
            fields,
            label_text=label_text,
            border_width=border_width,
            attribute_name=attribute_name,
            show_popup=show_popup,
            history_name=history_name,
            invalid_message=invalid_message,
            show_field_popups=show_field_popups,
        )

    def applicable_attribute(self):
        return isinstance(self.attribute, numpy.ndarray) and self.attribute.shape == (3,)

    def read_from_attribute(self):
        return tuple(self.attribute)

    def write_to_attribute(self, value):
        self.attribute = numpy.array(value)


class Units(TabulateComposed):
    Popup = popups.Translation

    def __init__(self, label_text=None, attribute_name=None, show_popup=True, show_field_popups=False, border_width=6):
        fields = [
            ComboBox(
                choices=[(UNIT, suffices[UNIT]) for UNIT in measures[measure]],
                label_text=measure_name,
            ) for measure, measure_name
            in measure_names.iteritems()
        ]
        TabulateComposed.__init__(
            self,
            fields,
            label_text=label_text,
            border_width=border_width,
            attribute_name=attribute_name,
            show_popup=show_popup,
            show_field_popups=show_field_popups,
        )

    def applicable_attribute(self):
        if not isinstance(self.attribute, dict): return False
        if not len(self.attribute) == len(measures): return False
        for measure in self.attribute:
            if not measure in measures: return False
        return True

    def read_from_attribute(self):
        return tuple(self.attribute[measure] for measure in measure_names)

    def write_to_attribute(self, value):
        for index, measure in enumerate(measure_names):
            self.attribute[measure] = value[index]

