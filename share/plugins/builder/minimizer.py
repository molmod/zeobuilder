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


from zeobuilder import context
from zeobuilder.actions.abstract import ConnectBase, AutoConnectMixin
from zeobuilder.actions.composed import Immediate, ImmediateWithMemory, CancelException
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.nodes.meta import PublishedProperties, Property
from zeobuilder.nodes.model_object import ModelObjectInfo
from zeobuilder.nodes.vector import Vector
from zeobuilder.nodes.color_mixin import ColorMixin
from zeobuilder.nodes.elementary import GLFrameBase
from zeobuilder.gui.fields_dialogs import DialogFieldInfo, FieldsDialogSimple
from zeobuilder.gui.glade_wrapper import GladeWrapper
from zeobuilder.child_process import ChildProcessDialog
from zeobuilder.conversion import express_measure
import zeobuilder.actions.primitive as primitive
import zeobuilder.gui.fields as fields

from molmod.data import periodic

import iterative

from OpenGL.GL import *
from OpenGL.GLU import *
import numpy, gtk

import math, copy, time


__all__ = ["Minimizer"]


class Minimizer(Vector, ColorMixin):
    info = ModelObjectInfo("plugins/builder/minimizer.svg")

    #
    # Properties
    #

    def set_radius(self, radius):
        self.radius = radius
        self.invalidate_draw_list()

    def set_quality(self, quality):
        self.quality = quality
        self.invalidate_draw_list()

    published_properties = PublishedProperties({
        "radius": Property(0.5, lambda self: self.radius, set_radius),
        "quality": Property(15, lambda self: self.quality, set_quality),
    })

    #
    # Dialog fields (see action EditProperties)
    #

    dialog_fields = set([
        DialogFieldInfo("Geometry", (2, 2), fields.faulty.Length(
            label_text="Radius",
            attribute_name="radius",
            low=0.0,
            low_inclusive=False,
        )),
        DialogFieldInfo("Markup", (1, 3), fields.faulty.Int(
            label_text="Quality",
            attribute_name="quality",
            minimum=3,
        )),
    ])

    #
    # Draw
    #

    def draw(self):
        Vector.draw(self)
        if self.length <= 0: return
        # halter
        ColorMixin.draw(self)
        gluCylinder(self.quadric, self.radius, 0.0, 0.5*self.length, self.quality, 1)
        glTranslate(0.0, 0.0, 0.5*self.length)
        gluCylinder(self.quadric, 0.0, self.radius, 0.5*self.length, self.quality, 1)

    def write_pov(self, indenter):
        if self.length <= 0: return
        indenter.write_line("union {", 1)
        indenter.write_line("cone {", 1)
        indenter.write_line("<0.0, 0.0, 0.0>, %f, <0.0, 0.0, %f>, 0.0" % (self.radius, 0.5*self.radius))
        indenter.write_line("pigment { rgb <%f, %f, %f> }" % tuple(self.color[0:3]))
        indenter.write_line("finish { my_finish }")
        indenter.write_line("}", -1)
        indenter.write_line("cone {", 1)
        indenter.write_line("<0.0, 0.0, %f>, 0.0, <0.0, 0.0, %f>, %f" % (0.5*self.radius, self.length, self.radius))
        indenter.write_line("pigment { rgb <%f, %f, %f> }" % tuple(self.color[0:3]))
        indenter.write_line("finish { my_finish }")
        indenter.write_line("}", -1)
        Vector.write_pov(self, indenter)
        indenter.write_line("}", -1)

    #
    # Revalidation
    #

    def revalidate_bounding_box(self):
        Vector.revalidate_bounding_box(self)
        if self.length > 0:
            self.bounding_box.extend_with_point(numpy.array([-self.radius, -self.radius, 0]))
            self.bounding_box.extend_with_point(numpy.array([self.radius, self.radius, self.length]))


