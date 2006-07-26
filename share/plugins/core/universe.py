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
from zeobuilder.nodes.meta import NodeClass, PublishedProperties, Property, DialogFieldInfo
from zeobuilder.nodes.elementary import GLContainerBase
from zeobuilder.nodes.parent_mixin import ReferentMixin
from zeobuilder.nodes.glmixin import GLTransformationMixin
from zeobuilder.nodes.helpers import FrameAxes
from zeobuilder.nodes.reference import SpatialReference
from zeobuilder.actions.composed import ImmediateWithMemory
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.gui import load_image
from zeobuilder.gui.fields_dialogs import FieldsDialogSimple
from zeobuilder.transformations import Translation
from zeobuilder.zml import dump_to_file, load_from_file
import zeobuilder.actions.primitive as primitive
import zeobuilder.gui.fields as fields

from molmod.unit_cell import UnitCell
from molmod.units import angstrom

from OpenGL.GL import *
import numpy, gtk

import math, copy, StringIO


class PeriodicBox(UnitCell):

    __metaclass__ = NodeClass

    #
    # Properties
    #

    def set_cell(self, cell):
        #if abs(numpy.linalg.det(cell)) < 1e-10:
        #    raise ValueError, "The volume of the unit cell must be significantly larger than zero."
        self.cell = cell
        self.update_reciproke()
        self.invalidate_draw_list()
        for child in self.children:
            child.invalidate_draw_list()
            child.invalidate_boundingbox_list()

    def set_cell_active(self, cell_active):
        self.cell_active = cell_active
        self.update_reciproke()
        self.invalidate_draw_list()
        for child in self.children:
            child.invalidate_draw_list()
            child.invalidate_boundingbox_list()

    def set_box_visible(self, box_visible):
        self.box_visible = box_visible
        self.invalidate_draw_list()

    published_properties = PublishedProperties({
        # The columns of the cell are the vectors that correspond
        # to the ridges of the parallellepipedum that describe the unit cell. In
        # other words this matrix transforms a unit cube to the unit cell.
        "cell": Property(numpy.array([[10, 0.0, 0.0], [0.0, 10.0, 0.0], [0.0, 0.0, 10.0]])*angstrom, lambda self: self.cell, set_cell),
        "cell_active": Property(numpy.array([False, False, False]), lambda self: self.cell_active, set_cell_active),
        "box_visible": Property(True, lambda self: self.box_visible, set_box_visible)
    })

    #
    # Dialog fields (see action EditProperties)
    #

    dialog_fields = set([
        DialogFieldInfo("Unit cell", (5, 0), fields.composed.CellMatrix(
            label_text="Cell dimensions",
            attribute_name="cell",
            invalid_message="Invalid unit cell dimensions",
        )),
        DialogFieldInfo("Unit cell", (5, 1), fields.composed.CellActive(
            label_text="Active directions",
            attribute_name="cell_active",
        )),
        DialogFieldInfo("Markup", (1, 5),fields.edit.CheckButton(
            label_text="Show periodic box (if active)",
            attribute_name="box_visible",
        ))
    ])

    #
    # Draw
    #

    def draw_box(self, light, draw_line, set_color):
        # filter out the inactive cell vectors: the rows of the cage matrix
        # correspond to the half ridges if that dimension is periodic, other
        # wise the row is zero.
        cage = numpy.transpose(0.5 * self.cell * self.cell_active)
        # calculate all corners of the parallellepipedum
        # r=right, l=left, t=top, b=bottom, f=front, a=back
        rtf =  cage[0] + cage[1] + cage[2]
        ltf = -cage[0] + cage[1] + cage[2]
        rbf =  cage[0] - cage[1] + cage[2]
        lbf = -cage[0] - cage[1] + cage[2]
        rta =  cage[0] + cage[1] - cage[2]
        lta = -cage[0] + cage[1] - cage[2]
        rba =  cage[0] - cage[1] - cage[2]
        lba = -cage[0] - cage[1] - cage[2]
        # colors
        col  = {True: 6.0, False: 4.0}[light]
        sat  = {True: 0.0, False: 1.0}[light]
        gray = {True: 6.0, False: 4.0}[light]

        if self.cell_active[0]:
            # the ridges parallell to the x-axis
            set_color(col, sat, sat)
            draw_line(lba, rba)
            set_color(gray, gray, gray)
            if self.cell_active[2]:
                draw_line(lbf, rbf)
            if self.cell_active[1] and self.cell_active[2]:
                draw_line(ltf, rtf)
            if self.cell_active[1]:
                draw_line(lta, rta)

        if self.cell_active[1]:
            # the ridges parallell to the y-axis
            set_color(sat, col, sat)
            draw_line(lba, lta)
            set_color(gray, gray, gray)
            if self.cell_active[2]:
                draw_line(lbf, ltf)
            if self.cell_active[0] and self.cell_active[2]:
                draw_line(rbf, rtf)
            if self.cell_active[0]:
                draw_line(rba, rta)

        if self.cell_active[2]:
            # the ridges parallell to the z-axis
            set_color(sat, sat, col)
            draw_line(lba, lbf)
            set_color(gray, gray, gray)
            if self.cell_active[1]:
                draw_line(lta, ltf)
            if self.cell_active[0] and self.cell_active[1]:
                draw_line(rta, rtf)
            if self.cell_active[0]:
                draw_line(rba, rbf)

    def draw(self, light):
        if self.box_visible:
            def draw_line(begin, end):
                glVertexf(begin)
                glVertexf(end)

            def set_color(r, g, b):
                glMaterial(GL_FRONT, GL_AMBIENT, [r, g, b, 1.0])

            glLineWidth(2)
            glMaterial(GL_FRONT, GL_DIFFUSE, [0.0, 0.0, 0.0, 0.0])
            glMaterial(GL_FRONT, GL_SPECULAR, [0.0, 0.0, 0.0, 0.0])
            glBegin(GL_LINES)
            self.draw_box(light, draw_line, set_color)
            glEnd()
            glMaterial(GL_FRONT, GL_SPECULAR, [0.7, 0.7, 0.7, 1.0])

    def write_pov(self, indenter):
        if self.box_visible:
            color = numpy.zeros(3, float)
            def draw_line(begin, end):
                indenter.write_line("cylinder {", 1)
                indenter.write_line("<%f, %f, %f>, <%f, %f, %f>, 0.05" % (tuple(begin) + tuple(end)))
                indenter.write_line("pigment { rgb <%f, %f, %f> }" % tuple(color))
                indenter.write_line("}", -1)

            def set_color(r, g, b):
                color[0] = r
                color[1] = g
                color[2] = b

            self.draw_box(True, draw_line, set_color)

    #
    # Revalidation
    #

    def extend_bounding_box(self, bounding_box):
        if self.box_visible:
            cage = numpy.transpose(0.5 * self.cell * self.cell_active)
            bounding_box.extend_with_point( cage[0] + cage[1] + cage[2])
            bounding_box.extend_with_point(-cage[0] + cage[1] + cage[2])
            bounding_box.extend_with_point( cage[0] - cage[1] + cage[2])
            bounding_box.extend_with_point(-cage[0] - cage[1] + cage[2])
            bounding_box.extend_with_point( cage[0] + cage[1] - cage[2])
            bounding_box.extend_with_point(-cage[0] + cage[1] - cage[2])
            bounding_box.extend_with_point( cage[0] - cage[1] - cage[2])
            bounding_box.extend_with_point(-cage[0] - cage[1] - cage[2])


