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
from zeobuilder.actions.composed import Immediate
from zeobuilder.actions.abstract import AddBase
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.nodes.meta import Property
from zeobuilder.nodes.elementary import GLGeometricBase
from zeobuilder.nodes.color_mixin import UserColorMixin
from zeobuilder.nodes.model_object import ModelObjectInfo
from zeobuilder.nodes.glcontainermixin import GLContainerMixin
from zeobuilder.gui.fields_dialogs import DialogFieldInfo
from zeobuilder.undefined import Undefined
import zeobuilder.gui.fields as fields
import zeobuilder.actions.primitive as primitive
import zeobuilder.authors as authors

from molmod.transformations import Translation

from molmod.data import periodic
from molmod.unit_cell import UnitCell
from molmod.binning import PositionedObject, SparseBinnedObjects, IntraAnalyseNeighboringObjects
from molmod.clusters import Cluster, ClusterFactory

from OpenGL.GL import *
from OpenGL.GLUT import *
import numpy

import math


class Atom(GLGeometricBase, UserColorMixin):
    info = ModelObjectInfo("plugins/molecular/atom.svg")
    authors = [authors.toon_verstraelen]

    #
    # State
    #

    def initnonstate(self):
        GLGeometricBase.initnonstate(self, Translation)

    #
    # Properties
    #

    def set_user_radius(self, user_radius):
        self.user_radius = user_radius
        self.invalidate_draw_list()
        self.invalidate_boundingbox_list()

    def set_quality(self, quality):
        self.quality = quality
        self.invalidate_draw_list()

    def set_number(self, number):
        self.number = number
        atom_info = periodic[number]
        self.default_radius = atom_info.radius
        color = [atom_info.red, atom_info.green, atom_info.blue, 1.0]
        if None in color:
            self.default_color = numpy.array([0.7, 0.7, 0.7, 1.0], float)
        else:
            self.default_color = numpy.array(color, float)
        self.invalidate_draw_list()
        self.invalidate_boundingbox_list()

    properties = [
        Property("user_radius", Undefined(0.5), lambda self: self.user_radius, set_user_radius, signal=True),
        Property("quality", 15, lambda self: self.quality, set_quality),
        Property("number", 6, lambda self: self.number, set_number, signal=True),
    ]

    #
    # Dialog fields (see action EditProperties)
    #

    dialog_fields = set([
        DialogFieldInfo("Geometry", (2, 9), fields.optional.CheckOptional(
            fields.faulty.Length(
                label_text="User defined radius",
                attribute_name="user_radius",
                low=0.0,
                low_inclusive=False,
            )
        )),
        DialogFieldInfo("Markup", (1, 3), fields.faulty.Int(
            label_text="Quality",
            attribute_name="quality",
            minimum=3,
        )),
        DialogFieldInfo("Molecular", (6, 0), fields.edit.Element(
            attribute_name="number",
            show_popup=False,
        )),
    ])

    #
    # Draw
    #

    def get_radius(self):
        if isinstance(self.user_radius, Undefined):
            return self.default_radius
        else:
            return self.user_radius

    def draw(self):
        GLGeometricBase.draw(self)
        UserColorMixin.draw(self)
        glutSolidSphere(self.get_radius(), self.quality, self.quality / 2)

    def write_pov(self, indenter):
        indenter.write_line("sphere {", 1)
        indenter.write_line("<0.0, 0.0, 0.0>, %f" % (self.get_radius()))
        indenter.write_line("pigment { rgb <%f, %f, %f> }" % tuple(self.get_color()[0:3]))
        GLGeometricBase.write_pov(self, indenter)
        indenter.write_line("}", -1)

    #
    # Revalidation
    #

    def revalidate_bounding_box(self):
        GLGeometricBase.revalidate_bounding_box(self)
        self.bounding_box.extend_with_corners([-self.get_radius()*numpy.ones(3, float), self.get_radius()*numpy.ones(3, float)])

    #
    # Tools
    #

    def num_bonds(self):
        Bond = context.application.plugins.get_node("Bond")
        return sum(isinstance(reference.parent, Bond) for reference in self.references)

    def yield_bonds(self):
        Bond = context.application.plugins.get_node("Bond")
        for reference in self.references:
            referent = reference.parent
            if isinstance(referent, Bond):
                yield referent

    def yield_neighbours(self):
        for bond in self.yield_bonds():
            first = bond.children[0].target
            if first == self:
                neighbour = bond.children[1].target
            else:
                neighbour = first
            if isinstance(neighbour, Atom):
                yield neighbour


class AddAtom(AddBase):
    description = "Add atom"
    menu_info = MenuInfo("default/_Object:tools/_Add:3d", "_Atom", image_name="plugins/molecular/atom.svg", order=(0, 4, 1, 0, 0, 4))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        return AddBase.analyze_selection(Atom)

    def do(self):
        AddBase.do(self, Atom)


