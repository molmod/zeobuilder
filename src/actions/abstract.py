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
from zeobuilder.nodes.glmixin import GLMixin, GLTransformationMixin
from zeobuilder.nodes.parent_mixin import ContainerMixin
import zeobuilder.actions.primitive as primitive

import copy


__all__ = ["AddBase", "CenterAlignBase", "ConnectBase"]


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
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        if not isinstance(context.application.cache.node, GLMixin): return False
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)

    def do(self, parent, transformed_children, transformation):
        if isinstance(parent, GLTransformationMixin) and not parent.get_fixed():
            primitive.Transform(parent, transformation)
        inverse = copy.deepcopy(transformation)
        inverse.invert()
        for child in transformed_children:
            primitive.Transform(child, inverse)


class ConnectBase(Immediate):
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        if len(cache.nodes) != 2: return False
        if len(cache.translations) != 2: return False
        if cache.common_parent == None: return False
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)

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
