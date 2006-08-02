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
from faulty import Float, Length, Int, MeasureEntry
from edit import CheckButton, ComboBox
from mixin import InvalidField, EditMixin, FaultyMixin, TableMixin
import popups
from zeobuilder.transformations import Translation as MathTranslation, Rotation as MathRotation

from molmod.units import measures, units_by_measure
from molmod.unit_cell import check_cell, UnitCell

import numpy, gtk

import math, sys


__all__ = [
    "ComposedInTable", "ComposedArray", "Translation", "Rotation", "CellMatrix", "CellActive",
    "Repetitions", "Units"
]


class ComposedInTable(Composed, TableMixin):
    def __init__(self, fields, label_text=None, attribute_name=None, show_popup=True, history_name=None, show_field_popups=False, short=True, cols=1):
        Composed.__init__(self, fields, label_text, attribute_name, show_popup, history_name, show_field_popups)
        TableMixin.__init__(self, short, cols)

    def create_widgets(self):
        Composed.create_widgets(self)
        TableMixin.create_widgets(self)
        

class ComposedArrayError(Exception):
    pass


class ComposedArray(ComposedInTable):
    Popup = None

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

        if self.Popup is None:
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
                measure="Angle",
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


class Parameters(object):
    pass


class CellMatrixPopup(popups.Measure):
    def fill_menu(self):
        popups.Measure.fill_menu(self)
        self.add_separator()
        try:
            cell = self.field.convert_to_value(self.field.read_from_widget())
            self.add_item("Set parameters ...", None, self.on_set_parameters, cell)
        except ValueError:
            self.add_item("Set parameters ... (invalid fields)", None, None)


    def on_set_parameters(self, menu, cell):
        from zeobuilder.gui.fields_dialogs import FieldsDialogSimple

        dialog = FieldsDialogSimple(
            "Set the cell parameters",
            CellParameters(
                attribute_name="cell",
                show_popup=False,
            ),
            ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK)),
        )

        parameters = Parameters()
        parameters.cell = cell
        if dialog.run(parameters) == gtk.RESPONSE_OK:
            self.field.write_to_widget(self.field.convert_to_representation(parameters.cell))



class CellMatrix(ComposedArray):
    Popup = CellMatrixPopup
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


class CellParameters(ComposedInTable):
    def __init__(self, label_text=None, attribute_name=None, show_popup=True, history_name=None, show_field_popups=False):
        ComposedInTable.__init__(
            self,
            fields=[
                ComposedArray(
                    FieldClass=Length,
                    array_name="%s",
                    suffices=["a", "b", "c"],
                    low=0.0,
                    low_inclusive=False,
                    scientific=False,
                    decimals=2,
                ),
                ComposedArray(
                    FieldClass=MeasureEntry,
                    array_name="%s",
                    suffices=["alpha", "beta", "gamma"],
                    measure="Angle",
                    low=0.0,
                    low_inclusive=False,
                    high=math.pi,
                    high_inclusive=False,
                    scientific=False,
                    decimals=0,
                ),
            ],
            label_text=label_text,
            attribute_name=attribute_name,
            show_popup=show_popup,
            history_name=history_name,
            show_field_popups=show_field_popups,
            cols=1,
        )

    def applicable_attribute(self):
        return isinstance(self.attribute, numpy.ndarray) and self.attribute.shape == (3,3)

    def convert_to_representation(self, value):
        unit_cell = UnitCell(value)
        self.saved_value = value
        lengths, angles = unit_cell.get_parameters()
        return ComposedInTable.convert_to_representation(self, (lengths, angles))

    def convert_to_value(self, representation):
        lengths, angles = ComposedInTable.convert_to_value(self, representation)
        unit_cell = UnitCell(self.saved_value)
        unit_cell.set_parameters(lengths, angles)
        return unit_cell.cell


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
                choices=[(unit, unit) for unit in units_by_measure[measure]],
                label_text=measure,
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
        return tuple(self.attribute[measure] for measure in measures)

    def write_to_attribute(self, value):
        for index, measure in enumerate(measures):
            self.attribute[measure] = value[index]

