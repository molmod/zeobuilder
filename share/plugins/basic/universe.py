# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 - 2010 Toon Verstraelen <Toon.Verstraelen@UGent.be>, Center
# for Molecular Modeling (CMM), Ghent University, Ghent, Belgium; all rights
# reserved unless otherwise stated.
#
# This file is part of Zeobuilder.
#
# Zeobuilder is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# In addition to the regulations of the GNU General Public License,
# publications and communications based in parts on this program or on
# parts of this program are required to cite the following article:
#
# "ZEOBUILDER: a GUI toolkit for the construction of complex molecules on the
# nanoscale with building blocks", Toon Verstraelen, Veronique Van Speybroeck
# and Michel Waroquier, Journal of Chemical Information and Modeling, Vol. 48
# (7), 1530-1541, 2008
# DOI:10.1021/ci8000748
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
from zeobuilder.actions.composed import ImmediateWithMemory, Immediate, \
    UserError, Parameters
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.nodes.meta import Property
from zeobuilder.nodes.elementary import GLContainerBase, GLReferentBase
from zeobuilder.nodes.model_object import ModelObjectInfo
from zeobuilder.nodes.parent_mixin import ReferentMixin
from zeobuilder.nodes.glmixin import GLTransformationMixin
from zeobuilder.nodes.helpers import FrameAxes
from zeobuilder.nodes.reference import SpatialReference
from zeobuilder.nodes.vector import Vector
from zeobuilder.undefined import Undefined
from zeobuilder.gui.fields_dialogs import FieldsDialogSimple, DialogFieldInfo
from zeobuilder.zml import dump_to_file, load_from_file
import zeobuilder.actions.primitive as primitive
import zeobuilder.gui.fields as fields
import zeobuilder.authors as authors

from molmod import Translation, UnitCell, angstrom

import numpy, gtk

import StringIO


default_unit_cell = UnitCell(numpy.identity(3, float)*10*angstrom, numpy.zeros(3, bool))


class GLPeriodicContainer(GLContainerBase):

    #
    # Properties
    #

    def update_vectors(self):
        for node in self.children:
            if isinstance(node, GLReferentBase):
                node.invalidate_draw_list()
                node.invalidate_boundingbox_list()

    def set_cell(self, cell, init=False):
        self.cell = cell
        if not init:
            self.invalidate_boundingbox_list()
            self.invalidate_draw_list()
            self.update_vectors()

    #
    # Properties
    #

    properties = [
        Property("cell", default_unit_cell, lambda self: self.cell, set_cell),
    ]

    #
    # Dialog fields (see action EditProperties)
    #

    dialog_fields = set([
        DialogFieldInfo("Unit cell", (5, 0), fields.composed.Cell(
            label_text="Periodic cell",
            attribute_name="cell",
        )),
    ])


def iter_all_positions(l):
    if len(l) == 0:
        yield []
    else:
        for rest in iter_all_positions(l[1:]):
            for i in xrange(int(l[0])):
                yield [i] + rest


