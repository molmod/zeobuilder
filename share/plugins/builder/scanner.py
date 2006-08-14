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
from zeobuilder.actions.composed import ImmediateWithMemory, UserError, CancelException, Immediate, CustomAction, Parameters
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.nodes.meta import Property
from zeobuilder.nodes.analysis import common_parent
from zeobuilder.nodes.elementary import GLFrameBase, ReferentBase
from zeobuilder.nodes.model_object import ModelObjectInfo
from zeobuilder.nodes.glmixin import GLTransformationMixin
from zeobuilder.nodes.glcontainermixin import GLContainerMixin
from zeobuilder.nodes.reference import Reference
from zeobuilder.gui.fields_dialogs import FieldsDialogSimple
from zeobuilder.gui.glade_wrapper import GladeWrapper
from zeobuilder.undefined import Undefined
from zeobuilder.child_process import ChildProcessDialog
import zeobuilder.actions.primitive as primitive
import zeobuilder.gui.fields as fields

from conscan import Geometry, ProgressMessage, Connection

from molmod.transformations import Rotation, Translation
from molmod.units import from_angstrom

import gtk, numpy

import weakref, copy


class ConscanResults(ReferentBase):
    info = ModelObjectInfo("plugins/builder/conscan_results.svg", "ShowConscanResultsWindow")

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
                (weakref.ref(self.children[0].target.children[index1]), weakref.ref(self.children[1].target.children[index2]))
                for index1, index2 in pairs
            ]) for quality, transformation, pairs
            in connections
        ]

    properties = [
        Property("connections", [], get_connections, set_connections),
    ]


class ConscanResultsWindow(GladeWrapper):
    def __init__(self):
        self.frame1 = None
        self.frame2 = None

        GladeWrapper.__init__(self, "plugins/builder/gui.glade", "wi_conscan_results", "window")
        self.init_callbacks(ConscanResultsWindow)
        self.init_proxies(["tv_results", "cb_auto_apply", "bu_apply", "bu_apply_opt", "bu_apply_opt_round"])
        self.window.hide()

        self.list_store = gtk.ListStore(float, int, object)

        column = gtk.TreeViewColumn("Quality")
        renderer_text = gtk.CellRendererText()
        column.pack_start(renderer_text, expand=False)
        column.add_attribute(renderer_text, "text", 0)
        self.tv_results.append_column(column)

        column = gtk.TreeViewColumn("# Connections")
        renderer_text = gtk.CellRendererText()
        column.pack_start(renderer_text, expand=False)
        column.add_attribute(renderer_text, "text", 1)
        self.tv_results.append_column(column)

        self.tv_results.set_model(self.list_store)

        self.tree_selection = self.tv_results.get_selection()
        self.tree_selection.connect("changed", self.on_selection_changed)

    def set_conscan_results(self, conscan_results):
        self.frame1 = conscan_results.children[0].target
        self.frame2 = conscan_results.children[1].target
        self.list_store.clear()
        for connection in conscan_results.connections:
            self.list_store.append([connection[0], len(connection[2]), connection])
        self.window.show_all()

    def update_sensitivities(self):
        model, iter = self.tree_selection.get_selected()
        if iter is None:
            self.bu_apply.set_sensitive(False)
            self.bu_apply_opt.set_sensitive(False)
            self.bu_apply_opt_round.set_sensitive(False)
        else:
            self.bu_apply.set_sensitive(not self.cb_auto_apply.get_active())
            self.bu_apply_opt.set_sensitive(True)
            self.bu_apply_opt_round.set_sensitive(True)

    def apply_normal(self):
        model, iter = self.tree_selection.get_selected()
        old_transformation = copy.deepcopy(self.frame2.transformation)
        self.frame2.transformation.clear()
        transformation =  self.frame1.get_frame_relative_to(self.frame2)
        transformation.apply_before(model.get_value(iter, 2)[1])
        self.frame2.set_transformation(transformation)
        primitive.SetProperty(self.frame2, "transformation", old_transformation, done=True)

    def connect_minimizers(self):
        model, iter = self.tree_selection.get_selected()
        Minimizer = context.application.plugins.get_node("Minimizer")
        minimizers = [
            Minimizer(targets=[node1(), node2()])
            for node1, node2
            in model.get_value(iter, 2)[2]
        ]
        parent = common_parent([self.frame1, self.frame2])
        for minimizer in minimizers:
            primitive.Add(minimizer, parent)
        return minimizers

    def free_optimize(self, minimizers):
        context.application.main.select_nodes(minimizers)
        MinimizeDistances = context.application.plugins.get_action("MinimizeDistances")
        parameters = Parameters()
        parameters.allow_rotation = True
        parameters.update_interval = 0.4
        parameters.update_steps = 1
        parameters.auto_close_report_dialog = True
        MinimizeDistances(parameters)

    def translate_optimize(self, minimizers):
        context.application.main.select_nodes(minimizers)
        MinimizeDistances = context.application.plugins.get_action("MinimizeDistances")
        parameters = Parameters()
        parameters.allow_rotation = False
        parameters.update_interval = 0.4
        parameters.update_steps = 1
        parameters.auto_close_report_dialog = True
        MinimizeDistances(parameters)

    def round_rotation(self):
        context.application.main.select_nodes([self.frame1, self.frame2])
        RoundRotation = context.application.plugins.get_action("RoundRotation")
        RoundRotation()

    def clean_minimizers(self, minimizers):
        for minimizer in minimizers:
            primitive.Delete(minimizer)

    def optimize(self):
        minimizers = self.connect_minimizers()
        self.free_optimize(minimizers)
        self.clean_minimizers(minimizers)

    def optimize_and_round(self):
        minimizers = self.connect_minimizers()
        self.free_optimize(minimizers)
        try:
            self.round_rotation()
            self.translate_optimize(minimizers)
        except UserError, CancelException:
            pass
        self.clean_minimizers(minimizers)

    def on_selection_changed(self, selection):
        self.update_sensitivities()
        if self.cb_auto_apply.get_active() and \
           self.tree_selection.get_selected()[1] is not None:
            action = CustomAction("Auto apply connection")
            self.apply_normal()
            action.finish()

    def on_cb_auto_apply_clicked(self, cb_apply):
        self.update_sensitivities()

    def on_bu_apply_clicked(self, button):
        if self.tree_selection.get_selected()[1] is not None:
            action = CustomAction("Apply connection")
            self.apply_normal()
            action.finish()

    def on_bu_apply_opt_clicked(self, button):
        if self.tree_selection.get_selected()[1] is not None:
            action = CustomAction("Apply connection and minimize distances")
            old_selection = copy.copy(context.application.cache.nodes)
            self.apply_normal()
            self.optimize()
            context.application.main.select_nodes(old_selection)
            action.finish()

    def on_bu_apply_opt_round_clicked(self, button):
        if self.tree_selection.get_selected()[1] is not None:
            action = CustomAction("Apply connection, minimize and round rotation")
            old_selection = copy.copy(context.application.cache.nodes)
            self.apply_normal()
            self.optimize_and_round()
            context.application.main.select_nodes(old_selection)
            action.finish()

    def on_window_delete_event(self, window, event):
        self.window.hide()
        return True


