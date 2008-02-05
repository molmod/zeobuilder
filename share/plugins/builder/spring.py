# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 Toon Verstraelen <Toon.Verstraelen@UGent.be>
#
# This file is part of Zeobuilder.
#
# Zeobuilder is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
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


from zeobuilder import context
from zeobuilder.actions.abstract import ConnectBase, AutoConnectMixin
from zeobuilder.actions.composed import Immediate, ImmediateWithMemory, CancelException, Parameters
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.nodes.meta import Property
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
import zeobuilder.authors as authors

from molmod.data.periodic import periodic
from molmod.transformations import Complete, Translation

import iterative

import numpy, gtk

import math, copy, time


__all__ = ["Spring"]


class Spring(Vector, ColorMixin):
    info = ModelObjectInfo("plugins/builder/spring.svg")
    authors = [authors.toon_verstraelen]

    #
    # Properties
    #

    def set_radius(self, radius):
        self.radius = radius
        self.invalidate_draw_list()

    def set_quality(self, quality):
        self.quality = quality
        self.invalidate_draw_list()

    def set_rest_length(self, rest_length):
        self.rest_length = rest_length
        self.invalidate_draw_list()

    properties = [
        Property("radius", 0.5, lambda self: self.radius, set_radius),
        Property("quality", 15, lambda self: self.quality, set_quality),
        Property("rest_length", 0.0, lambda self: self.rest_length, set_rest_length),
    ]

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
        DialogFieldInfo("Basic", (0, 8), fields.faulty.Length(
            label_text="Rest length",
            attribute_name="rest_length",
            low=0.0,
            low_inclusive=True,
        )),
    ])

    #
    # Draw
    #

    def draw(self):
        Vector.draw(self)
        ColorMixin.draw(self)
        vb = context.application.vis_backend
        if self.length > self.rest_length:
            l_cyl = self.rest_length
            l_cone = 0.5*(self.length - l_cyl)
            if l_cone > 0:
                vb.draw_cone(self.radius, 0.0, l_cone, self.quality)
                vb.translate(0.0, 0.0, l_cone)
            if l_cyl > 0:
                vb.draw_cone(0.5*self.radius, 0.5*self.radius, l_cyl, self.quality)
                vb.translate(0.0, 0.0, l_cyl)
            if l_cone > 0:
                vb.draw_cone(0.0, self.radius, l_cone, self.quality)
        else:
            l_cyl = self.length
            l_cone = 0.5*(self.rest_length - self.length)
            if l_cone > 0:
                vb.translate(0.0, 0.0, -l_cone)
                vb.draw_cone(0.0, self.radius, l_cone, self.quality)
                vb.translate(0.0, 0.0, l_cone)
            if l_cyl > 0:
                vb.draw_cylinder(0.5*self.radius, l_cyl, self.quality)
                vb.translate(0.0, 0.0, l_cyl)
            if l_cone > 0:
                vb.draw_cone(self.radius, 0.0, l_cone, self.quality)

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


class ConnectSpring(ConnectBase):
    description = "Connect with spring"
    menu_info = MenuInfo("default/_Object:tools/_Connect:pair", "_Spring", image_name="plugins/builder/spring.svg", order=(0, 4, 1, 3, 0, 4))
    authors = [authors.toon_verstraelen]

    def new_connector(self, begin, end):
        return Spring(targets=[begin, end])


class AutoConnectSprings(AutoConnectMixin, Immediate):
    description = "Connect overlapping atoms with springs"
    menu_info = MenuInfo("default/_Object:tools/_Builder:spring", "_Connect overlapping atoms with springs", order=(0, 4, 1, 6, 0, 0))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not AutoConnectMixin.analyze_selection(): return False
        if not Immediate.analyze_selection(): return False
        # C) passed all tests:
        return True

    def allow_node(self, node):
        return isinstance(node, context.application.plugins.get_node("Atom"))

    def get_vector(self, atom1, atom2, distance):
        for reference in atom2.references:
            referent = reference.parent
            if isinstance(referent, Spring):
                if (referent.children[0].target == atom1) or \
                   (referent.children[1].target == atom1):
                    return None

        if (periodic[atom1.number].radius + periodic[atom2.number].radius) >= distance:
            return Spring(targets=[atom1, atom2])
        else:
            return None

    def do(self):
        AutoConnectMixin.do(self, 2*periodic.max_radius)