class ConnectMinimizer(ConnectBase):
    description = "Connect with minimizer"
    menu_info = MenuInfo("default/_Object:tools/_Connect:pair", "_Minimizer", image_name="plugins/builder/minimizer.svg", order=(0, 4, 1, 3, 0, 4))

    def new_connector(self, begin, end):
        return Minimizer(targets=[begin, end])


class AutoConnectMinimizers(AutoConnectMixin, Immediate):
    description = "Connect overlapping atoms with minimizers"
    menu_info = MenuInfo("default/_Object:tools/_Builder:minimizer", "_Connect overlapping atoms with minimizers", order=(0, 4, 1, 6, 0, 0))

    def analyze_selection():
        # A) calling ancestor
        if not AutoConnectMixin.analyze_selection(): return False
        if not Immediate.analyze_selection(): return False
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)

    def allow_node(self, node):
        return isinstance(node, context.application.plugins.get_node("Atom"))

    def get_vector(self, atom1, atom2, distance):
        for reference in atom2.references:
            referent = reference.parent
            if isinstance(referent, Minimizer):
                if (referent.children[0].target == atom1) or \
                   (referent.children[1].target == atom1):
                    return None

        if 0.5*(periodic[atom1.number].radius + periodic[atom2.number].radius) >= distance:
            return Minimizer(targets=[atom1, atom2])
        else:
            return None

    def do(self):
        AutoConnectMixin.do(self, periodic.max_radius)


class MinimizeReportDialog(ChildProcessDialog, GladeWrapper):
    def __init__(self):
        GladeWrapper.__init__(self, "plugins/builder/gui.glade", "di_minimize", "dialog")
        ChildProcessDialog.__init__(self, self.dialog, self.dialog.action_area.get_children())
        self.init_callbacks(MinimizeReportDialog)
        self.init_proxies(["la_num_iter", "la_average_length", "progress_bar"])
        self.state_indices = None

    def run(self, minimize, involved_frames, update_interval, update_steps):
        self.la_num_iter.set_text("0")
        self.la_average_length.set_text(express_measure(0.0, "Length"))
        self.progress_bar.set_fraction(0.0)
        self.progress_bar.set_text("0%")
        self.minimize = minimize
        self.involved_frames = involved_frames

        self.update_interval = update_interval
        self.update_steps = update_steps
        self.last_time = time.time()
        self.last_step = 0
        self.status = None

        result = ChildProcessDialog.run(self, "/usr/bin/iterative", self.minimize)

        # just to avoid confusion
        del self.minimize
        del self.involved_frames
        del self.update_interval
        del self.update_steps
        del self.last_time
        del self.last_step
        del self.status

        return result


    def conditional_update_gui(self):
        if self.last_step > self.update_steps:
            self.last_step = 0
        else:
            self.last_step += 1
            return
        current_time = time.time()
        if self.last_time < current_time:
            self.last_time = current_time + self.update_interval
        else:
            return
        self.update_gui()

    def update_gui(self):
        if self.status is not None:
            self.status.state = numpy.array(self.status.state)
            self.la_num_iter.set_text("%i" % self.status.step)
            self.la_average_length.set_text(express_measure(math.sqrt(self.status.value), "Length"))
            self.progress_bar.set_text("%i%%" % int(self.status.progress*100))
            self.progress_bar.set_fraction(self.status.progress)
            for state_index, frame, variable in zip(self.state_indices, self.involved_frames, self.minimize.root_expression.state_variables):
                (
                    frame.transformation.rotation_matrix,
                    frame.transformation.translation_vector
                ) = variable.extract_state(state_index, self.status.state)
                frame.invalidate_transformation_list()
            context.application.main.drawing_area.queue_draw()

    def on_received(self, com_thread):
        ChildProcessDialog.on_received(self, com_thread)
        instance = com_thread.stack.pop(0)
        if isinstance(instance, iterative.alg.Status):
            self.status = instance
            self.conditional_update_gui()
        else:
            self.state_indices = instance

    def on_finished(self, com_thread):
        ChildProcessDialog.on_finished(self, com_thread)
        self.update_gui()