class GLPeriodicContainer(GLContainerBase, PeriodicBox):

    #
    # State
    #

    def initstate(self, **initstate):
        GLContainerBase.initstate(self, **initstate)
        self.child_connections = {}
        for child in self.children:
            if isinstance(child, GLTransformationMixin):
                self.child_connections[child] = child.connect("on-transformation-list-invalidated", self.on_child_transformation_changed)
        self.update_reciproke()

    #
    # Properties
    #

    def set_cell(self, cell):
        PeriodicBox.set_cell(self, cell)
        self.update_child_positions()
        self.invalidate_boundingbox_list()


    def set_cell_active(self, cell_active):
        PeriodicBox.set_cell_active(self, cell_active)
        self.update_child_positions()
        self.invalidate_boundingbox_list()

    #
    # Tree
    #

    def add(self, modelobject, index=-1):
        GLContainerBase.add(self, modelobject, index)
        if isinstance(modelobject, GLTransformationMixin):
            self.child_connections[modelobject] = modelobject.connect("on-transformation-list-invalidated", self.on_child_transformation_changed)
            self.on_child_transformation_changed(modelobject)

    def remove(self, modelobject):
        GLContainerBase.remove(self, modelobject)
        if isinstance(modelobject, GLTransformationMixin):
            modelobject.disconnect(self.child_connections[modelobject])

    #
    # Draw
    #

    def draw(self):
        GLContainerBase.draw(self)
        PeriodicBox.draw(self, self.selected)

    def write_pov(self, indenter):
        PeriodicBox.write_pov(self, indenter)
        GLContainerBase.write_pov(self, indenter)

    #
    # Invalidate
    #

    def on_child_transformation_changed(self, child):
        self.wrap_position_in_cell(child)

    #
    # Revalidate
    #

    def revalidate_bounding_box(self):
        GLContainerBase.revalidate_bounding_box(self)
        PeriodicBox.extend_bounding_box(self, self.bounding_box)

    #
    # Geometrix
    #

    def wrap_position_in_cell(self, child):
        cell_index = self.to_index(child.transformation.translation_vector)
        if cell_index.any():
            translation = Translation()
            translation.translation_vector = -numpy.dot(self.cell, cell_index)
            primitive.Transform(child, translation)

    def update_child_positions(self):
        if not self.cell_active.any(): return
        for child in self.children:
            if isinstance(child, GLTransformationMixin):
                self.wrap_position_in_cell(child)

    def shortest_vector(self, delta):
        return PeriodicBox.shortest_vector(self, delta)