class OptimizationReportDialog(ChildProcessDialog, GladeWrapper):
    def __init__(self):
        GladeWrapper.__init__(self, "plugins/builder/gui.glade", "di_optimize", "dialog")
        ChildProcessDialog.__init__(self, self.dialog, self.dialog.action_area.get_children())
        self.init_callbacks(OptimizationReportDialog)
        self.init_proxies(["la_num_iter", "la_rms_error", "progress_bar"])
        self.state_indices = None

    def run(self, minimize, auto_close, involved_frames, update_interval, update_steps, num_springs):
        self.la_num_iter.set_text("0")
        self.la_rms_error.set_text(express_measure(0.0, "Length"))
        self.progress_bar.set_fraction(0.0)
        self.progress_bar.set_text("0%")
        self.minimize = minimize
        self.involved_frames = [frame for frame in involved_frames if frame is not None]
        self.update_interval = update_interval
        self.update_steps = update_steps
        self.num_springs = num_springs

        self.last_time = time.time()
        self.last_step = 0
        self.status = None

        result = ChildProcessDialog.run(self,
            [context.get_share_file("helpers/iterative")],
            self.minimize, auto_close, pickle=True
        )

        # just to avoid confusion
        del self.minimize
        del self.involved_frames
        del self.update_interval
        del self.update_steps
        del self.last_time
        del self.last_step
        del self.num_springs
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
            self.la_num_iter.set_text("%i" % self.status.step)
            self.la_rms_error.set_text(express_measure(math.sqrt(self.status.value/self.num_springs), "Length"))
            self.progress_bar.set_text("%i%%" % int(self.status.progress*100))
            self.progress_bar.set_fraction(self.status.progress)
            for state_index, frame, variable in zip(self.state_indices, self.involved_frames, self.minimize.root_expression.state_variables):
                if isinstance(variable, iterative.var.Frame):
                    (
                        frame.transformation.r,
                        frame.transformation.t
                    ) = variable.extract_state(state_index, self.status.state)
                elif isinstance(variable, iterative.var.Translation):
                    frame.transformation.t = variable.extract_state(state_index, self.status.state)
                frame.invalidate_transformation_list()
            context.application.main.drawing_area.queue_draw()

    def on_receive(self, instance):
        if isinstance(instance, iterative.alg.Status):
            self.status = instance
            self.conditional_update_gui()
        else:
            self.state_indices = instance

    def on_done(self):
        ChildProcessDialog.on_done(self)
        self.update_gui()


def get_spring_problem(cache):
    class SpringProblem:
        springs = {}
        frames = set([])
    result = SpringProblem()
    parent = cache.parent
    if parent is None:
        return

    def get_frame(trace):
        parent_pos = trace.index(parent)
        if parent_pos < len(trace) - 2:
            frame = trace[parent_pos+1]
            if isinstance(frame, GLFrameBase):
                return frame
        return None

    for node in cache.nodes:
        if not isinstance(node, Spring):
            return None
        two_frames = {}
        for child in node.children:
            frame = get_frame(child.target.trace())
            two_frames[child.target] = frame
        tmp = two_frames.values()
        if tmp[0] == tmp[1]:
            return None
        result.springs[node] = two_frames
        for frame in two_frames.itervalues():
            result.frames.add(frame)
    result.frames = list(result.frames)
    return result
get_spring_problem.authors=[authors.toon_verstraelen]


