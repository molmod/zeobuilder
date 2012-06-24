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
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.nodes.elementary import GLFrameBase
from zeobuilder.nodes.glmixin import GLTransformationMixin
from zeobuilder.nodes.parent_mixin import ContainerMixin
from zeobuilder.nodes.glcontainermixin import GLContainerMixin
from zeobuilder.nodes.vector import Vector
import zeobuilder.actions.primitive as primitive
import zeobuilder.authors as authors


class GroupBase(Immediate):
    @staticmethod
    def analyze_selection(NewParentClass):
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        old_parent = cache.parent
        if old_parent is None: return False
        if not isinstance(old_parent, ContainerMixin): return False
        if not old_parent.check_add(NewParentClass): return False
        if cache.some_nodes_fixed: return False
        for Class in cache.classes:
            if not NewParentClass.check_add(Class): return False
        # C) Passed all tests
        return True

    def do(self, NewParentClass):
        cache = context.application.cache
        old_parent = cache.parent
        new_parent = NewParentClass()
        nodes = list(cache.nodes)
        primitive.Add(new_parent, old_parent, index=cache.lowest_index)
        for victim in nodes:
            primitive.Move(victim, new_parent)
        return new_parent


class GroupInFolder(GroupBase):
    description = "Group"
    menu_info = MenuInfo("default/_Object:tools/A_rrange:group", "_Group in folder", order=(0, 4, 1, 1, 0, 0))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        Folder = context.application.plugins.get_node("Folder")
        return GroupBase.analyze_selection(Folder)

    def do(self):
        Folder = context.application.plugins.get_node("Folder")
        GroupBase.do(self, Folder)


class Frame(GroupBase):
    description = "Frame"
    menu_info = MenuInfo("default/_Object:tools/A_rrange:group", "_Frame", ord("f"), order=(0, 4, 1, 1, 0, 2))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        Frame = context.application.plugins.get_node("Frame")
        return GroupBase.analyze_selection(Frame)

    def do(self):
        Frame = context.application.plugins.get_node("Frame")
        frame = GroupBase.do(self, Frame)
        context.application.main.select_nodes([frame])
        CenterOfMass = context.application.plugins.get_action("CenterOfMass")
        CenterOfMass()


class UngroupBase(Immediate):
    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        new_parent = cache.parent
        if new_parent is None: return False
        for Class in cache.classes:
            if not issubclass(Class, ContainerMixin): return False
        if cache.some_children_fixed: return False
        for Class in cache.child_classes:
            if not new_parent.check_add(Class): return False
        # C) passed all tests
        return True

    def do(self):
        cache = context.application.cache
        new_parent = cache.parent
        old_parents = list(cache.nodes)
        for old_parent in old_parents:
            old_parent_index = old_parent.get_index()
            while len(old_parent.children) > 0:
                primitive.Move(old_parent.children[-1], new_parent, old_parent_index + 1)
            primitive.Delete(old_parent)


class Ungroup(UngroupBase):
    description = "Ungroup"
    menu_info = MenuInfo("default/_Object:tools/A_rrange:group", "_Ungroup", order=(0, 4, 1, 1, 0, 1))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not UngroupBase.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        Folder = context.application.plugins.get_node("Folder")
        for Class in cache.classes:
            if not issubclass(Class, Folder): return False
        if not isinstance(cache.parent, Folder): return False
        # C) passed all tests
        return True


class UnframeRelative(UngroupBase):
    description = "Unframe (relative)"
    menu_info = MenuInfo("default/_Object:tools/A_rrange:group", "_Unframe relative", order=(0, 4, 1, 1, 0, 3))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not UngroupBase.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        Frame = context.application.plugins.get_node("Frame")
        for Class in cache.classes:
            if not issubclass(Class, Frame): return False
        if not isinstance(cache.parent, GLContainerMixin): return False
        # C) passed all tests
        return True


