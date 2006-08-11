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
# -


from zeobuilder import context
from zeobuilder.actions.composed import ImmediateWithMemory
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.nodes.elementary import GLFrameBase
from zeobuilder.gui.fields_dialogs import FieldsDialogSimple
#from zeobuilder.gui.glade_wrapper import GladeWrapper
from zeobuilder.undefined import Undefined
#from zeobuilder.child_process import ChildProcessDialog
#import zeobuilder.actions.primitive as primitive
import zeobuilder.gui.fields as fields

from molmod.transformations import Rotation
from molmod.units import from_angstrom

import gtk


class ConnectionPointDescription(fields.composed.ComposedInTable):
    Popup = fields.popups.Default

    def __init__(self, label_text=None, attribute_name=None, show_popup=True, history_name=None, show_field_popups=False):
        fields.composed.ComposedInTable.__init__(
            self,
            fields=[
                fields.faulty.Entry(
                    label_text="Filter expression",
                    show_popup=True,
                    history_name="filter",
                ), fields.faulty.Entry(
                    label_text="Radius expression",
                ), fields.faulty.Entry(
                    label_text="Quality expression",
                )
            ],
            label_text=label_text,
            attribute_name=attribute_name,
            show_popup=show_popup,
            history_name=history_name,
            show_field_popups=show_field_popups
        )

    def applicable_attribute(self):
        return (
            isinstance(self.attribute, tuple) and
            len(self.attribute) == 3 and
            isinstance(self.attribute[0], str) and
            isinstance(self.attribute[1], str) and
            isinstance(self.attribute[2], str)
        )


class ScanForConnections(ImmediateWithMemory):
    description = "Scan for connections"
    menu_info = MenuInfo("default/_Object:tools/_Builder:conscan", "_Scan for connections", order=(0, 4, 1, 6, 1, 0))

    geometry_dialog = FieldsDialogSimple(
        "Connection scanner: Geometries (1/2)",
        fields.group.Table(fields=[
            ConnectionPointDescription(
                label_text="Geometry 1: connecting points",
                attribute_name="connect_description1"
            ),
            ConnectionPointDescription(
                label_text="Geometry 2: connecting points",
                attribute_name="connect_description2"
            ),
            ConnectionPointDescription(
                label_text="Geometry 1: repulsive points",
                attribute_name="repulse_description1"
            ),
            ConnectionPointDescription(
                label_text="Geometry 2: repulsive points",
                attribute_name="repulse_description2"
            ),
        ], cols=2),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK)),
    )

    parameters_dialog = FieldsDialogSimple(
        "Connection scanner: Parameters (2/2)",
        fields.group.Table(fields=[
            fields.group.Table(fields=[
                fields.faulty.Length(
                    label_text="Action radius",
                    attribute_name="action_radius",
                    low=0.0,
                    low_inclusive=False,
                ),
                fields.faulty.Length(
                    label_text="Overlap tolerance",
                    attribute_name="overlap_error",
                    low=0.0,
                    low_inclusive=False,
                ),
            ]),
            fields.group.Table(fields=[
                fields.optional.RadioOptional(slave=fields.group.Table(fields=[
                #fields.group.Table(fields=[
                    fields.edit.CheckButton(
                        label_text="Allow inversion rotations",
                        attribute_name="allow_inversions",
                    ),
                    fields.faulty.Length(
                        label_text="Triangle side tolerance",
                        attribute_name="triangle_side_tolerance",
                        low=0.0,
                        low_inclusive=False,
                    ),
                    fields.faulty.Length(
                        label_text="Minimum triangle size",
                        attribute_name="minimum_triangle_size",
                        low=0.0,
                        low_inclusive=False,
                    ),
                    fields.faulty.Length(
                        label_text="Translation tolerance",
                        attribute_name="translation_tolerance_a",
                        low=0.0,
                        low_inclusive=False,
                    ),
                    fields.faulty.Float(
                        label_text="Rotation tolerance",
                        attribute_name="rotation_tolerance",
                        low=0.0,
                        low_inclusive=False,
                    ),
                ], label_text="Allow free rotations")),
                fields.optional.RadioOptional(slave=fields.group.Table(fields=[
                    fields.composed.Rotation(
                        label_text="Relative rotation of the two structures",
                        attribute_name="rotation2",
                    ),
                    fields.faulty.Length(
                        label_text="Distance tolerance",
                        attribute_name="distance_tolerance",
                        low=0.0,
                        low_inclusive=False,
                    ),
                    fields.faulty.Length(
                        label_text="Translation tolerance",
                        attribute_name="translation_tolerance_b",
                        low=0.0,
                        low_inclusive=False,
                    ),
                ], label_text="Use a fixed rotation")),
            ], cols=2, short=True),
        ]),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK)),
    )

    def analyze_selection(parameters=None):
        # A) calling ancestor
        if not ImmediateWithMemory.analyze_selection(parameters): return False
        # B) validating
        cache = context.application.cache
        if len(cache.nodes) == 0 or len(cache.nodes) > 2: return False
        for Class in cache.classes:
            if not issubclass(Class, GLFrameBase): return False
        if len(cache.nodes) == 2 and not isinstance(cache.parent, GLContainerMixin): return False
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)

    def init_parameters(self):
        rotation2 = Rotation()
        rotation2.set_rotation_properties(0.0, [1, 0, 0], False)

        self.parameters.connect_description1 = ("", "", "")
        self.parameters.connect_description2 = ("", "", "")
        self.parameters.repulse_description1 = ("", "", "")
        self.parameters.repulse_description2 = ("", "", "")
        self.parameters.action_radius = from_angstrom(7)
        self.parameters.overlap_error = from_angstrom(0.1)
        self.parameters.allow_inversions = True
        self.parameters.triangle_side_tolerance = from_angstrom(0.1)
        self.parameters.minimum_triangle_size = from_angstrom(0.1)
        self.parameters.translation_tolerance_a = from_angstrom(0.1)
        self.parameters.rotation_tolerance = 0.05
        self.parameters.rotation2 = Undefined(rotation2)
        self.parameters.distance_tolerance = Undefined(from_angstrom(0.1))
        self.parameters.translation_tolerance_b = Undefined(from_angstrom(0.1))

    def ask_parameters(self):
        if len(context.application.cache.nodes) == 1:
            if not isinstance(self.parameters.connect_description2, Undefined):
                self.parameters.connect_description2 = Undefined(self.parameters.connect_description2)
            if not isinstance(self.parameters.repulse_description2, Undefined):
                self.parameters.repulse_description2 = Undefined(self.parameters.repulse_description2)
        else:
            if isinstance(self.parameters.connect_description2, Undefined):
                self.parameters.connect_description2 = self.parameters.connect_description2.value
            if isinstance(self.parameters.repulse_description2, Undefined):
                self.parameters.repulse_description2 = self.parameters.repulse_description2.value

        if self.geometry_dialog.run(self.parameters) != gtk.RESPONSE_OK:
            self.parameters.clear()
            return

        if self.parameters_dialog.run(self.parameters) != gtk.RESPONSE_OK:
            self.parameters.clear()
            return

    def do(self):
        cache = context.application.cache


actions = {
    "ScanForConnections": ScanForConnections,
}
