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


from elementary import ComposedInTable
from faulty import Float, Length, Int, MeasureEntry
from edit import CheckButton, ComboBox
from mixin import InvalidField, EditMixin, FaultyMixin
import popups
from zeobuilder.transformations import Translation as MathTranslation, Rotation as MathRotation

from molmod.units import suffices, measures, measure_names, units_by_measure, ANGLE
from molmod.unit_cell import check_cell

import numpy, gtk

import math, sys


__all__ = [
    "ComposedArray", "Translation", "Rotation", "CellMatrix", "CellActive",
    "Repetitions", "Units"
]


class ComposedArrayError(Exception):
    pass


class ComposedArray(ComposedInTable):
    def __init__(self, FieldClass, array_name, suffices, label_text=None, attribute_name=None, show_popup=True, history_name=None, show_field_popups=False, short=True, one_row=False, **keyval):
        suffices = numpy.array(suffices)
        self.shape = suffices.shape

        if len(self.shape) == 2:
            cols = self.shape[1]
            fields = sum([[
                FieldClass(
                    label_text=(array_name % suffix),
                    **keyval
                ) for suffix in row
            ] for row in suffices], [])
        elif len(self.shape) == 1:
            if one_row:
                cols = self.shape[0]
            else:
                cols = 1
            fields = [FieldClass(
                label_text=(array_name % suffix),
                **keyval
            ) for suffix in suffices]
        else:
            raise ComposedArrayError("the suffices must be given as one- or two-dimensional iterable objects. (shape=%s)" % len(suffices.shape))


        if issubclass(FieldClass, Float):
            self.decimals = fields[0].decimals
            self.scientific = fields[0].scientific

        if issubclass(FieldClass, MeasureEntry):
            self.measure = fields[0].measure

        self.Popup = fields[0].Popup

        ComposedInTable.__init__(
            self,
            fields=fields,
            label_text=label_text,
            attribute_name=attribute_name,
            show_popup=show_popup,
            history_name=history_name,
            show_field_popups=show_field_popups,
            short=short,
            cols=cols,
        )

    def applicable_attribute(self):
        return isinstance(self.attribute, numpy.ndarray) and self.attribute.shape == self.shape

    def convert_to_representation(self, value):
        intermediate = tuple(value.ravel())
        return ComposedInTable.convert_to_representation(self, intermediate)

    def convert_to_value(self, representation):
        intermediate = ComposedInTable.convert_to_value(self, representation)
        result = numpy.array(intermediate)
        result.shape = self.shape
        return result


class Translation(ComposedArray):
    reset_representation = ('0.0', '0.0', '0.0')

    def __init__(self, label_text=None, attribute_name=None, show_popup=True, history_name=None, show_field_popups=False, scientific=False, decimals=2, vector_name="t.%s"):
        ComposedArray.__init__(
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


class Rotation(ComposedInTable):
    Popup = popups.Default
    reset_representation = ('0.0', ('1.0', '0.0', '0.0'), False)

    def __init__(self, label_text=None, attribute_name=None, show_popup=True, history_name=None, show_field_popups=False, decimals=2, scientific=False, axis_name="n.%s"):
        fields = [
            MeasureEntry(
                measure=ANGLE,
                label_text="Angle",
                decimals=decimals,
                scientific=scientific,
            ), ComposedArray(
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
        ComposedInTable.__init__(
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
        self.attribute.set_rotation_properties(*value)


class CellMatrix(ComposedArray):
    reset_representation = (('10.0 A', '0.0 A', '0.0 A', '0.0 A', '10.0 A', '0.0 A', '0.0 A', '0.0 A', '10.0 A'))

    def __init__(self, label_text=None, attribute_name=None, show_popup=True, history_name=None, show_field_popups=False, scientific=False, decimals=2):
        ComposedArray.__init__(
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
        intermediate = ComposedArray.convert_to_value(self, representation)
        check_cell(intermediate)
        return intermediate


class CellActive(ComposedArray):
    def __init__(self, label_text=None, attribute_name=None, show_popup=True, history_name=None, show_field_popups=False):
        ComposedArray.__init__(
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


class Repetitions(ComposedArray):
    def __init__(self, label_text=None, attribute_name=None, show_popup=True, history_name=None, show_field_popups=False):
        ComposedArray.__init__(
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


class Units(ComposedInTable):
    Popup = popups.Default

    def __init__(self, label_text=None, attribute_name=None, show_popup=True, show_field_popups=False):
        fields = [
            ComboBox(
                choices=[(unit, suffices[unit]) for unit in units_by_measure[measure]],
                label_text=measure_names[measure],
            ) for measure
            in measures
        ]
        ComposedInTable.__init__(
            self,
            fields=fields,
            label_text=label_text,
            attribute_name=attribute_name,
            show_popup=show_popup,
            show_field_popups=show_field_popups,
            cols=3,
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

