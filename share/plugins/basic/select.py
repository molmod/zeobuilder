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
from zeobuilder.actions.composed import Immediate, ImmediateWithMemory, Interactive, UserError, Parameters
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.actions.collections.interactive import InteractiveInfo, InteractiveGroup
from zeobuilder.nodes.meta import Property
from zeobuilder.nodes.parent_mixin import ParentMixin
from zeobuilder.nodes.elementary import ReferentBase
from zeobuilder.nodes.model_object import ModelObjectInfo
from zeobuilder.nodes.reference import Reference
from zeobuilder.expressions import Expression
from zeobuilder.gui.fields_dialogs import FieldsDialogSimple
import zeobuilder.gui.fields as fields
import zeobuilder.actions.primitive as primitive
import zeobuilder.authors as authors

import copy, gtk, numpy


#
# Basic Selection Operations
#

class SelectNone(Immediate):
    description = "Select none"
    menu_info = MenuInfo("default/_Select:default", "_None", order=(0, 3, 0, 0))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # C) passed all tests:
        return True

    def do(self):
        context.application.main.tree_selection.unselect_all()


class SelectTargets(Immediate):
    description = "Select targets"
    menu_info = MenuInfo("default/_Select:default", "_Targets", order=(0, 3, 0, 1))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        classes = context.application.cache.classes
        if len(classes) == 0: return False
        for Class in classes:
            if not issubclass(Class, Reference): return False
        # C) passed all tests:
        return True

    def do(self):
        references = copy.copy(context.application.cache.nodes)
        main = context.application.main
        for reference in references:
            main.toggle_selection(reference, False)
            if reference.target is not None:
                main.toggle_selection(reference.target, True)


class SelectParents(Immediate):
    description = "Select parents"
    menu_info = MenuInfo("default/_Select:default", "_Parents", 65365, False, order=(0, 3, 0, 2))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        parents = context.application.cache.parents
        if len(parents) == 0: return False
        if len(parents) == 1 and parents[0] is None: return False
        # C) passed all tests:
        return True

    def do(self):
        parents = context.application.cache.parents
        main = context.application.main
        main.tree_selection.unselect_all()
        for parent in parents:
            if parent is not None: main.toggle_selection(parent, on=True)


class SelectChildren(Immediate):
    description = "Select children"
    menu_info = MenuInfo("default/_Select:default", "_Children", 65366, False, order=(0, 3, 0, 3))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        if len(context.application.cache.children) == 0: return False
        # C) passed all tests:
        return True

    def do(self):
        context.application.main.select_nodes(context.application.cache.children)


class SelectChildrenByExpression(ImmediateWithMemory):
    description = "Select children by expression"
    menu_info = MenuInfo("default/_Select:default", "Children by _expression", order=(0, 3, 0, 4))
    authors = [authors.toon_verstraelen]

    SELECT_PLAIN = 0
    SELECT_RECURSIVE = 1
    SELECT_RECURSIVE_IF_MATCH = 2

    parameters_dialog = FieldsDialogSimple(
        "Select children by expression",
        fields.group.Table(
            fields=[
                fields.edit.ComboBox(
                    choices=[
                        (SELECT_PLAIN, "No"),
                        (SELECT_RECURSIVE, "Yes"),
                        (SELECT_RECURSIVE_IF_MATCH, "Yes if match")
                    ],
                    label_text="Recursive",
                    attribute_name="recursive",
                    show_popup=False
                ),
                fields.faulty.Expression(
                    label_text="Filter expression:",
                    attribute_name="expression",
                    show_popup=True,
                    history_name="filter",
                )
            ],
            label_text="Selection rules"
        ),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK))
    )

    @staticmethod
    def analyze_selection(parameters=None):
        # A) calling ancestor
        if not ImmediateWithMemory.analyze_selection(parameters): return False
        # B) validating
        cache = context.application.cache
        if len(cache.containers_with_children) + len(cache.referents_with_children) == 0: return False
        # C) passed all tests:
        return True

    @classmethod
    def default_parameters(cls):
        result = Parameters()
        result.expression = Expression()
        result.recursive = cls.SELECT_PLAIN
        return result

    def do(self):
        cache = context.application.cache
        parents = cache.nodes
        containers = cache.containers_with_children

        main = context.application.main

        def toggle_children(parent):
            for node in parent.children:
                match = self.parameters.expression(node)
                if match:
                    main.toggle_selection(node, on=True)
                if ((self.parameters.recursive == self.SELECT_RECURSIVE_IF_MATCH) and match) or (self.parameters.recursive == self.SELECT_RECURSIVE):
                    if isinstance(node, ParentMixin):
                        toggle_children(node)


        for parent in parents:
            main.toggle_selection(parent, on=False)
        try:
            for container in containers:
                toggle_children(container)
        except Exception:
            main.tree_selection.unselect_all()
            for parent in parents:
                main.toggle_selection(parent, on=True)
            raise UserError("An exception occured while evaluating the filter expression.")