def yield_all_positions(l):
    if len(l) == 0:
        yield []
    else:
        for rest in yield_all_positions(l[1:]):
            for i in xrange(int(l[0])):
                yield [i] + rest


class Universe(GLPeriodicContainer, FrameAxes):
    icon = load_image("universe.svg", (20, 20))

    #
    # Properties
    #

    def set_repetitions(self, repetitions):
        self.repetitions = repetitions
        self.invalidate_draw_list()

    published_properties = PublishedProperties({
        "repetitions": Property(numpy.array([1, 1, 1]), lambda self: self.repetitions, set_repetitions),
    })

    #
    # Dialog fields (see action EditProperties)
    #

    dialog_fields = set([
        DialogFieldInfo("Unit cell", (5, 2), fields.composed.Repetitions(
            label_text="Repetitions",
            attribute_name="repetitions",
            invalid_message="Please enter valid repetitions",
        ))
    ])

    #
    # Tree
    #

    def check_add(Class, ModelClass):
        if not GLPeriodicContainer.check_add(ModelClass): return False
        if issubclass(ModelClass, Universe): return False
        return True
    check_add = classmethod(check_add)

    #
    # Flags
    #

    def set_selected(self, selected):
        GLPeriodicContainer.set_selected(self, selected)
        self.invalidate_draw_list()

    #
    # Draw
    #

    def draw(self):
        # reduce the number of repetitions to one for inactive axes
        repetitions = self.repetitions * self.cell_active + 1 - self.cell_active
        for position in yield_all_positions(repetitions):
            glPushMatrix()
            t = numpy.dot(self.cell, position)
            glTranslate(t[0], t[1], t[2])
            GLPeriodicContainer.draw(self)
            glPopMatrix()
        FrameAxes.draw(self, self.selected)

    def write_pov(self, indenter):
        indenter.write_line("union {", 1)
        FrameAxes.write_pov(self, indenter)
        GLPeriodicContainer.write_pov(self, indenter)
        indenter.write_line("}", -1)

    #
    # Revalidation
    #

    def revalidate_bounding_box(self):
        GLPeriodicContainer.revalidate_bounding_box(self)
        FrameAxes.extend_bounding_box(self, self.bounding_box)


