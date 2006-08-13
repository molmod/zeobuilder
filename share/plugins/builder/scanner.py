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
from zeobuilder.actions.composed import ImmediateWithMemory, UserError
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.nodes.meta import Property
from zeobuilder.nodes.elementary import GLFrameBase, ReferentBase
from zeobuilder.nodes.model_object import ModelObjectInfo
from zeobuilder.nodes.glmixin import GLTransformationMixin
from zeobuilder.nodes.reference import Reference
from zeobuilder.gui.fields_dialogs import FieldsDialogSimple
from zeobuilder.undefined import Undefined
from zeobuilder.child_process import ChildProcessDialog
import zeobuilder.actions.primitive as primitive
import zeobuilder.gui.fields as fields

from conscan import Geometry, ProgressMessage, Connection

from molmod.transformations import Rotation, Translation
from molmod.units import from_angstrom

import gtk, numpy

import weakref


class ConscanResults(ReferentBase):
    info = ModelObjectInfo("plugins/builder/conscan_results.svg")

    #
    # State
    #

    def create_references(self):
        return [
            Reference(prefix="First"),
            Reference(prefix="Second")
        ]

    #
    # Properties
    #

    def get_connections(self):
        return [
            (quality, transformation, [
                (node1().get_index(), node2().get_index())
                for node1, node2 in pairs
            ]) for quality, transformation, pairs
            in self.connections
        ]

    def set_connections(self, connections):
        self.connections = [
            (quality, transformation, [
                (weakref.ref(self.children[0].target.children[index1]), weakref.ref(self.children[0].target.children[index1]))
                for index1, index2 in pairs
            ]) for quality, transformation, pairs
            in self.connections
        ]

    properties = [
        Property("connections", [], get_connections, set_connections),
    ]


class ConscanReportDialog(ChildProcessDialog):
    def __init__(self, progress_items):
        self.dialog = gtk.Dialog(
            "Connection scanner progress", flags=gtk.DIALOG_MODAL,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK),
        )
        ChildProcessDialog.__init__(self, self.dialog, self.dialog.action_area.get_children())
        table = gtk.Table(len(progress_items), 2, )
        self.progress_bars = {}
        for index, (label, name) in enumerate(progress_items):
            l = gtk.Label("%s:" % name)
            l.set_alignment(0.0, 0.5)
            table.attach(l, 0, 1, index, index+1)
            pb = gtk.ProgressBar()
            self.progress_bars[label] = pb
            table.attach(pb, 1, 2, index, index+1)
        table.show_all()
        table.set_border_width(6)
        table.set_row_spacings(6)
        table.set_col_spacings(6)
        self.dialog.vbox.pack_start(table, expand=True, fill=True)

    def clear_gui(self):
        for pb in self.progress_bars.itervalues():
            pb.set_text("- / -")
            pb.set_fraction(0.0)

    def run(self, inp, auto_close):
        self.clear_gui()
        self.connections = []
        if ChildProcessDialog.run(self, "/usr/bin/conscan", inp, auto_close) == gtk.RESPONSE_OK:
            result = self.connections
            del self.connections
            return result

    def handle_message(self, instance):
        if isinstance(instance, ProgressMessage):
            pb = self.progress_bars[instance.label]
            if instance.maximum > 0:
                pb.set_text("%i / %i" % (instance.progress, instance.maximum))
                fraction = float(instance.progress)/instance.maximum
                if fraction > 1: fraction = 1
                elif fraction < 0: fraction = 0
                pb.set_fraction(float(instance.progress)/instance.maximum)
            else:
                pb.set_text("- / -")
                pb.set_fraction(0.0)
        elif isinstance(instance, Connection):
            self.connections.append(instance)