class Universe(GLPeriodicContainer, FrameAxes):
    info = ModelObjectInfo("plugins/basic/universe.svg")
    authors = [authors.toon_verstraelen]
    clip_margin = 0.1

    #
    # State
    #

    def initnonstate(self):
        GLPeriodicContainer.initnonstate(self)
        self.model_center = Translation.identity()

    def update_center(self):
        self.model_center = Translation(0.5*numpy.dot(
            self.cell.matrix,
            self.repetitions * self.cell.active
        ))

    #
    # Properties
    #

    def set_cell(self, cell, init=False):
        GLPeriodicContainer.set_cell(self, cell, init)
        if not init:
            self.update_clip_planes()
            self.update_center()
            self.invalidate_total_list()
            self.invalidate_box_list()

    def set_repetitions(self, repetitions, init=False):
        self.repetitions = repetitions
        if not init:
            self.update_clip_planes()
            self.update_center()
            self.invalidate_box_list()
            self.invalidate_total_list()

    def set_box_visible(self, box_visible, init=False):
        self.box_visible = box_visible
        if not init:
            self.invalidate_total_list()

    def set_clipping(self, clipping, init=False):
        self.clipping = clipping
        if not init:
            self.invalidate_total_list()
            self.invalidate_box_list()
            self.update_clip_planes()

    properties = [
        Property("repetitions", numpy.array([1, 1, 1], int), lambda self: self.repetitions, set_repetitions),
        Property("box_visible", True, lambda self: self.box_visible, set_box_visible),
        Property("clipping", False, lambda self: self.clipping, set_clipping),
    ]

    #
    # Dialog fields (see action EditProperties)
    #

    dialog_fields = set([
        DialogFieldInfo("Unit cell", (5, 2), fields.composed.Repetitions(
            label_text="Repetitions",
            attribute_name="repetitions",
        )),
        DialogFieldInfo("Markup", (1, 5),fields.edit.CheckButton(
            label_text="Show periodic box (if active)",
            attribute_name="box_visible",
        )),
        DialogFieldInfo("Markup", (1, 6),fields.edit.CheckButton(
            label_text="Clip the unit cell contents.",
            attribute_name="clipping",
        )),
    ])

    #
    # Tree
    #

    @classmethod
    def check_add(Class, ModelObjectClass):
        if not GLPeriodicContainer.check_add(ModelObjectClass): return False
        if issubclass(ModelObjectClass, Universe): return False
        return True

    #
    # OpenGL
    #

    def initialize_gl(self):
        vb = context.application.vis_backend
        self.set_clip_planes()
        self.update_center()
        self.box_list = vb.create_list()
        ##print "Created box list (%i): %s" % (self.box_list, self.get_name())
        self.box_list_valid = True
        GLPeriodicContainer.initialize_gl(self)

    def cleanup_gl(self):
        vb = context.application.vis_backend
        GLPeriodicContainer.cleanup_gl(self)
        ##print "Deleting box list (%i): %s" % (self.box_list, self.get_name())
        vb.delete_list(self.box_list)
        del self.box_list
        del self.box_list_valid
        self.unset_clip_planes()

    #
    # Clipping
    #

    def update_clip_planes(self):
        if self.gl_active > 0:
            self.unset_clip_planes()
            self.set_clip_planes()

    def set_clip_planes(self):
        if not self.clipping:
            return
        clip_planes = context.application.scene.clip_planes
        assert len(clip_planes) == 0
        active, inactive = self.cell.active_inactive
        for index in active:
            axis = self.cell.matrix[:,index]
            ortho = self.cell.reciprocal[index] / numpy.linalg.norm(self.cell.reciprocal[index])
            length = abs(numpy.dot(ortho, axis))
            repetitions = self.repetitions[index]
            clip_planes.append(numpy.array(list(ortho) + [self.clip_margin]))
            clip_planes.append(numpy.array(list(-ortho) + [repetitions*length + self.clip_margin]))
        context.application.main.drawing_area.queue_draw()

    def unset_clip_planes(self):
        context.application.scene.clip_planes = []
        context.application.main.drawing_area.queue_draw()

    def shortest_vector(self, delta):
        return self.cell.shortest_vector(delta)

    #
    # Invalidation
    #


    def invalidate_box_list(self):
        if self.gl_active > 0 and self.box_list_valid:
            self.box_list_valid = False
            context.application.main.drawing_area.queue_draw()
            context.application.scene.add_revalidation(self.revalidate_box_list)
            ##print "EMIT %s: on-box-list-invalidated" % self.get_name()

    def invalidate_all_lists(self):
        self.invalidate_box_list()
        GLPeriodicContainer.invalidate_all_lists(self)

    #
    # Draw
    #

    def draw_box(self):
        vb = context.application.vis_backend
        vb.set_line_width(2)
        vb.set_specular(False)

        col  = {True: 4.0, False: 2.5}[self.selected]
        sat  = {True: 0.0, False: 0.5}[self.selected]
        gray = {True: 4.0, False: 2.5}[self.selected]

        def draw_three(origin):
            if self.cell.active[0]:
                vb.set_color(col, sat, sat)
                vb.draw_line(origin, origin+self.cell.matrix[:,0])
            if self.cell.active[1]:
                vb.set_color(sat, col, sat)
                vb.draw_line(origin, origin+self.cell.matrix[:,1])
            if self.cell.active[2]:
                vb.set_color(sat, sat, col)
                vb.draw_line(origin, origin+self.cell.matrix[:,2])

        def draw_gray(origin, axis1, axis2, n1, n2, delta, nd):
            vb.set_color(gray, gray, gray)
            if n1 == 0 and n2 == 0:
                return
            for i1 in xrange(n1+1):
                if i1 == 0:
                    b2 = 1
                    vb.draw_line(origin+delta, origin+nd*delta)
                else:
                    b2 = 0
                for i2 in xrange(b2, n2+1):
                    vb.draw_line(origin+i1*axis1+i2*axis2, origin+i1*axis1+i2*axis2+nd*delta)

        def draw_ortho(origin, axis1, axis2, n1, n2, delta):
            vb.set_color(gray, gray, gray)
            if n1 == 0 and n2 == 0:
                return
            for i1 in xrange(n1+1):
                for i2 in xrange(n2+1):
                    vb.draw_line(
                        origin + i1*axis1 + i2*axis2 - 0.5*delta,
                        origin + i1*axis1 + i2*axis2 + 0.5*delta
                    )

        origin = numpy.zeros(3, float)
        draw_three(origin)
        repetitions = self.repetitions*self.cell.active

        if self.cell.active[2]:
            draw_gray(origin, self.cell.matrix[:,0], self.cell.matrix[:,1], repetitions[0], repetitions[1], self.cell.matrix[:,2], repetitions[2])
        else:
            draw_ortho(origin, self.cell.matrix[:,0], self.cell.matrix[:,1], repetitions[0], repetitions[1], self.cell.matrix[:,2])

        if self.cell.active[0]:
            draw_gray(origin, self.cell.matrix[:,1], self.cell.matrix[:,2], repetitions[1], repetitions[2], self.cell.matrix[:,0], repetitions[0])
        else:
            draw_ortho(origin, self.cell.matrix[:,1], self.cell.matrix[:,2], repetitions[1], repetitions[2], self.cell.matrix[:,0])

        if self.cell.active[1]:
            draw_gray(origin, self.cell.matrix[:,2], self.cell.matrix[:,0], repetitions[2], repetitions[0], self.cell.matrix[:,1], repetitions[1])
        else:
            draw_ortho(origin, self.cell.matrix[:,2], self.cell.matrix[:,0], repetitions[2], repetitions[0], self.cell.matrix[:,1])


        vb.set_specular(True)

    def draw(self):
        FrameAxes.draw(self, self.selected)
        GLPeriodicContainer.draw(self)

    #
    # Revalidation
    #

    def revalidate_box_list(self):
        if self.gl_active > 0:
            ##print "Compiling box list (%i): %s" % (self.box_list,  self.get_name())
            vb = context.application.vis_backend
            vb.begin_list(self.box_list)
            if sum(self.cell.active) > 0:
                self.draw_box()
            vb.end_list()
            self.box_list_valid = True

    def revalidate_total_list(self):
        if self.gl_active > 0:
            ##print "Compiling total list (%i): %s" % (self.total_list, self.get_name())
            vb = context.application.vis_backend
            vb.begin_list(self.total_list)
            if self.visible:
                vb.push_name(self.draw_list)
                if self.box_visible: vb.call_list(self.box_list)
                if self.selected and sum(self.cell.active) == 0:
                    vb.call_list(self.boundingbox_list)

                # repeat the draw list for all the unit cell images.
                if self.clipping:
                    repetitions = (self.repetitions + 2) * self.cell.active + 1 - self.cell.active
                else:
                    repetitions = self.repetitions * self.cell.active + 1 - self.cell.active
                for position in iter_all_positions(repetitions):
                    vb.push_matrix()
                    t = numpy.dot(self.cell.matrix, numpy.array(position) - self.cell.active * self.clipping)
                    vb.translate(*t)
                    vb.call_list(self.draw_list)
                    vb.pop_matrix()

                vb.pop_name()
            vb.end_list()
            self.total_list_valid = True

    def revalidate_bounding_box(self):
        GLPeriodicContainer.revalidate_bounding_box(self)
        FrameAxes.extend_bounding_box(self, self.bounding_box)

    #
    # Signal handlers
    #

    def on_select_chaged(self, selected):
        GLPeriodicContainer.on_select_chaged(self, selected)
        self.invalidate_box_list()