class UnitCellToCluster(ImmediateWithMemory):
    description = "Convert the unit cell to a cluster"
    menu_info = MenuInfo("default/_Object:special", "_Unit cell to cluster", order=(0, 4, 2, 0))

    cuttoff = FieldsDialogSimple(
        "Unit cell to cluster",
        fields.group.Table(
            fields=[
                fields.composed.Interval(
                    attribute_name="interval_%s" % ridge.lower(),
                    invalid_message="Please enter a valid interval for the fractional coordinates of ridge %s" % ridge,
                    interval_name=ridge,
                    length=False,
                )
                for ridge in ["A", "B", "C"]
            ],
            buttons=fields.group.CHECK_BUTTONS,
            label_text="The cutoff region in fractional coordinates:"
        ),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK))
    )

    def analyze_selection(parameters=None):
        # A) calling ancestor
        if not ImmediateWithMemory.analyze_selection(parameters): return False
        # B) validating
        node = context.application.cache.node
        if not isinstance(node, UnitCell): return False
        if sum(node.cell_active) == 0: return False
        if hasattr(parameters, "interval_a") and not node.cell_active[0]: return False
        if hasattr(parameters, "interval_b") and not node.cell_active[1]: return False
        if hasattr(parameters, "interval_c") and not node.cell_active[2]: return False
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)

    def ask_parameters(self):
        universe = context.application.cache.node
        if universe.cell_active[0]:
            self.parameters.interval_a = numpy.array([-0.5, -0.5 + universe.repetitions[0]], float)
        if universe.cell_active[1]:
            self.parameters.interval_b = numpy.array([-0.5, -0.5 + universe.repetitions[1]], float)
        if universe.cell_active[2]:
            self.parameters.interval_c = numpy.array([-0.5, -0.5 + universe.repetitions[2]], float)
        if self.cuttoff.run(self.parameters) != gtk.RESPONSE_OK:
            self.parameters.clear()

    def do(self):
        universe = context.application.cache.node
        def extend_to_cluster(axis, interval):
            if interval is None: return
            assert universe.cell_active[axis]
            interval.sort()
            index_min = int(math.floor(interval[0]))
            index_max = int(math.ceil(interval[1]))

            positioned = [
                node
                for node
                in universe.children
                if (
                    isinstance(node, GLTransformationMixin) and
                    isinstance(node.transformation, Translation)
                )
            ]
            if len(positioned) == 0: return

            serialized = StringIO.StringIO()
            dump_to_file(serialized, positioned)

            # replication the positioned objects
            new_children = {}
            for cell_index in xrange(index_min, index_max+1):
                serialized.seek(0)
                nodes = load_from_file(serialized)
                new_children[cell_index] = {}
                for node_index, node in enumerate(nodes):
                    position = node.transformation.translation_vector + universe.cell[:,axis]*cell_index
                    fractional = universe.to_fractional(position)
                    if (fractional[axis] < interval[0]) or (fractional[axis] > interval[1]):
                        continue
                    node.transformation.translation_vector = position
                    new_children[cell_index][node_index] = node

            new_connectors = []
            # replicate the objects that connect these positioned objects
            for cell_index in xrange(index_min, index_max+1):
                for connector in universe.children:
                    if not isinstance(connector, ReferentMixin): continue
                    skip = False
                    for reference in connector.children:
                        if not isinstance(reference, SpatialReference):
                            skip = True
                            break
                    if skip: continue

                    first_target_orig = connector.children[0].target
                    first_target_index = positioned.index(first_target_orig)
                    first_target = new_children[cell_index].get(first_target_index)
                    if first_target is None:
                        continue
                    new_targets = [first_target]

                    skip = False
                    for reference in connector.children[1:]:
                        other_target_orig = reference.target
                        shortest_vector = universe.shortest_vector((
                            other_target_orig.transformation.translation_vector
                           -first_target_orig.transformation.translation_vector
                        ))
                        translation = first_target.transformation.translation_vector + shortest_vector
                        other_cell_index = universe.to_index(translation)
                        other_target_index = positioned.index(other_target_orig)
                        other_cell_children = new_children.get(other_cell_index[axis])
                        if other_cell_children is None:
                            skip = True
                            break
                        other_target = other_cell_children.get(other_target_index)
                        if other_target is None:
                            skip = True
                            break
                        new_targets.append(other_target)
                    if skip:
                        del new_targets
                        continue

                    state = connector.__getstate__()
                    state["targets"] = new_targets
                    new_connectors.append(connector.__class__(**state))

            # forget about the others

            serialized.close()
            del serialized

            # remove the existing nodes

            while len(universe.children) > 0:
                primitive.Delete(universe.children[0])
            del positioned

            # remove the periodicity

            tmp_active = universe.cell_active.copy()
            tmp_active[axis] = False
            primitive.SetPublishedProperty(universe, "cell_active", tmp_active)

            # add the new nodes

            for nodes in new_children.itervalues():
                for node in nodes.itervalues():
                    primitive.Add(node, universe)

            for connector in new_connectors:
                primitive.Add(connector, universe)


        if hasattr(self.parameters, "interval_a"):
            extend_to_cluster(0, self.parameters.interval_a)
        if hasattr(self.parameters, "interval_b"):
            extend_to_cluster(1, self.parameters.interval_b)
        if hasattr(self.parameters, "interval_c"):
            extend_to_cluster(2, self.parameters.interval_c)


nodes = {
    "Universe": Universe
}

actions = {
    "UnitCellToCluster": UnitCellToCluster
}