class ShowConscanResultsWindow(Immediate):
    description = "Show the selected connection scanner results in a window"
    menu_info = MenuInfo("default/_Object:tools/_Builder:conscan", "Show scan results", order=(0, 4, 1, 6, 1, 1))

    conscan_results_window = ConscanResultsWindow()

    def analyze_selection(parameters=None):
        # A) calling ancestor
        if not ImmediateWithMemory.analyze_selection(parameters): return False
        # B) validating
        if not isinstance(context.application.cache.node, ConscanResults): return False
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)

    def do(self):
        self.conscan_results_window.set_conscan_results(context.application.cache.node)


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

        table.set_border_width(6)
        table.set_row_spacings(6)
        table.set_col_spacings(6)
        table.show_all()

        self.clear_gui()
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
        ("eval_con", "Evaluating connections"),
        ("elim_dup", "Eliminating duplicates"),
        ("send_con", "Receiving solutions"),
    ])

    pair_report_dialog = ConscanReportDialog([
        ("calc_env", "Calculating environments"),
        ("comp_env", "Comparing environments"),
        ("calc_trans", "Calculating transformations"),
        ("eval_con", "Evaluating connections"),
        ("elim_dup", "Eliminating duplicates"),
        ("send_con", "Receiving solutions"),
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
        self.parameters.rotation_tolerance = 0.05
        self.parameters.rotation2 = Undefined(rotation2)
        self.parameters.distance_tolerance = Undefined(from_angstrom(0.1))

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
        else:
            inp["allow_rotations"] = False
            inp["rotation2"] = self.parameters.rotation2
            inp["distance_error"] = self.parameters.distance_tolerance

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
                    float(connection.quality),
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
    "ShowConscanResultsWindow": ShowConscanResultsWindow,
}