class UnitCellToCluster(ImmediateWithMemory):
    description = "Convert the unit cell to a cluster"
    menu_info = MenuInfo("default/_Object:tools/_Unit Cell:default", "_To cluster", order=(0, 4, 1, 4, 0, 0))
    authors = [authors.toon_verstraelen]
    store_last_parameters = False

    parameters_dialog = FieldsDialogSimple(
        "Unit cell to cluster",
        fields.group.Table(
            fields=[
                fields.optional.CheckOptional(
                    fields.composed.ComposedArray(
                        FieldClass=fields.faulty.Float,
                        array_name=(ridge+".%s"),
                        suffices=["min", "max"],
                        attribute_name="interval_%s" % ridge.lower(),
                        one_row=True,
                        short=False,
                    )
                )
                for ridge in ["a", "b", "c"]
            ],
            label_text="The retained region in fractional coordinates:"
        ),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK))
    )

    @staticmethod
    def analyze_selection(parameters=None):
        # A) calling ancestor
        if not ImmediateWithMemory.analyze_selection(parameters): return False
        # B) validating
        universe = context.application.model.universe
        if sum(universe.cell.active) == 0: return False
        if hasattr(parameters, "interval_a") and not universe.cell.active[0]: return False
        if hasattr(parameters, "interval_b") and not universe.cell.active[1]: return False
        if hasattr(parameters, "interval_c") and not universe.cell.active[2]: return False
        # C) passed all tests:
        return True

    @classmethod
    def default_parameters(cls):
        result = Parameters()
        universe = context.application.model.universe
        if universe.cell.active[0]:
            result.interval_a = numpy.array([0.0, universe.repetitions[0]], float)
        if universe.cell.active[1]:
            result.interval_b = numpy.array([0.0, universe.repetitions[1]], float)
        if universe.cell.active[2]:
            result.interval_c = numpy.array([0.0, universe.repetitions[2]], float)
        return result

    def do(self):
        universe = context.application.model.universe

        def vector_acceptable(vector, cell_vector):
            return abs(numpy.dot(vector, cell_vector)/numpy.dot(cell_vector,cell_vector)) < 0.5


        def extend_to_cluster(axis, interval):
            if (interval is None) or isinstance(interval, Undefined): return
            assert universe.cell.active[axis]
            interval.sort()
            index_min = int(numpy.floor(interval[0]))
            index_max = int(numpy.ceil(interval[1]))

            original_points = [
                node for node in universe.children if (
                    isinstance(node, GLTransformationMixin) and
                    isinstance(node.transformation, Translation)
                )
            ]
            if len(original_points) == 0: return

            original_connections = [
                node for node in universe.children if (
                    isinstance(node, ReferentMixin) and
                    reduce(
                        (lambda x,y: x and y),
                        (isinstance(child, SpatialReference) for child in node.children),
                        True,
                    )
                )
            ]

            # replication of the points
            new_points = {}
            for old_point in original_points:
                orig_position = universe.cell.shortest_vector(old_point.transformation.t)
                #orig_position -= universe.cell.matrix[:,axis]*universe.cell.to_fractional(orig_position)[axis]
                fractional = universe.cell.to_fractional(orig_position)
                for cell_index in xrange(index_min, index_max):
                    position = orig_position + universe.cell.matrix[:,axis]*cell_index
                    if (fractional[axis]+cell_index < interval[0]) or (fractional[axis]+cell_index > interval[1]):
                        continue
                    state = old_point.__getstate__()
                    state["transformation"] = state["transformation"].copy_with(t=position)
                    new_point = old_point.__class__(**state)
                    new_points[(old_point, cell_index)] = new_point

            new_connections = []
            # replication of the connections
            for cell_index in xrange(index_min-1, index_max+1):
                for connection in original_connections:
                    old_target0 = connection.children[0].target
                    new_target0 = new_points.get((old_target0, cell_index))
                    if new_target0 is None: continue

                    new_targets = [new_target0]

                    for reference in connection.children[1:]:
                        abort = True
                        old_target1 = reference.target
                        for offset in 0,1,-1:
                            new_target1 = new_points.get((old_target1, cell_index+offset))
                            if new_target1 is not None:
                                delta = new_target0.transformation.t - new_target1.transformation.t
                                if vector_acceptable(delta, universe.cell.matrix[:,axis]):
                                    new_targets.append(new_target1)
                                    abort = False
                                    break
                        if abort: break
                    if abort:
                        del new_targets
                        continue

                    state = connection.__getstate__()
                    state["targets"] = new_targets
                    new_connections.append(connection.__class__(**state))

            # remove the existing points and connections

            for node in original_connections:
                primitive.Delete(node)
            del original_connections
            for node in original_points:
                primitive.Delete(node)
            del original_points

            # remove the periodicity

            new_active = universe.cell.active.copy()
            new_active[axis] = False
            new_cell = universe.cell.copy_with(active=new_active)
            primitive.SetProperty(universe, "cell", new_cell)

            # add the new nodes

            for node in new_points.itervalues():
                primitive.Add(node, universe)

            for connection in new_connections:
                primitive.Add(connection, universe)


        if hasattr(self.parameters, "interval_a"):
            extend_to_cluster(0, self.parameters.interval_a)
        if hasattr(self.parameters, "interval_b"):
            extend_to_cluster(1, self.parameters.interval_b)
        if hasattr(self.parameters, "interval_c"):
            extend_to_cluster(2, self.parameters.interval_c)


