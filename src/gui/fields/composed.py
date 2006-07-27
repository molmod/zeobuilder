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


from elementary import Composed, TabulateComposed
from faulty import Float, Length, Int, MeasureEntry
from edit import CheckButton, ComboBox
from mixin import InvalidField, EditMixin, FaultyMixin
import popups
from zeobuilder.transformations import Translation as MathTranslation, Rotation as MathRotation

from molmod.units import suffices, measures, measure_names, units_by_measure, ANGLE

import numpy, gtk

import math


__all__ = [
    "Array", "Translation", "Rotation", "CellMatrix", "CellActive",
    "Repetitions", "Units"
]


class ArrayError(Exception):
    pass


class Array(TabulateComposed):
    def __init__(self, FieldClass, array_name, suffices, label_text=None, attribute_name=None, show_popup=True, history_name=None, show_field_popups=False, short=True, transpose=False, **keyval):
        # make sure that the suffices are given as a numpy array.
        suffices = numpy.array(suffices)
        if len(suffices.shape) != 1 and len(suffices.shape) != 2:
            raise ArrayError("the suffices must be given as one- or two-dimensional iterable objects. (shape=%s)" % len(suffices.shape))
        self.shape = suffices.shape
        if len(suffices.shape) == 1:
            self.suffices = numpy.array([suffices]).transpose()
        else:
            self.suffices = suffices

        self.short = short

        self.transpose = transpose
        if transpose:
            self.suffices = self.suffices.transpose()

        self.high_widget = (self.suffices.shape[0] != 1)


        self.fields_array = numpy.array([
            [
                FieldClass(
                    label_text=(array_name % suffix),
                    **keyval
                ) for suffix in row
            ] for row in self.suffices
        ])

        fields = self.fields_array.ravel().tolist()

        if issubclass(FieldClass, EditMixin):
            for field in fields:
                field.show_popup = show_field_popups

        if issubclass(FieldClass, Float):
            self.decimals = fields[0].decimals
            self.scientific = fields[0].scientific

        if issubclass(FieldClass, MeasureEntry):
            self.measure = fields[0].measure

        self.Popup = fields[0].Popup

        Composed.__init__(
            self,
            fields=fields,
            label_text=label_text,
            attribute_name=attribute_name,
            show_popup=show_popup,
            history_name=history_name,
            show_field_popups=show_field_popups
        )

    def applicable_attribute(self):
        return isinstance(self.attribute, numpy.ndarray) and self.attribute.shape == self.shape

    def convert_to_representation(self, value):
        if self.transpose:
            intermediate = tuple(value.transpose().ravel())
        else:
            intermediate = tuple(value.ravel())
        return Composed.convert_to_representation(self, intermediate)

    def convert_to_value(self, representation):
        intermediate = Composed.convert_to_value(self, representation)
        if self.transpose:
            result = numpy.array(intermediate)
            if len(self.shape) == 1:
                result.shape = self.shape
            else:
                result.shape = (self.shape[0], self.shape[1])
                result = result.transpose()
        else:
            result = numpy.array(intermediate)
            result.shape = self.shape
        return result

    def create_widgets(self):
        Composed.create_widgets(self)
        table = gtk.Table(self.suffices.shape[0], self.suffices.shape[1]*4 - 1)
        table.set_row_spacings(6)
        table.set_col_spacings(6)
        for row_index, row in enumerate(self.fields_array):
            for col_index, field in enumerate(row):
                if field.high_widget:
                    if self.short:
                        container = field.get_widgets_short_container()
                    else:
                        container = field.get_widgets_flat_container()
                    container.set_border_width(0)
                    table.attach(
                        container,
                        col_index * 4, col_index * 4 + 3,
                        row_index, row_index+1,
                        xoptions=gtk.EXPAND|gtk.FILL, yoptions=0,
                    )
                else:
                    label, data_widget, bu_popup = field.get_widgets_separate()
                    container_left = col_index * 4
                    container_right = container_left + 3
                    if label is not None:
                        table.attach(
                            label,
                            container_left, container_left + 1,
                            row_index, row_index + 1,
                            xoptions=gtk.FILL, yoptions=0,
                        )
                        container_left += 1
                    if bu_popup is not None:
                        table.attach(
                            bu_popup,
                            container_right - 1, container_right,
                            row_index, row_index + 1,
                            xoptions=0, yoptions=0,
                        )
                        container_right -= 1
                    table.attach(
                        data_widget,
                        container_left, container_right,
                        row_index, row_index + 1,
                        xoptions=gtk.EXPAND|gtk.FILL, yoptions=0,
                    )
                if col_index > 0:
                    stub = gtk.Label()
                    stub.set_size_request(6, 1)
                    table.attach(
                        stub,
                        col_index * 4 - 1, col_index * 4,
                        row_index, row_index + 1,
                        xoptions=0, yoptions=0,
                    )

        self.data_widget = table


