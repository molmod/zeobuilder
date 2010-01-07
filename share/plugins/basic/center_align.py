# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 - 2009 Toon Verstraelen <Toon.Verstraelen@UGent.be>, Center
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
from zeobuilder.actions.composed import Immediate
from zeobuilder.actions.abstract import CenterAlignBase
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.nodes.parent_mixin import ContainerMixin
from zeobuilder.nodes.glmixin import GLTransformationMixin
from zeobuilder.nodes.analysis import calculate_center
import zeobuilder.actions.primitive as primitive
import zeobuilder.authors as authors

from molmod import Translation, Rotation, Complete

import numpy

import copy, math


class DefineOrigin(CenterAlignBase):
    description = "Define origin"
    menu_info = MenuInfo("default/_Object:tools/_Transform:center", "_Define origin", order=(0, 4, 1, 2, 2, 0))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not CenterAlignBase.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        node = cache.node
        if not isinstance(node, GLTransformationMixin): return False
        if not isinstance(node.transformation, Translation): return False
        if cache.some_neighbors_fixed: return False
        # C) passed all tests:
        return True

    def do(self):
        cache = context.application.cache
        translation = Translation(cache.node.transformation.t)
        CenterAlignBase.do(self, cache.parent, cache.translated_neighbors, translation)


class Align(CenterAlignBase):
    description = "Align to parent"
    menu_info = MenuInfo("default/_Object:tools/_Transform:align", "_Align", order=(0, 4, 1, 2, 3, 0))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not CenterAlignBase.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        node = cache.node
        if not isinstance(node, GLTransformationMixin): return False
        if not isinstance(node.transformation, Rotation): return False
        if cache.some_neighbors_fixed: return False
        # C) passed all tests:
        return True

    def do(self):
        cache = context.application.cache
        rotation = Rotation(cache.node.transformation.r)
        CenterAlignBase.do(self, cache.parent, cache.transformed_neighbors, rotation)


class DefineOriginAndAlign(CenterAlignBase):
    description = "Define as origin and align to parent"
    menu_info = MenuInfo("default/_Object:tools/_Transform:centeralign", "De_fine origin and align", order=(0, 4, 1, 2, 4, 0))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not CenterAlignBase.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        node = cache.node
        if not isinstance(node, GLTransformationMixin): return False
        if not isinstance(node.transformation, Complete): return False
        if cache.some_neighbors_fixed: return False
        # C) passed all tests:
        return True

    def do(self):
        cache = context.application.cache
        CenterAlignBase.do(self, cache.parent, cache.transformed_neighbors, cache.node.transformation)


class CenterToChildren(CenterAlignBase):
    description = "Center to children"
    menu_info = MenuInfo("default/_Object:tools/_Transform:center", "Center to c_hildren", order=(0, 4, 1, 2, 2, 1))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not CenterAlignBase.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        if len(cache.nodes) == 0: return False
        for node in cache.nodes:
            if not isinstance(node, ContainerMixin): return False
        # C) passed all tests:
        return True

    def do(self):
        cache = context.application.cache
        for node in cache.nodes:
            child_translations = []
            translated_children = []
            for child in node.children:
                if isinstance(child, GLTransformationMixin) and isinstance(child.transformation, Translation):
                    if child.get_fixed():
                        translated_children = []
                        break
                    translated_children.append(child)
                    child_translations.append(child.transformation)
            if len(translated_children) > 0:
                translation = Translation(calculate_center(child_translations))
                CenterAlignBase.do(self, node, translated_children, translation)


class AlignUnitCell(Immediate):
    description = "Align unit cell"
    menu_info = MenuInfo("default/_Object:tools/_Transform:align", "_Align unit cell", order=(0, 4, 1, 2, 3, 1))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestors
        if not Immediate.analyze_selection(): return False
        # B) validating
        node = context.application.cache.node
        Universe = context.application.plugins.get_node("Universe")
        if not isinstance(node, Universe): return False
        if node.cell_active.sum() == 0: return False
        # C) passed all tests:
        return True

    def do(self):
        universe = context.application.cache.node
        # first make sure the cell is right handed
        if numpy.linalg.det(universe.cell.matrix) < 0 and universe.cell_active.sum() == 3:
            new_matrix = universe.cell.matrix.copy()
            temp = new_matrix[:,0].copy()
            new_matrix[:,0] = new_matrix[:,1]
            new_matrix[:,1] = temp
            new_cell = UnitCell(new_matrix, universe.cell.active)
            primitive.SetProperty(universe, "cell", new_cell)

        # then rotate the unit cell box to the normalized frame:
        rotation = Rotation(universe.calc_align_rotation_matrix())
        for child in context.application.cache.transformed_children:
            primitive.Transform(child, rotation)
        new_cell = UnitCell(numpy.dot(rotation.r, universe.cell.matrix), universe.cell.active)
        primitive.SetProperty(universe, "cell", new_cell)


actions = {
    "DefineOrigin": DefineOrigin,
    "Align": Align,
    "DefineOriginAndAlign": DefineOriginAndAlign,
    "CenterToChildren": CenterToChildren,
    "AlignUnitCell": AlignUnitCell,
}