class SuperCell(ImmediateWithMemory):
    description = "Convert the unit cell to larger unit cell"
    menu_info = MenuInfo("default/_Object:tools/_Unit Cell:default", "_Super cell", order=(0, 4, 1, 4, 0, 1))
    authors = [authors.toon_verstraelen]
    store_last_parameters = False

    parameters_dialog = FieldsDialogSimple(
        "Super cell",
        fields.group.Table(
            fields=[
                fields.faulty.Int(
                    attribute_name="repetitions_%s" % ridge.lower(),
                    label_text=ridge,
                    minimum=1,
                )
                for ridge in ["a", "b", "c"]
            ],
            label_text="The number of repetitions along each active axis."
        ),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK))
    )

    @staticmethod
    def analyze_selection(parameters=None):
        # A) calling ancestor
        if not ImmediateWithMemory.analyze_selection(parameters): return False
        # B) validating
        universe = context.application.model.universe
        if sum(universe.cell.active) == 0: return False
        if hasattr(parameters, "repetitions_a") and not universe.cell.active[0]: return False
        if hasattr(parameters, "repetitions_b") and not universe.cell.active[1]: return False
        if hasattr(parameters, "repetitions_c") and not universe.cell.active[2]: return False
        # C) passed all tests:
        return True

    @classmethod
    def default_parameters(cls):
        result = Parameters()
        universe = context.application.model.universe
        if universe.cell.active[0]:
            result.repetitions_a = universe.repetitions[0]
        if universe.cell.active[1]:
            result.repetitions_b = universe.repetitions[1]
        if universe.cell.active[2]:
            result.repetitions_c = universe.repetitions[2]
        return result

    def do(self):
        # create the repetitions vector
        repetitions = []

        if hasattr(self.parameters, "repetitions_a"):
            repetitions.append(self.parameters.repetitions_a)
        else:
            repetitions.append(1)

        if hasattr(self.parameters, "repetitions_b"):
            repetitions.append(self.parameters.repetitions_b)
        else:
            repetitions.append(1)

        if hasattr(self.parameters, "repetitions_c"):
            repetitions.append(self.parameters.repetitions_c)
        else:
            repetitions.append(1)

        repetitions = numpy.array(repetitions, int)

        # serialize the positioned children
        universe = context.application.model.universe

        positioned = [
            node for node in universe.children if (
                isinstance(node, GLTransformationMixin) and
                isinstance(node.transformation, Translation)
            )
        ]
        if len(positioned) == 0: return

        serialized = StringIO.StringIO()
        dump_to_file(serialized, positioned)

        # create the replica's

        # replicate the positioned objects
        new_children = {}
        for cell_index in iter_all_positions(repetitions):
            cell_index = numpy.array(cell_index)
            cell_hash = tuple(cell_index)
            serialized.seek(0)
            nodes = load_from_file(serialized)
            new_children[cell_hash] = nodes
            for node in nodes:
                t = node.transformation.t + numpy.dot(universe.cell.matrix, cell_index)
                new_transformation = node.transformation.copy_with(t=t)
                node.set_transformation(new_transformation)

        # forget about serialized stuff
        serialized.close()
        del serialized

        new_connectors = []
        # replicate the objects that connect these positioned objects
        for cell_index in iter_all_positions(repetitions):
            cell_index = numpy.array(cell_index)
            cell_hash = tuple(cell_index)
            for connector in universe.children:
                # Only applicable to ReferentMixin with only SpatialReference
                # children
                if not isinstance(connector, ReferentMixin):
                    continue
                skip = False
                for reference in connector.children:
                    if not isinstance(reference, SpatialReference):
                        skip = True
                        break
                if skip:
                    continue

                # first locate the new first target for this cell_index
                first_target_orig = connector.children[0].target
                first_target_index = positioned.index(first_target_orig)
                first_target = new_children[cell_hash][first_target_index]
                assert first_target is not None
                new_targets = [first_target]

                for reference in connector.children[1:]:
                    # then find the other new targets, taking into account
                    # periodicity
                    other_target_orig = reference.target
                    shortest_vector = universe.shortest_vector((
                        other_target_orig.transformation.t
                        -first_target_orig.transformation.t
                    ))
                    translation = first_target.transformation.t + shortest_vector
                    other_target_pos = translation
                    other_cell_index = numpy.floor(universe.cell.to_fractional(other_target_pos)).astype(int)
                    other_cell_index %= repetitions
                    other_cell_hash = tuple(other_cell_index)
                    other_target_index = positioned.index(other_target_orig)
                    other_cell_children = new_children.get(other_cell_hash)
                    assert other_cell_children is not None
                    other_target = other_cell_children[other_target_index]
                    assert other_target is not None
                    new_targets.append(other_target)

                state = connector.__getstate__()
                state["targets"] = new_targets
                new_connectors.append(connector.__class__(**state))

        # remove the existing nodes
        while len(universe.children) > 0:
            primitive.Delete(universe.children[0])
        del positioned

        # multiply the cell matrix and reset the number of repetitions
        new_matrix = universe.cell * repetitions
        primitive.SetProperty(universe, "cell", new_matrix)
        primitive.SetProperty(universe, "repetitions", numpy.array([1, 1, 1], int))

        # add the new nodes
        for nodes in new_children.itervalues():
            for node in nodes:
                primitive.Add(node, universe)

        for connector in new_connectors:
            primitive.Add(connector, universe)