def get_minimizer_problem(cache):
    class MinimizerProblem:
        minimizers = {}
        frames = set([])
    result = MinimizerProblem()
    parent = cache.parent
    if parent is None:
        return
    for node in cache.nodes:
        if not isinstance(node, Minimizer):
            return
        two_frames = {}
        for child in node.children:
            trace = child.target.trace()
            if parent not in trace: return None
            parent_pos = trace.index(parent)
            if parent_pos == len(trace) - 1: return None
            frame = trace[parent_pos + 1]
            if not isinstance(frame, GLFrameBase): return None
            two_frames[child.target] = frame
        result.minimizers[node] = two_frames
        for frame in two_frames.itervalues():
            result.frames.add(frame)
    result.frames = list(result.frames)
    return result


class MinimizeDistances(ImmediateWithMemory):
    description = "Minimize the minimizer's lengths"
    menu_info = MenuInfo("default/_Object:tools/_Builder:minimizer", "_Minimize selected distances", order=(0, 4, 1, 6, 0, 1))

    parameters_dialog = FieldsDialogSimple(
        "Minimization parameters",
        fields.group.Table(fields=[
            fields.faulty.Float(
                label_text="Update interval [s]",
                attribute_name="update_interval",
                low=0.0,
                low_inclusive=True,
            ),
            fields.faulty.Int(
                label_text="Number of iterations between update",
                attribute_name="update_steps",
                minimum=1
            ),
        ]),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK)),
    )

    report_dialog = MinimizeReportDialog()

    def analyze_selection(parameters=None):
        # A) calling ancestor
        if not ImmediateWithMemory.analyze_selection(parameters): return False
        # B) validating
        cache = context.application.cache
        for Class in cache.classes:
            if not issubclass(Class, Minimizer): return False
        if cache.parent is None: return False
        minimizer_problem = cache.minimizer_problem
        if minimizer_problem is None: return False
        if len(minimizer_problem.frames) == 0: return False
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)

    def init_parameters(self):
        self.parameters.update_interval = 0.4
        self.parameters.update_steps = 1

    def ask_parameters(self):
        if self.parameters_dialog.run(self.parameters) != gtk.RESPONSE_OK:
            self.parameters.clear()

    def do(self):
        cache = context.application.cache
        parent = cache.parent
        involved_frames = cache.minimizer_problem.frames
        minimizers = cache.minimizer_problem.minimizers

        old_transformations = [(frame, copy.deepcopy(frame.transformation)) for frame in involved_frames]

        cost_function = iterative.expr.Root(1, 10, True)
        for frame in involved_frames:
            variable = iterative.var.Frame(
                frame.transformation.rotation_matrix,
                frame.transformation.translation_vector,
            )
            cost_function.register_state_variable(variable)
            constraint = iterative.expr.Orthonormality(1e-10)
            constraint.register_input_variable(variable)

        for minimizer, frames in minimizers.iteritems():
            cost_term = iterative.expr.Spring()
            for target, frame in frames.iteritems():
                cost_term.register_input_variable(
                    cost_function.state_variables[involved_frames.index(frame)],
                    target.get_frame_up_to(frame).translation_vector
                )

        minimize = iterative.alg.DefaultMinimize(
            cost_function,
            numpy.array([0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 1.0, 1.0, 1.0]*len(involved_frames), float),
            iterative.stop.NoIncrease()
        )

        if self.report_dialog.run(minimize, involved_frames, self.parameters.update_interval, self.parameters.update_steps) != gtk.RESPONSE_OK:
            for frame, transformation in old_transformations:
                frame.transformation = transformation
                frame.invalidate_transformation_list()
            raise CancelException

        for frame, transformation in old_transformations:
            primitive.SetPublishedProperty(
                frame, "transformation", transformation, done=True,
            )


nodes = {
    "Minimizer": Minimizer
}


actions = {
    "ConnectMinimizer": ConnectMinimizer,
    "AutoConnectMinimizers": AutoConnectMinimizers,
    "MinimizeDistances": MinimizeDistances,
}

cache_plugins = {
    "minimizer_problem": get_minimizer_problem,
}
