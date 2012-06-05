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
from zeobuilder.actions.composed import Immediate
from zeobuilder.nodes.glmixin import GLTransformationMixin
from zeobuilder.nodes.parent_mixin import ContainerMixin
from zeobuilder.nodes.analysis import common_parent
import zeobuilder.actions.primitive as primitive

from molmod import PairSearchIntra, Translation

import numpy


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
        for child in transformed_children:
            primitive.Transform(child, transformation.inv)


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
        # C) passed all tests:
        return True

    def allow_node(self, node):
        raise NotImplementedError

    def get_vector(self, node1, node2, distance):
        raise NotImplementedError

    def do(self, cutoff):
        cache = context.application.cache
        parent = cache.common_root

        def iter_translation_nodes(nodes):
            for node in nodes:
                if isinstance(node, GLTransformationMixin) and \
                   isinstance(node.transformation, Translation) and \
                   self.allow_node(node):
                    yield node
                if isinstance(node, ContainerMixin):
                    for subnode in iter_translation_nodes(node.children):
                        yield subnode

        nodes = []
        coordinates = []
        for node in iter_translation_nodes(cache.nodes_without_children):
            nodes.append(node)
            coordinates.append(node.get_frame_up_to(parent).t)
        coordinates = numpy.array(coordinates)

        unit_cell = None
        if isinstance(parent, context.application.plugins.get_node("Universe")):
            unit_cell = parent.cell

        vector_counter = 1
        for i0, i1, delta, distance in PairSearchIntra(coordinates, cutoff, unit_cell):
            vector = self.get_vector(nodes[i0], nodes[i1], distance)
            if vector is not None:
                vector.name += " %i" % vector_counter
                vector_counter += 1
                primitive.Add(vector, common_parent([nodes[i0], nodes[i1]]))