class DefineUnitCellVectors(Immediate):
    description = "Wraps the universe in a unit cell"
    menu_info = MenuInfo("default/_Object:tools/_Unit Cell:default", "_Define unit cell vector(s)", order=(0, 4, 1, 4, 0, 2))
    repeatable = False
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        if len(cache.nodes) < 1: return False
        if len(cache.nodes) + sum(context.application.model.universe.cell.active) > 3: return False
        for Class in cache.classes:
            if not issubclass(Class, Vector): return False
        # C) passed all tests:
        return True

    def do(self):
        vectors = context.application.cache.nodes
        universe = context.application.model.root[0]
        new_cell = universe.cell
        try:
            for vector in vectors:
                new_cell = new_cell.add_cell_vector(vector.shortest_vector_relative_to(universe))
        except ValueError:
            if len(vectors) == 1:
                raise UserError("Failed to add the selected vector as cell vector since it would make the unit cell singular.")
            else:
                raise UserError("Failed to add the selected vectors as cell vectors since they would make the unit cell singular.")
        primitive.SetProperty(universe, "cell", new_cell)


class WrapCellContents(Immediate):
    description = "Wrap the unit cell contents"
    menu_info = MenuInfo("default/_Object:tools/_Unit Cell:default", "_Wrap cell contents", ord("w"), order=(0, 4, 1, 4, 0, 3))
    repeatable = False
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        universe = context.application.model.universe
        if sum(universe.cell.active) == 0: return False
        if len(universe.children) == 0: return False
        # C) passed all tests:
        return True

    def do(self):
        universe = context.application.model.universe
        for child in universe.children:
            if isinstance(child, GLTransformationMixin) and isinstance(child.transformation, Translation):
                cell_index = universe.cell.to_fractional(child.transformation.t)
                cell_index = numpy.floor(cell_index)
                if cell_index.any():
                    t = child.transformation.t - universe.cell.to_cartesian(cell_index)
                    new_transformation = child.transformation.copy_with(t=t)
                    primitive.SetProperty(child, "transformation", new_transformation)


