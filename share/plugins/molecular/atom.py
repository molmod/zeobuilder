# -*- coding: utf-8 -*-
# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 - 2012 Toon Verstraelen <Toon.Verstraelen@UGent.be>, Center
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
#--


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

from molmod import Translation, UnitCell, PairSearchIntra, ClusterFactory
from molmod.periodic import periodic

import numpy


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

    def set_user_radius(self, user_radius, init=False):
        self.user_radius = user_radius
        if not init:
            self.invalidate_draw_list()
            self.invalidate_boundingbox_list()

    def set_quality(self, quality, init=False):
        self.quality = quality
        if not init:
            self.invalidate_draw_list()

    def set_number(self, number, init=False):
        self.number = number
        atom_info = periodic[number]
        if atom_info.vdw_radius is not None:
            self.default_radius = atom_info.vdw_radius*0.2
        else:
            self.default_radius = 1.0
        color = [atom_info.red, atom_info.green, atom_info.blue, 1.0]
        if None in color:
            self.default_color = numpy.array([0.7, 0.7, 0.7, 1.0], float)
        else:
            self.default_color = numpy.array(color, float)
        if not init:
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
        vb = context.application.vis_backend
        vb.draw_sphere(self.get_radius(), self.quality)

    #
    # Revalidation
    #

    def revalidate_bounding_box(self):
        GLGeometricBase.revalidate_bounding_box(self)
        radius = self.get_radius()
        self.bounding_box.extend_with_corners(numpy.array([
            [-radius, -radius, -radius],
            [ radius,  radius,  radius]
        ]))

    #
    # Tools
    #

    def num_bonds(self):
        Bond = context.application.plugins.get_node("Bond")
        return sum(isinstance(reference.parent, Bond) for reference in self.references)

    def iter_bonds(self):
        Bond = context.application.plugins.get_node("Bond")
        for reference in self.references:
            referent = reference.parent
            if isinstance(referent, Bond):
                yield referent

    def iter_neighbors(self):
        for bond in self.iter_bonds():
            first = bond.children[0].target
            if first == self:
                neighbor = bond.children[1].target
            else:
                neighbor = first
            if isinstance(neighbor, Atom):
                yield neighbor


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
        atoms = []
        coordinates = []
        for child in parent.children:
            if isinstance(child, Atom):
                atoms.append(child)
                coordinates.append(child.transformation.t)
        coordinates = numpy.array(coordinates)

        cf = ClusterFactory()
        for i0, i1, delta, distance in PairSearchIntra(coordinates, periodic.max_radius*0.4, unit_cell):
            atom0 = atoms[i0]
            atom1 = atoms[i1]
            if atom0.number == atom1.number:
                if distance < periodic[atom0.number].vdw_radius*0.4:
                    cf.add_related(atom0, atom1)
        clusters = cf.get_clusters()
        del cf

        # define the new singles
        singles = []
        for cluster in clusters:
            number = iter(cluster.items).next().number
            single = Atom(name="Single " + periodic[number].symbol)
            single.set_number(number)
            singles.append((single, list(cluster.items)))

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
            single.set_transformation(Translation(first_pos + delta_to_mean))

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
        l = []
        Atom = context.application.plugins.get_node("Atom")
        Point = context.application.plugins.get_node("Point")
        for child in cache.children:
            if isinstance(child, Atom):
                l.append((-child.extra.get("index", -1), child.number, child))
            elif isinstance(child, Point):
                l.append((-child.extra.get("index", -1), 0, child))

        l.sort()
        l.reverse()

        counter = 0
        parent = cache.node
        for order, number, child in l:
            child.name = "%s" % periodic[number].symbol
            primitive.Move(child, parent, new_index=counter)
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