class Translation(Array):
    Popup = popups.Default
    reset_representation = ('0.0', '0.0', '0.0')

    def __init__(self, label_text=None, attribute_name=None, show_popup=True, history_name=None, show_field_popups=False, scientific=False, decimals=5, vector_name="t.%s"):
        Array.__init__(
            self,
            FieldClass=Length,
            array_name=vector_name,
            suffices=["x", "y", "z"],
            label_text=label_text,
            attribute_name=attribute_name,
            show_popup=show_popup,
            history_name=history_name,
            show_field_popups=show_field_popups,
            scientific=scientific,
            decimals=decimals,
        )

    def applicable_attribute(self):
        return isinstance(self.attribute, MathTranslation)

    def read_from_attribute(self):
        return self.attribute.translation_vector

    def write_to_attribute(self, value):
        self.attribute.translation_vector = value


class Rotation(TabulateComposed):
    Popup = popups.Default
    reset_representation = ('0.0', ('1.0', '0.0', '0.0'), False)

    def __init__(self, label_text=None, attribute_name=None, show_popup=True, history_name=None, show_field_popups=False, decimals=5, scientific=False, axis_name="n.%s"):
        fields = [
            MeasureEntry(
                measure=ANGLE,
                label_text="Angle",
                decimals=decimals,
                scientific=scientific,
            ), Array(
                FieldClass=Float,
                array_name=axis_name,
                suffices=["x", "y", "z"],
                show_popup=False,
                decimals=decimals,
                scientific=scientific,
            ), CheckButton(
                label_text="Inversion",
            )
        ]
        TabulateComposed.__init__(
            self,
            fields=fields,
            label_text=label_text,
            attribute_name=attribute_name,
            show_popup=show_popup,
            history_name=history_name,
            show_field_popups=show_field_popups
        )

    def applicable_attribute(self):
        return isinstance(self.attribute, MathRotation)

    def read_from_attribute(self):
        return self.attribute.get_rotation_properties()

    def write_to_attribute(self, value):
        self.attribute.set_rotation_properties(value[0], value[1], value[2])


class CellMatrix(Array):
    Popup = popups.Default
    reset_representation = (('10.0 A', '0.0 A', '0.0 A', '0.0 A', '10.0 A', '0.0 A', '0.0 A', '0.0 A', '10.0 A'))

    def __init__(self, label_text=None, attribute_name=None, show_popup=True, history_name=None, show_field_popups=False, scientific=False, decimals=5):
        Array.__init__(
            self,
            FieldClass=Length,
            array_name="%s",
            suffices=[["A.x", "B.x", "C.x"], ["A.y", "B.y", "C.y"], ["A.z", "B.z", "C.z"]],
            label_text=label_text,
            attribute_name=attribute_name,
            show_popup=show_popup,
            history_name=history_name,
            show_field_popups=show_field_popups,
            scientific=scientific,
            decimals=decimals,
        )

    def convert_to_value(self, representation):
        intermediate = Array.convert_to_value(self, representation)
        for col, name in enumerate(["A", "B", "C"]):
            norm = math.sqrt(numpy.dot(intermediate[:,col], intermediate[:,col]))
            if norm < 1e-6:
                raise ValueError("The length of ridge %s is (nearly) zero." % name)
            intermediate[:,col] /= norm
        if abs(numpy.linalg.det(intermediate)) < 1e-6:
            raise ValueError("The ridges of the unit cell are (nearly) linearly dependent vectors.")
        return intermediate


class CellActive(Array):
    Popup = popups.Default

    def __init__(self, label_text=None, attribute_name=None, show_popup=True, history_name=None, show_field_popups=False):
        Array.__init__(
            self,
            FieldClass=CheckButton,
            array_name="Active in %s direction",
            suffices=("A", "B", "C"),
            label_text=label_text,
            attribute_name=attribute_name,
            show_popup=show_popup,
            history_name=history_name,
            show_field_popups=show_field_popups,
        )


class Repetitions(Array):
    Popup = popups.Default

    def __init__(self, label_text=None, attribute_name=None, show_popup=True, history_name=None, show_field_popups=False):
        Array.__init__(
            self,
            FieldClass=Int,
            array_name="repetitions along %s",
            suffices=("A", "B", "C"),
            label_text=label_text,
            attribute_name=attribute_name,
            show_popup=show_popup,
            history_name=history_name,
            show_field_popups=show_field_popups,
            minimum=1,
        )


class Units(TabulateComposed):
    Popup = popups.Translation

    def __init__(self, label_text=None, attribute_name=None, show_popup=True, show_field_popups=False):
        fields = [
            ComboBox(
                choices=[(unit, suffices[unit]) for unit in units_by_measure[measure]],
                label_text=measure_names[measure],
            ) for measure
            in measures
        ]
        TabulateComposed.__init__(
            self,
            fields,
            label_text=label_text,
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