class ScaleUnitCell(ImmediateWithMemory):
    description = "Scale the unit cell and its contents"
    menu_info = MenuInfo("default/_Object:tools/_Unit Cell:default", "_Scale unit cell", order=(0, 4, 1, 4, 0, 4))
    repeatable = False
    authors = [authors.toon_verstraelen]
    store_last_parameters = False

    parameters_dialog = FieldsDialogSimple(
        "Scale unit cell",
        fields.composed.CellMatrix(
            label_text="Cell dimensions",
            attribute_name="matrix",
        ),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK))
    )

    @staticmethod
    def analyze_selection(parameters=None):
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        universe = context.application.model.universe
        if sum(universe.cell.active) == 0: return False
        # C) passed all tests:
        return True

    @classmethod
    def default_parameters(cls):
        result = Parameters()
        result.matrix = context.application.model.universe.cell.matrix.copy()
        return result

    def do(self):
        universe = context.application.model.universe
        scaling = numpy.dot(self.parameters.matrix, numpy.linalg.inv(universe.cell.matrix))
        primitive.SetProperty(universe, "cell", universe.cell.copy_with(matrix=self.parameters.matrix))

        for child in universe.children:
            if isinstance(child, GLTransformationMixin) and isinstance(child.transformation, Translation):
                 new_transformation = child.transformation.copy_with(t=numpy.dot(scaling, child.transformation.t))
                 primitive.SetProperty(child, "transformation", new_transformation)



nodes = {
    "Universe": Universe
}

actions = {
    "UnitCellToCluster": UnitCellToCluster,
    "SuperCell": SuperCell,
    "DefineUnitCellVectors": DefineUnitCellVectors,
    "WrapCellContents": WrapCellContents,
    "ScaleUnitCell": ScaleUnitCell,
}