class UnframeAbsolute(UnframeRelative):
    description = "Unframe (absolute)"
    menu_info = MenuInfo("default/_Object:tools/A_rrange:group", "_Unframe absolute", ord("f"), accel_shift=True, order=(0, 4, 1, 1, 0, 4))
    authors = [authors.toon_verstraelen]

    def do(self):
        cache = context.application.cache
        for old_parent in cache.nodes:
            for child in old_parent.children:
                if isinstance(child, GLTransformationMixin):
                    primitive.Transform(child, old_parent.transformation)
        UnframeRelative.do(self)


class OneLevelHigherBase(Immediate):
    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        old_parent = cache.parent
        if old_parent is None: return False
        new_parent = old_parent.parent
        if new_parent is None: return False
        if cache.some_nodes_fixed: return False
        for Class in cache.classes:
            if not new_parent.check_add(Class): return False
        # C) passed all tests
        return True

    def do(self):
        cache = context.application.cache
        new_parent = cache.parent.parent
        nodes = list(cache.nodes)
        for node in nodes:
            primitive.Move(node, new_parent)


class OneLevelHigherRelative(OneLevelHigherBase):
    description = "One level higher (relative)"
    menu_info = MenuInfo("default/_Object:tools/A_rrange:level", "_One level higher (relative)", order=(0, 4, 1, 1, 1, 0))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not OneLevelHigherBase.analyze_selection(): return False
        # B) validating
        if not isinstance(context.application.cache.parent, GLFrameBase): return False
        # C) passed all tests
        return True


class OneLevelHigherAbsolute(OneLevelHigherRelative):
    description = "One level higher (relative)"
    menu_info = MenuInfo("default/_Object:tools/A_rrange:level", "_One level higher (absolute)", order=(0, 4, 1, 1, 1, 1))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not OneLevelHigherRelative.analyze_selection(): return False
        # B) validating
        if not isinstance(context.application.cache.parent.parent, GLContainerMixin): return False
        # C) passed all tests
        return True

    def do(self):
        cache = context.application.cache
        old_parent_transformation = cache.parent.transformation
        for node in cache.transformed_nodes:
            primitive.Transform(node, old_parent_transformation)
        OneLevelHigherRelative.do(self)


class SeparateFrame(Immediate):
    description = "Separate the selected frame"
    menu_info = MenuInfo("default/_Object:tools/A_rrange:single", "_Separate frame", order=(0, 4, 1, 1, 2, 0))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating & initializing
        node = context.application.cache.node
        Frame = context.application.plugins.get_node("Frame")
        if not Frame.check_add(node.__class__): return False
        if node.get_fixed(): return False
        if not isinstance(node, GLTransformationMixin): return False
        if not node.parent.check_add(Frame): return False
        # C) passed all tests:
        return True

    def do(self):
        victim = context.application.cache.node
        Frame = context.application.plugins.get_node("Frame")
        frame = Frame(name = "Frame of " + victim.name)
        primitive.Add(frame, victim.parent, index=victim.get_index())
        primitive.Transform(frame, victim.transformation)
        primitive.Move(victim, frame)
        primitive.SetProperty(victim, "transformation", victim.Transformation())


class SwapVector(Immediate):
    description = "Swap vector"
    menu_info = MenuInfo("default/_Object:tools/A_rrange:single", "_Swap vector", order=(0, 4, 1, 1, 2, 1))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        if len(cache.nodes) == 0: return False
        for Class in cache.classes:
            if not issubclass(Class, Vector): return False
        # C) passed all tests
        return True

    def do(self):
        for vector in context.application.cache.nodes:
            primitive.SetProperty(vector, "targets", vector.get_targets()[::-1])


actions = {
    "GroupInFolder": GroupInFolder,
    "Frame": Frame,
    "Ungroup": Ungroup,
    "UnframeRelative": UnframeRelative,
    "UnframeAbsolute": UnframeAbsolute,
    "OneLevelHigherRelative": OneLevelHigherRelative,
    "OneLevelHigherAbsolute": OneLevelHigherAbsolute,
    "SeparateFrame": SeparateFrame,
    "SwapVector": SwapVector,
}