class OptimizeSprings(ImmediateWithMemory):
    description = "Optimize the springs"
    menu_info = MenuInfo("default/_Object:tools/_Builder:spring", "_Optimize the selected springs", order=(0, 4, 1, 6, 0, 1))
    authors = [authors.toon_verstraelen]

    parameters_dialog = FieldsDialogSimple(
        "Minimization parameters",
        fields.group.Table(fields=[
            fields.edit.CheckButton(
                label_text="Allow free rotation",
                attribute_name="allow_rotation",
            ),
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

    report_dialog = OptimizationReportDialog()

    @staticmethod
    def analyze_selection(parameters=None):
        # A) calling ancestor
        if not ImmediateWithMemory.analyze_selection(parameters): return False
        # B) validating
        cache = context.application.cache
        for Class in cache.classes:
            if not issubclass(Class, Spring): return False
        if cache.parent is None: return False
        spring_problem = cache.spring_problem
        if spring_problem is None: return False
        if len(spring_problem.frames) == 0: return False
        # C) passed all tests:
        return True

    @classmethod
    def default_parameters(cls):
        result = Parameters()
        result.allow_rotation = True
        result.update_interval = 0.4
        result.update_steps = 1
        return result

    def ask_parameters(self):
        if self.parameters_dialog.run(self.parameters) != gtk.RESPONSE_OK:
            self.parameters.clear()
            return

        self.parameters.auto_close_report_dialog = False

    def do(self):
        cache = context.application.cache
        parent = cache.parent
        involved_frames = cache.spring_problem.frames
        springs = cache.spring_problem.springs
        max_step = []

        old_transformations = [
            (frame, copy.deepcopy(frame.transformation))
            for frame in involved_frames if frame is not None
        ]

        variable_indices = dict((frame, index) for index, frame in enumerate(frame for frame in involved_frames if frame is not None))

        cost_function = iterative.expr.Root(1, 10, True)
        for frame in involved_frames:
            if frame is None:
                pass
            elif self.parameters.allow_rotation and isinstance(frame.transformation, Complete):
                variable = iterative.var.Frame(
                    frame.transformation.r,
                    frame.transformation.t,
                )
                cost_function.register_state_variable(variable)
                constraint = iterative.expr.Orthonormality(1e-10)
                constraint.register_input_variable(variable)
                max_step.extend([0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 1.0, 1.0, 1.0])
            elif isinstance(frame.transformation, Translation):
                variable = iterative.var.Translation(
                    frame.transformation.r,
                    frame.transformation.t,
                )
                cost_function.register_state_variable(variable)
                max_step.extend([1.0, 1.0, 1.0])
            else:
                raise UserError("The involved frames shoud be at least capable of being translated.")

        for spring, frames in springs.iteritems():
            spring_term = iterative.expr.Spring(spring.rest_length)
            for target, frame in frames.iteritems():
                if frame is None:
                    spring_term.register_input_variable(
                        iterative.expressions.NoFrame(),
                        target.get_frame_up_to(parent).t
                    )
                else:
                    spring_term.register_input_variable(
                        cost_function.state_variables[variable_indices[frame]],
                        target.get_frame_up_to(frame).t
                    )

        max_step = numpy.array(max_step, float)
        minimize = iterative.alg.DefaultMinimize(
            cost_function,
            max_step,
            max_step*1e-8,
        )

        result = self.report_dialog.run(
            minimize,
            self.parameters.auto_close_report_dialog,
            involved_frames,
            self.parameters.update_interval,
            self.parameters.update_steps,
            len(springs),
        )
        if result != gtk.RESPONSE_OK:
            for frame, transformation in old_transformations:
                frame.transformation = transformation
                frame.invalidate_transformation_list()
            raise CancelException

        for frame, transformation in old_transformations:
            primitive.SetProperty(
                frame, "transformation", transformation, done=True,
            )


class MergeAtomsConnectedWithSpring(Immediate):
    description = "Merge atoms connected by spring"
    menu_info = MenuInfo("default/_Object:tools/_Builder:spring", "_Merge atoms connected by spring", order=(0, 4, 1, 6, 0, 2))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        for cls in cache.classes:
            if not issubclass(cls, Spring):
                return False
        # C) passed all tests:
        return True

    def do(self):
        Atom = context.application.plugins.get_node("Atom")

        cache = context.application.cache
        for spring in list(cache.nodes):
            atom1, atom2 = spring.get_targets()
            if isinstance(atom1, Atom) and isinstance(atom2, Atom):
                replacement = Atom(
                    name="Merge of %s and %s" % (atom1.name, atom2.name),
                    number=max([atom1.number, atom2.number])
                )
                replacement.transformation.t = 0.5*(
                    atom1.get_frame_relative_to(spring.parent).t +
                    atom2.get_frame_relative_to(spring.parent).t
                )
                primitive.Add(replacement, spring.parent, spring.get_index())
                for atom in [atom1, atom2]:
                    while len(atom.references) > 0:
                        primitive.SetTarget(atom.references[0], replacement)
                primitive.Delete(spring)
                primitive.Delete(atom1)
                primitive.Delete(atom2)


nodes = {
    "Spring": Spring
}


actions = {
    "ConnectSpring": ConnectSpring,
    "AutoConnectSprings": AutoConnectSprings,
    "OptimizeSprings": OptimizeSprings,
    "MergeAtomsConnectedWithSpring": MergeAtomsConnectedWithSpring,
}

cache_plugins = {
    "spring_problem": get_spring_problem,
}