class ConnectionPointDescription(fields.composed.ComposedInTable):
    Popup = fields.popups.Default

    def __init__(self, label_text=None, attribute_name=None, show_popup=True, history_name=None, show_field_popups=True):
        fields.composed.ComposedInTable.__init__(
            self,
            fields=[
                fields.edit.TextView(
                    label_text="Filter expression",
                    history_name="filter",
                    width=250,
                    height=60,
                ), fields.edit.TextView(
                    label_text="Radius expression",
                    history_name="radius",
                    width=250,
                    height=60,
                ), fields.edit.TextView(
                    label_text="Quality expression",
                    history_name="quality",
                    width=250,
                    height=60,
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

    parameters_dialog = FieldsDialogSimple(
        "Connection scanner parameters",
        fields.group.Notebook([
            (
                "Geometry1",
                fields.group.Table(fields=[
                    ConnectionPointDescription(
                        label_text="Connecting points",
                        attribute_name="connect_description1",
                        history_name="conscan_description",
                    ),
                    ConnectionPointDescription(
                        label_text="Repulsive points",
                        attribute_name="repulse_description1",
                        history_name="conscan_description",
                    ),
                ], cols=2),
            ), (
                "Geometry2",
                fields.group.Table(fields=[
                    ConnectionPointDescription(
                        label_text="Connecting points",
                        attribute_name="connect_description2",
                        history_name="conscan_description",
                    ),
                    ConnectionPointDescription(
                        label_text="Repulsive points",
                        attribute_name="repulse_description2",
                        history_name="conscan_description",
                    ),
                ], cols=2),
            ), (
                "Parameters",
                fields.group.Table(fields=[
                    fields.faulty.Length(
                        label_text="Action radius",
                        attribute_name="action_radius",
                        low=0.0,
                        low_inclusive=False,
                    ),
                    fields.faulty.Length(
                        label_text="Overlap tolerance",
                        attribute_name="overlap_tolerance",
                        low=0.0,
                        low_inclusive=False,
                    ),
                    fields.optional.RadioOptional(slave=fields.group.Table(fields=[
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
                ], cols=2),
            )
        ]),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK)),
    )

    triangle_report_dialog = ConscanReportDialog([
        ("calc_env", "Calculating environments"),
        ("comp_env", "Comparing environments"),
        ("calc_trans", "Calculating transformations"),
        ("mirror", "Adding inversions"),
        ("elim_dup", "Eliminating duplicates"),
        ("eval_con", "Evaluating connections"),
    ])

    pair_report_dialog = ConscanReportDialog([
        ("calc_env", "Calculating environments"),
        ("comp_env", "Comparing environments"),
        ("calc_trans", "Calculating transformations"),
        ("elim_dup", "Eliminating duplicates"),
        ("eval_con", "Evaluating connections"),
    ])

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

        self.parameters.connect_description1 = ("True", "node.get_radius()", "1")
        self.parameters.repulse_description1 = ("True", "node.get_radius()", "-1")
        self.parameters.connect_description2 = ("True", "node.get_radius()", "1")
        self.parameters.repulse_description2 = ("True", "node.get_radius()", "-1")
        self.parameters.action_radius = from_angstrom(7)
        self.parameters.overlap_tolerance = from_angstrom(0.1)
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

        if self.parameters_dialog.run(self.parameters) != gtk.RESPONSE_OK:
            self.parameters.clear()
            return

        self.parameters.auto_close_report_dialog = False

    def do(self):
        cache = context.application.cache

        my_globals = context.application.plugins.nodes.copy()

        geometry_nodes = [[], []]

        def get_parameters(node, point_type, geometry_index, filter_expression, radius_expression, quality_expression):
            template = "An exception occured in the %%s expression\nfor the %s points of geometry %i." % (point_type, geometry_index+1)
            my_globals["node"] = node
            try:
                is_connect = eval(filter_expression, my_globals)
            except Exception, e:
                raise UserError(template % "filter")
            if is_connect:
                try:
                    radius = eval(radius_expression, my_globals)
                except Exception, e:
                    raise UserError(template % "radius")
                try:
                    amplitude = eval(quality_expression, my_globals)
                except Exception, e:
                    raise UserError(template % "quality")
                geometry_nodes[geometry_index].append(node)
                return True, radius, amplitude
            else:
                return False, None, None

        def read_geometry(frame, geometry_index, connect_description, repulse_description):
            coordinates = []
            connect_masks = []
            radii = []
            amplitudes = []
            for child in frame.children:
                if isinstance(child, GLTransformationMixin) and \
                   isinstance(child.transformation, Translation):
                    is_connect, radius, amplitude = get_parameters(
                        child, "connecting", geometry_index,
                        *connect_description
                    )
                    if is_connect:
                        coordinates.append(child.transformation.t)
                        connect_masks.append(True)
                        radii.append(radius)
                        amplitudes.append(amplitude)
                    else:
                        is_repulse, radius, amplitude = get_parameters(
                            child, "repulsive", geometry_index,
                            *repulse_description
                        )
                        if is_repulse:
                            coordinates.append(child.transformation.t)
                            connect_masks.append(False)
                            radii.append(radius)
                            amplitudes.append(amplitude)
            return Geometry(
                numpy.array(coordinates, float),
                numpy.array(connect_masks, bool),
                numpy.array(radii, float),
                numpy.array(amplitudes, float)
            )

        inp = {}
        inp["geometry1"] = read_geometry(cache.nodes[0], 0, self.parameters.connect_description1, self.parameters.repulse_description1)
        if len(cache.nodes) == 2:
            inp["geometry2"] = read_geometry(cache.nodes[1], 1, self.parameters.connect_description2, self.parameters.repulse_description2)
        else:
            inp["geometry2"] = None
        inp["action_radius"] = self.parameters.action_radius
        inp["overlap_threshold"] = self.parameters.overlap_tolerance**2
        if not isinstance(self.parameters.allow_inversions, Undefined):
            inp["allow_rotations"] = True
            inp["allow_inversions"] = self.parameters.allow_inversions
            inp["triangle_side_error"] = self.parameters.triangle_side_tolerance
            inp["minimum_triangle_area"] = self.parameters.minimum_triangle_size**2
            inp["translation_threshold"] = self.parameters.translation_tolerance_a**2
            inp["rotation_threshold"] = self.parameters.rotation_tolerance**2
        else:
            inp["allow_rotations"] = False
            inp["rotation2"] = self.parameters.rotation2
            inp["distance_error"] = self.parameters.distance_tolerance
            inp["translation_threshold"] = self.parameters.translation_tolerance_b**2

        if inp["allow_rotations"]:
            connections = self.triangle_report_dialog.run(inp, self.parameters.auto_close_report_dialog)
        else:
            connections = self.pair_report_dialog.run(inp, self.parameters.auto_close_report_dialog)

        if connections is not None and len(connections) > 0:
            if len(cache.nodes) == 1:
                frame1 = cache.nodes[0]
                Duplicate = context.application.plugins.get_action("Duplicate")
                Duplicate()
                frame2 = cache.nodes[0]
                geometry_nodes[1] = geometry_nodes[0]
            else:
                frame1, frame2 = cache.nodes

            conscan_results = ConscanResults(
                targets=[frame1, frame2],
                connections=[(
                    connection.quality,
                    connection.transformation, [
                        (geometry_nodes[0][first].get_index(), geometry_nodes[1][second].get_index())
                        for first, second in connection.pairs
                    ],
                ) for connection in connections],
            )
            primitive.Add(conscan_results, context.application.model.folder)


nodes = {
    "ConscanResults": ConscanResults,
}


actions = {
    "ScanForConnections": ScanForConnections,
}
