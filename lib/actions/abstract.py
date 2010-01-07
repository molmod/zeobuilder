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
from zeobuilder.nodes.glmixin import GLMixin, GLTransformationMixin
from zeobuilder.nodes.parent_mixin import ContainerMixin
import zeobuilder.actions.primitive as primitive

from molmod import UnitCell

import numpy

import copy


__all__ = ["AddBase", "CenterAlignBase", "ConnectBase", "AutoConnectMixin"]


class AddBase(Immediate):
    def analyze_selection(AddModelObject):
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        # first check wether the nodes parameter is ok:
        # only one node and it should accept the an AddModelObject
        node = context.application.cache.node
        if not isinstance(node, ContainerMixin): return False
        if not node.check_add(AddModelObject): return False
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)

    def do(self, AddModelObject):
        primitive.Add(AddModelObject(), context.application.cache.node)


class CenterAlignBase(Immediate):
    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # C) passed all tests:
        return True

    def do(self, parent, transformed_children, transformation):
        if isinstance(parent, GLTransformationMixin) and not parent.get_fixed():
            primitive.Transform(parent, transformation, after=False)
        inverse = copy.deepcopy(transformation)
        inverse.invert()
        for child in transformed_children:
            primitive.Transform(child, inverse)


class ConnectBase(Immediate):
    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        if len(cache.nodes) != 2: return False
        if len(cache.translations) != 2: return False
        if cache.common_parent is None: return False
        # C) passed all tests:
        return True

    def do(self):
        cache = context.application.cache
        nodes = cache.nodes
        primitive.Add(
            self.new_connector(nodes[0], nodes[1]),
            cache.common_parent,
            index=cache.highest_index + 1
        )

    def new_connector(self, begin, end):
        raise NotImplementedError


class AutoConnectMixin(object):
    @staticmethod
    def analyze_selection():
        # B) validating
        cache = context.application.cache
        if len(cache.nodes) == 0: return False
        if cache.common_root == None: return False
        # C) passed all tests:
        return True

    def allow_node(self, node):
        return isinstance(node, GLTransformationMixin) and \
            isinstance(node.transformation, Translation)

    def get_vector(self, node1, node2, distance):
        raise NotImplementedError

    def do(self, grid_size):
        cache = context.application.cache
        parent = cache.common_root
        nodes = cache.nodes_without_children

        unit_cell = None
        if isinstance(parent, UnitCell):
            unit_cell = parent

        binned_nodes = SparseBinnedObjects(
            YieldPositionedChildren(
                nodes, parent, True,
                lambda node: self.allow_node(node)
            )(),
            grid_size
        )

        def connect_nodes(positioned1, positioned2):
            delta = parent.shortest_vector(positioned2.coordinate - positioned1.coordinate)
            distance = numpy.linalg.norm(delta)
            return self.get_vector(positioned1.id, positioned2.id, distance)

        vector_counter = 1
        for (positioned1, positioned2), vector in IntraAnalyseNeighboringObjects(binned_nodes, connect_nodes)(unit_cell):
            vector.name += " %i" % vector_counter
            vector_counter += 1
            primitive.Add(vector, parent)