#
# SavedSelection
#


class SavedSelection(ReferentBase):
    info = ModelObjectInfo("plugins/basic/saved_selection.svg", "RestoreSavedSelection")
    authors = [authors.toon_verstraelen]

    def set_targets(self, targets, init=False):
        self.set_children([Reference(prefix="Selected") for target in targets])
        ReferentBase.set_targets(self, targets, init)


class SaveSelection(Immediate):
    description = "Save selection"
    menu_info = MenuInfo("default/_Select:saved", "_Save selection", image_name="plugins/basic/saved_selection.svg", order=(0, 3, 1, 0))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        classes = context.application.cache.classes
        if len(classes) == 0: return False
        for Class in classes:
            if issubclass(Class, Reference): return False
        # C) passed all tests:
        return True

    def do(self):
        primitive.Add(SavedSelection(targets=context.application.cache.nodes), context.application.model.folder)


class RestoreSavedSelection(Immediate):
    description = "Restore saved selection"
    menu_info = MenuInfo("default/_Select:saved", "_Restore saved selection", order=(0, 3, 1, 1))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        for Class in context.application.cache.classes:
            if not issubclass(Class, SavedSelection): return False
        # C) passed all tests:
        return True

    def do(self):
        referents = copy.copy(context.application.cache.nodes)
        main = context.application.main
        for referent in referents:
            main.toggle_selection(referent, False)
            for reference in referent.children:
                if reference.target is not None:
                    main.toggle_selection(reference.target, True)


#
# Selection Filter
#


class EditSelectionFilter(Immediate):
    description = "Edit selection filter"
    menu_info = MenuInfo("default/_Select:preferences", "_Selection filter", order=(0, 3, 2, 0))
    authors = [authors.toon_verstraelen]

    selection_filter = FieldsDialogSimple(
        "Selection filter",
        fields.group.Table(fields=[
            fields.edit.CheckButton(
                label_text="Filter active",
                attribute_name="filter_active",
                show_popup=False,
            ),
            fields.faulty.Expression(
                label_text="Filter expression",
                attribute_name="filter_expression",
                show_popup=True,
                history_name="filter",
            )
        ]),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK))
    )

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # C) passed all tests:
        return True

    def do(self):
        self.selection_filter.run(context.application.main)


#
# Selection Picker
#


class PickSelection(Interactive):
    description = "Pick a selection"
    interactive_info = InteractiveInfo("plugins/basic/selection_picker.svg", mouse=True)
    authors = [authors.toon_verstraelen]

    def button_press(self, drawing_area, event):
        self.beginx = event.x
        self.beginy = event.y
        self.endx = event.x
        self.endy = event.y
        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
            nearest = context.application.main.drawing_area.get_nearest(event.x, event.y)
            if nearest is not None:
                context.application.action_manager.default_action(nearest)

    def button_motion(self, drawing_area, event, startbutton):
        self.endx = event.x
        self.endy = event.y
        r1 = drawing_area.screen_to_camera(numpy.array([self.beginx, self.beginy], float))
        r2 = drawing_area.screen_to_camera(numpy.array([event.x, event.y], float))
        context.application.vis_backend.tool("rectangle", r1, r2)

    def button_release(self, drawing_area, event):
        context.application.vis_backend.tool("clear")
        main = context.application.main
        if (event.button == 1):
            main.tree_selection.unselect_all()
        if abs(self.beginx - self.endx) > 1 or abs(self.beginy - self.endy) > 1:
            if self.beginx < self.endx:
                left = self.beginx
                right = self.endx
            else:
                left = self.endx
                right = self.beginx

            if self.beginy < self.endy:
                top = self.beginy
                bottom = self.endy
            else:
                top = self.endy
                bottom = self.beginy

            for hit in drawing_area.yield_hits((left, top, right, bottom)):
                main.toggle_selection(hit, event.button!=3)

        else:
            hit = drawing_area.get_nearest(event.x, event.y)
            if hit is None:
                main.tree_selection.unselect_all()
            else:
                main.toggle_selection(hit, event.button != 3)

        self.finish()


nodes = {
    "SavedSelection": SavedSelection
}

actions = {
    "SelectNone": SelectNone,
    "SelectTargets": SelectTargets,
    "SelectParents": SelectParents,
    "SelectChildren": SelectChildren,
    "SelectChildrenByExpression": SelectChildrenByExpression,
    "SaveSelection": SaveSelection,
    "RestoreSavedSelection": RestoreSavedSelection,
    "EditSelectionFilter": EditSelectionFilter,
    "PickSelection": PickSelection,
}

interactive_groups = {
    "selection": InteractiveGroup(
        image_name="plugins/basic/selection_picker.svg",
        description="Selection picker",
        initial_mask=0,
        order=0,
        authors=[authors.toon_verstraelen],
    )
}


