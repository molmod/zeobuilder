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
from zeobuilder.actions.composed import ImmediateWithMemory
from zeobuilder.actions.collections.drag import DragInfo
from zeobuilder.nodes.glmixin import GLMixin, GLTransformationMixin
from zeobuilder.nodes.parent_mixin import ContainerMixin
from zeobuilder.nodes.reference import Reference
import zeobuilder.actions.primitive as primitive


class MoveObjects(ImmediateWithMemory):
    store_last_parameters = False

    def analyze_selection(parameters=None):
        # A) calling ancestor
        if not ImmediateWithMemory.analyze_selection(parameters): return False
        # B) validating and initialising
        destination = context.application.cache.drag_destination
        if not isinstance(destination, ContainerMixin): return False
        for Class in context.application.cache.classes:
            if not destination.check_add(Class): return False
        if context.application.cache.recursive_drag: return False
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)


class Move3DObjects(MoveObjects):
    description = "Drag 'n' drop transformations"
    drag_info = DragInfo(order=0)

    def analyze_selection(parameters=None):
        # A) calling ancestor
        if not MoveObjects.analyze_selection(parameters): return False
        # B) validating and initialising
        destination = context.application.cache.drag_destination
        if not isinstance(destination, GLMixin): return False
        for Class in context.application.cache.classes:
            if not issubclass(Class, GLMixin): return False
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)

    def do(self):
        node = context.application.cache.node
        destination = context.application.cache.drag_destination
        if isinstance(node, GLTransformationMixin):
            transformation = destination.get_frame_relative_to(node.parent)
            transformation.invert()
            primitive.Transform(node, transformation)
        primitive.Move(node, destination, new_index=self.parameters.child_index)


class MoveNon3DObjects(MoveObjects):
    description = "Drag 'n' drop objects"
    drag_info = DragInfo(order=1)

    def do(self):
        node = context.application.cache.node
        destination = context.application.cache.drag_destination
        primitive.Move(node, destination, new_index=self.parameters.child_index)


class DropTarget(ImmediateWithMemory):
    description = "Drop target"
    drag_info = DragInfo(order=2)
    store_last_parameters = False

    def analyze_selection(parameters=None):
        # A) calling ancestor
        if not ImmediateWithMemory.analyze_selection(parameters): return False
        # B) validating and initialising
        destination = context.application.cache.drag_destination
        if parameters.child_index != -1: return False
        if not isinstance(destination, Reference): return False
        if not destination.check_target(context.application.cache.node): return False
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)

    def do(self):
        destination = context.application.cache.drag_destination
        primitive.SetTarget(destination, context.application.cache.node)


actions = {
    "MoveNon3DObjects": MoveNon3DObjects,
    "Move3DObjects": Move3DObjects,
    "DropTarget": DropTarget,
}