class MergeOverlappingAtoms(Immediate):
    description = "Merge overlapping atoms"
    menu_info = MenuInfo("default/_Object:tools/_Molecular:rearrange", "_Merge overlapping atoms", order=(0, 4, 1, 5, 0, 0))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        Atom = context.application.plugins.get_node("Atom")
        if not isinstance(cache.node, GLContainerMixin): return False
        some_atoms = False
        for cls in cache.child_classes:
            if issubclass(cls, Atom):
                some_atoms = True
                break
        if not some_atoms: return False
        # C) passed all tests:
        return True

    def do(self):
        cache = context.application.cache
        parent = cache.node

        unit_cell = None
        if isinstance(parent, UnitCell):
            unit_cell = parent

        Atom = context.application.plugins.get_node("Atom")
        def yield_positioned_atoms():
            for child in parent.children:
                if isinstance(child, Atom):
                    yield PositionedObject(child, child.transformation.t)

        binned_atoms = SparseBinnedObjects(yield_positioned_atoms(), periodic.max_radius)

        def overlap(positioned1, positioned2):
            number = positioned1.id.number
            if number != positioned2.id.number: return
            delta = parent.shortest_vector(positioned2.coordinate - positioned1.coordinate)
            distance = math.sqrt(numpy.dot(delta, delta))
            if distance < periodic[number].radius:
                return True

        cf = ClusterFactory()
        for (positioned1, positioned2), foo in IntraAnalyseNeighboringObjects(binned_atoms, overlap)(unit_cell):
            cf.add_members([positioned1.id, positioned2.id])
        clusters = cf.get_clusters()
        del cf

        # define the new singles
        singles = []
        for cluster in clusters:
            number = cluster.members[0].number
            single = Atom(name="Single " + periodic[number].symbol)
            single.set_number(number)
            singles.append((single, cluster.members))

        # calculate their positions
        for single, overlappers in singles:
            # in the following algorithm, we suppose that the cluster of
            # atoms is small compared to the parent's periodic sizes
            # (if the parent is a periodic system)
            first_pos = overlappers[0].transformation.t
            delta_to_mean = numpy.zeros(3, float)
            for atom in overlappers[1:]:
                delta_to_mean += parent.shortest_vector(atom.transformation.t - first_pos)
            delta_to_mean /= float(len(overlappers))
            single.transformation.t = first_pos + delta_to_mean

        # modify the model
        for single, overlappers in singles:
            lowest_index = min([atom.get_index() for atom in overlappers])
            primitive.Add(single, parent, index=lowest_index)
            for atom in overlappers:
                while len(atom.references) > 0:
                    primitive.SetTarget(atom.references[0], single)
                primitive.Delete(atom)


class RearrangeAtoms(Immediate):
    description = "Rearrange atoms"
    menu_info = MenuInfo("default/_Object:tools/_Molecular:rearrange", "_Rearrange Atoms", order=(0, 4, 1, 5, 0, 1))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        if cache.node is None: return False
        contains_atoms = False
        for cls in cache.child_classes:
            if issubclass(cls, Atom):
                contains_atoms = True
                break
        if not contains_atoms: return False
        # C) passed all tests
        return True

    def do(self):
        cache = context.application.cache
        sorted = {}
        Atom = context.application.plugins.get_node("Atom")
        for child in cache.children:
            if isinstance(child, Atom):
                if child.number in sorted:
                    sorted[child.number].append(child)
                else:
                    sorted[child.number] = [child]

        numbers = sorted.keys()
        numbers.sort()
        numbers.reverse()

        counter = 0
        parent = cache.node
        for number in numbers:
            atoms = sorted[number]
            for atom in atoms:
                atom.name = "%s" % periodic[number].symbol
                primitive.Move(atom, parent, new_index=counter)
                counter += 1


class MoldenLabels(Immediate):
    description = "Label the atoms in molden style."
    menu_info = MenuInfo("default/_Object:tools/_Molecular:rearrange", "_Molden labels", order=(0, 4, 1, 5, 0, 2))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        if cache.node is None: return False
        contains_atoms = False
        for cls in cache.child_classes:
            if issubclass(cls, Atom):
                contains_atoms = True
                break
        if not contains_atoms: return False
        # C) passed all tests
        return True

    def do(self):
        counter = 1
        for node in context.application.cache.children:
            if isinstance(node, Atom):
                primitive.SetProperty(node, "name", periodic[node.number].symbol + str(counter))
                counter += 1


nodes = {
    "Atom": Atom
}

actions = {
    "AddAtom": AddAtom,
    "MergeOverlappingAtoms": MergeOverlappingAtoms,
    "RearrangeAtoms": RearrangeAtoms,
    "MoldenLabels": MoldenLabels,
}
