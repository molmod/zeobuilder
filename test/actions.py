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


from application_test_case import ApplicationTestCase

from zeobuilder import context
from zeobuilder.actions.composed import Parameters
from zeobuilder.undefined import Undefined
from zeobuilder.expressions import Expression
import zeobuilder.actions.primitive as primitive

from molmod.transformations import Rotation, Translation, Complete
from molmod.bonds import BOND_SINGLE
from molmod.units import angstrom

import gtk, numpy

import math


__all__ = [
    "CoreActions", "MolecularActions", "BuilderActions", "PrimitiveActions"
]


class CoreActions(ApplicationTestCase):
    def test_file_new(self):
        def fn():
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()
        self.run_test_application(fn)

    def test_add_box(self):
        def fn():
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()
            context.application.main.toggle_selection(context.application.model.universe, on=True)
            AddBox = context.application.plugins.get_action("AddBox")
            self.assert_(AddBox.analyze_selection())
            AddBox()
        self.run_test_application(fn)

    def test_add_frame(self):
        def fn():
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()
            context.application.main.toggle_selection(context.application.model.universe, on=True)
            AddFrame = context.application.plugins.get_action("AddFrame")
            self.assert_(AddFrame.analyze_selection())
            AddFrame()
        self.run_test_application(fn)

    def test_add_point(self):
        def fn():
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()
            context.application.main.toggle_selection(context.application.model.universe, on=True)
            AddPoint = context.application.plugins.get_action("AddPoint")
            self.assert_(AddPoint.analyze_selection())
            AddPoint()
        self.run_test_application(fn)

    def test_add_sphere(self):
        def fn():
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()
            context.application.main.toggle_selection(context.application.model.universe, on=True)
            AddSphere = context.application.plugins.get_action("AddSphere")
            self.assert_(AddSphere.analyze_selection())
            AddSphere()
        self.run_test_application(fn)

    def test_add_folder(self):
        def fn():
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()
            context.application.main.toggle_selection(context.application.model.folder, on=True)
            AddFolder = context.application.plugins.get_action("AddFolder")
            self.assert_(AddFolder.analyze_selection())
            AddFolder()
        self.run_test_application(fn)

    def test_add_notes(self):
        def fn():
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()
            context.application.main.toggle_selection(context.application.model.folder, on=True)
            AddNotes = context.application.plugins.get_action("AddNotes")
            self.assert_(AddNotes.analyze_selection())
            AddNotes()
        self.run_test_application(fn)

    def test_select_none(self):
        def fn():
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()
            context.application.main.toggle_selection(context.application.model.folder, on=True)
            SelectNone = context.application.plugins.get_action("SelectNone")
            self.assert_(SelectNone.analyze_selection())
            SelectNone()
        self.run_test_application(fn)

    def test_select_targets(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe.children[2].children[0], on=True)
            context.application.main.toggle_selection(context.application.model.universe.children[2].children[1], on=True)
            SelectTargets = context.application.plugins.get_action("SelectTargets")
            self.assert_(SelectTargets.analyze_selection())
            SelectTargets()
        self.run_test_application(fn)

    def test_select_parents(self):
        def fn():
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()
            context.application.main.toggle_selection(context.application.model.folder, on=True)
            AddFolder = context.application.plugins.get_action("AddFolder")
            self.assert_(AddFolder.analyze_selection())
            AddFolder()
            context.application.main.toggle_selection(context.application.model.folder, on=False)
            context.application.main.toggle_selection(context.application.model.folder.children[0], on=True)
            SelectParents = context.application.plugins.get_action("SelectParents")
            self.assert_(SelectParents.analyze_selection())
            SelectParents()
        self.run_test_application(fn)

    def test_select_children(self):
        def fn():
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()
            context.application.main.select_nodes([context.application.model.folder])
            AddFolder = context.application.plugins.get_action("AddFolder")
            self.assert_(AddFolder.analyze_selection())
            AddFolder()
            context.application.main.select_nodes([context.application.model.folder])
            SelectChildren = context.application.plugins.get_action("SelectChildren")
            self.assert_(SelectChildren.analyze_selection())
            SelectChildren()
        self.run_test_application(fn)

    def test_select_children_by_expression(self):
        def fn():
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()
            context.application.main.select_nodes([context.application.model.folder])
            AddFolder = context.application.plugins.get_action("AddFolder")
            self.assert_(AddFolder.analyze_selection())
            AddFolder()
            context.application.main.select_nodes([context.application.model.folder])
            AddNotes = context.application.plugins.get_action("AddNotes")
            self.assert_(AddNotes.analyze_selection())
            AddNotes()
            context.application.main.select_nodes([context.application.model.folder])
            SelectChildrenByExpression = context.application.plugins.get_action("SelectChildrenByExpression")
            parameters = Parameters()
            parameters.recursive = SelectChildrenByExpression.SELECT_PLAIN
            parameters.expression = Expression("isinstance(node, Folder)")
            self.assert_(SelectChildrenByExpression.analyze_selection(parameters))
            SelectChildrenByExpression(parameters)
            self.assert_(context.application.model.folder.children[0].selected, "First node should be selected.")
            self.assert_(not context.application.model.folder.children[1].selected, "Second node should not be selected.")
        self.run_test_application(fn)

    def test_save_selection(self):
        def fn():
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()
            context.application.main.toggle_selection(context.application.model.folder, on=True)
            AddFolder = context.application.plugins.get_action("AddFolder")
            self.assert_(AddFolder.analyze_selection())
            AddFolder()
            context.application.main.toggle_selection(context.application.model.folder, on=False)
            context.application.main.toggle_selection(context.application.model.folder.children[0], on=True)
            SaveSelection = context.application.plugins.get_action("SaveSelection")
            self.assert_(SaveSelection.analyze_selection())
            SaveSelection()
            self.assert_(context.application.model.folder.children[0] == context.application.model.folder.children[1].children[0].target, "Wrong saved selection")
        self.run_test_application(fn)

    def test_restore_selection(self):
        def fn():
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()
            context.application.main.toggle_selection(context.application.model.folder, on=True)
            AddFolder = context.application.plugins.get_action("AddFolder")
            self.assert_(AddFolder.analyze_selection())
            AddFolder()
            context.application.main.toggle_selection(context.application.model.folder, on=False)
            context.application.main.toggle_selection(context.application.model.folder.children[0], on=True)
            SaveSelection = context.application.plugins.get_action("SaveSelection")
            self.assert_(SaveSelection.analyze_selection())
            SaveSelection()
            context.application.main.toggle_selection(context.application.model.folder.children[0], on=False)
            context.application.main.toggle_selection(context.application.model.folder.children[1], on=True)
            RestoreSavedSelection = context.application.plugins.get_action("RestoreSavedSelection")
            self.assert_(RestoreSavedSelection.analyze_selection())
            RestoreSavedSelection()
            self.assert_(context.application.model.folder.children[0].selected, "First node should be selected.")
            self.assert_(not context.application.model.folder.children[1].selected, "Second node should not be selected.")
        self.run_test_application(fn)

    def test_group_in_folder(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.folder.children[0], on=False)
            context.application.main.toggle_selection(context.application.model.folder.children[1], on=True)
            GroupInFolder = context.application.plugins.get_action("GroupInFolder")
            self.assert_(GroupInFolder.analyze_selection())
            GroupInFolder()
        self.run_test_application(fn)

    def test_frame(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe.children[0], on=False)
            context.application.main.toggle_selection(context.application.model.universe.children[1], on=True)
            Frame = context.application.plugins.get_action("Frame")
            self.assert_(Frame.analyze_selection())
            Frame()
        self.run_test_application(fn)

    def test_ungroup(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.folder.children[1], on=True)
            Ungroup = context.application.plugins.get_action("Ungroup")
            self.assert_(Ungroup.analyze_selection())
            Ungroup()
        self.run_test_application(fn)

    def test_unframe_relative(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe.children[3], on=True)
            UnframeRelative = context.application.plugins.get_action("UnframeRelative")
            self.assert_(UnframeRelative.analyze_selection())
            UnframeRelative()
        self.run_test_application(fn)

    def test_unframe_absolute(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe.children[3], on=True)
            UnframeAbsolute = context.application.plugins.get_action("UnframeAbsolute")
            self.assert_(UnframeAbsolute.analyze_selection())
            UnframeAbsolute()
        self.run_test_application(fn)

    def test_one_level_higher_relative(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe.children[3].children[0], on=True)
            OneLevelHigherRelative = context.application.plugins.get_action("OneLevelHigherRelative")
            self.assert_(OneLevelHigherRelative.analyze_selection())
            OneLevelHigherRelative()
        self.run_test_application(fn)

    def test_one_level_higher_absolute(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe.children[3].children[0], on=True)
            OneLevelHigherAbsolute = context.application.plugins.get_action("OneLevelHigherAbsolute")
            self.assert_(OneLevelHigherAbsolute.analyze_selection())
            OneLevelHigherAbsolute()
        self.run_test_application(fn)

    def test_swap_vector(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe.children[2], on=True)
            SwapVector = context.application.plugins.get_action("SwapVector")
            self.assert_(SwapVector.analyze_selection())
            SwapVector()
        self.run_test_application(fn)

    def test_connect_arrow(self):
        def fn():
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()
            context.application.main.select_nodes([context.application.model.universe])
            AddPoint = context.application.plugins.get_action("AddPoint")
            self.assert_(AddPoint.analyze_selection())
            AddPoint()
            context.application.main.select_nodes([context.application.model.universe])
            AddPoint = context.application.plugins.get_action("AddPoint")
            self.assert_(AddPoint.analyze_selection())
            AddPoint()
            context.application.main.select_nodes(context.application.model.universe.children)
            #context.application.model.universe.children[1].transformation.t = numpy.array([1.0, 0.0, 0.0], float)
            ConnectArrow = context.application.plugins.get_action("ConnectArrow")
            self.assert_(ConnectArrow.analyze_selection())
            ConnectArrow()
        self.run_test_application(fn)

    def test_define_center(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe.children[0], on=True)
            DefineOrigin = context.application.plugins.get_action("DefineOrigin")
            self.assert_(DefineOrigin.analyze_selection())
            DefineOrigin()
        self.run_test_application(fn)

    def test_align(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe.children[0], on=True)
            Align = context.application.plugins.get_action("Align")
            self.assert_(Align.analyze_selection())
            Align()
        self.run_test_application(fn)

    def test_define_center_and_align(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe.children[0], on=True)
            DefineOriginAndAlign = context.application.plugins.get_action("DefineOriginAndAlign")
            self.assert_(DefineOriginAndAlign.analyze_selection())
            DefineOriginAndAlign()
        self.run_test_application(fn)

    def test_center_to_children(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe, on=True)
            CenterToChildren = context.application.plugins.get_action("CenterToChildren")
            self.assert_(CenterToChildren.analyze_selection())
            CenterToChildren()
        self.run_test_application(fn)

    def test_align_unit_cell(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe, on=True)
            AlignUnitCell = context.application.plugins.get_action("AlignUnitCell")
            self.assert_(AlignUnitCell.analyze_selection())
            AlignUnitCell()
        self.run_test_application(fn)

    def test_scale_unit_cell(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe, on=True)
            ScaleUnitCell = context.application.plugins.get_action("ScaleUnitCell")
            self.assert_(ScaleUnitCell.analyze_selection())
            parameters = Parameters()
            parameters.cell = numpy.array([
                [1.0, 0.0, 0.0],
                [0.0, 2.0, 0.0],
                [0.0, 0.0, 3.0],
            ])
            ScaleUnitCell(parameters)
        self.run_test_application(fn)

    def test_move_3d_objects(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe.children[0], on=True)
            context.application.cache.drag_destination = context.application.model.universe
            parameters = Parameters()
            parameters.child_index = 3
            Move3DObjects = context.application.plugins.get_action("Move3DObjects")
            self.assert_(Move3DObjects.analyze_selection(parameters))
            Move3DObjects(parameters)
        self.run_test_application(fn)

    def test_move_3d_objects(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.folder.children[0], on=True)
            context.application.cache.drag_destination = context.application.model.folder
            parameters = Parameters()
            parameters.child_index = 2
            MoveNon3DObjects = context.application.plugins.get_action("MoveNon3DObjects")
            self.assert_(MoveNon3DObjects.analyze_selection(parameters))
            MoveNon3DObjects(parameters)
        self.run_test_application(fn)

    def test_drop_target(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe.children[3], on=True)
            context.application.cache.drag_destination = context.application.model.universe.children[2].children[0]
            DropTarget = context.application.plugins.get_action("DropTarget")
            parameters = Parameters()
            parameters.child_index = -1
            self.assert_(DropTarget.analyze_selection(parameters))
            DropTarget(parameters)
        self.run_test_application(fn)

    def test_undo_redo(self):
        def fn():
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()
            context.application.main.toggle_selection(context.application.model.universe, on=True)
            AddPoint = context.application.plugins.get_action("AddPoint")
            self.assert_(AddPoint.analyze_selection())
            AddPoint()
            Undo = context.application.plugins.get_action("Undo")
            self.assert_(Undo.analyze_selection())
            Undo()
            Redo = context.application.plugins.get_action("Redo")
            self.assert_(Redo.analyze_selection())
            Redo()
        self.run_test_application(fn)

    def test_repeat(self):
        def fn():
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()
            context.application.main.select_nodes([context.application.model.universe])
            AddPoint = context.application.plugins.get_action("AddPoint")
            self.assert_(AddPoint.analyze_selection())
            AddPoint()
            context.application.main.select_nodes([context.application.model.universe])
            Repeat = context.application.plugins.get_action("Repeat")
            self.assert_(Repeat.analyze_selection())
            Repeat()
        self.run_test_application(fn)

    def test_cut_paste(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe.children[0], on=True)
            context.application.main.toggle_selection(context.application.model.universe.children[1], on=True)
            Cut = context.application.plugins.get_action("Cut")
            self.assert_(Cut.analyze_selection())
            Cut()
            context.application.main.toggle_selection(context.application.model.universe, on=True)
            Paste = context.application.plugins.get_action("Paste")
            self.assert_(Paste.analyze_selection())
            Paste()
        self.run_test_application(fn)

    def test_copy_paste(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe.children[0], on=True)
            context.application.main.toggle_selection(context.application.model.universe.children[1], on=True)
            Copy = context.application.plugins.get_action("Copy")
            self.assert_(Copy.analyze_selection())
            Copy()
            # It can take some time before the clipboard actually knows that
            # it has recieved something through the Copy() action.
            import time
            time.sleep(1)
            context.application.main.toggle_selection(context.application.model.universe.children[0], on=False)
            context.application.main.toggle_selection(context.application.model.universe.children[1], on=False)
            context.application.main.toggle_selection(context.application.model.universe, on=True)
            Paste = context.application.plugins.get_action("Paste")
            self.assert_(Paste.analyze_selection())
            Paste()
        self.run_test_application(fn)

    def test_copy_empty_references(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe.children[2], on=True)
            Copy = context.application.plugins.get_action("Copy")
            self.assert_(Copy.analyze_selection())
            Copy()
            context.application.main.toggle_selection(context.application.model.universe.children[2], on=False)
            context.application.main.toggle_selection(context.application.model.universe, on=True)
            Paste = context.application.plugins.get_action("Paste")
            self.assert_(not Paste.analyze_selection())
        self.run_test_application(fn)

    def test_delete(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe.children[0], on=True)
            Delete = context.application.plugins.get_action("Delete")
            self.assert_(Delete.analyze_selection())
            Delete()
        self.run_test_application(fn)

    def test_duplicate(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe.children[1], on=True)
            Duplicate = context.application.plugins.get_action("Duplicate")
            self.assert_(Duplicate.analyze_selection())
            Duplicate()
        self.run_test_application(fn)

    def test_edit_properties(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe, on=True)
            EditProperties = context.application.plugins.get_action("EditProperties")
            self.assert_(EditProperties.analyze_selection())
            EditProperties()
        self.run_test_application(fn)

    def test_transformation_reset(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe.children[3], on=True)
            TransformationReset = context.application.plugins.get_action("TransformationReset")
            self.assert_(TransformationReset.analyze_selection())
            TransformationReset()
        self.run_test_application(fn)

    def test_transformation_invert(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe.children[3], on=True)
            TransformationInvert = context.application.plugins.get_action("TransformationInvert")
            self.assert_(TransformationInvert.analyze_selection())
            TransformationInvert()
        self.run_test_application(fn)

    def test_rotate_dialog(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe.children[3], on=True)
            parameters = Parameters()
            parameters.rotation = Rotation()
            parameters.rotation.set_rotation_properties(1.0, numpy.array([0.1, 1.4, 0.3]), False)
            RotateDialog = context.application.plugins.get_action("RotateDialog")
            self.assert_(RotateDialog.analyze_selection(parameters))
            RotateDialog(parameters)
        self.run_test_application(fn)

    def test_rotate_around_center_dialog(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe.children[3], on=True)
            parameters = Parameters()
            parameters.complete = Complete()
            parameters.complete.set_rotation_properties(1.0, numpy.array([0.1, 1.4, 0.3]), False)
            parameters.complete = Translation()
            parameters.complete.t = numpy.array([2.0, 4.1, -1.0], float)
            RotateAboutAxisDialog = context.application.plugins.get_action("RotateAboutAxisDialog")
            self.assert_(RotateAboutAxisDialog.analyze_selection(parameters))
            RotateAboutAxisDialog(parameters)
        self.run_test_application(fn)

    def test_translate_dialog(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe.children[3], on=True)
            parameters = Parameters()
            parameters.translation = Translation()
            parameters.translation.t = numpy.array([2.0, 4.1, -1.0], float)
            TranslateDialog = context.application.plugins.get_action("TranslateDialog")
            self.assert_(TranslateDialog.analyze_selection(parameters))
            TranslateDialog(parameters)
        self.run_test_application(fn)

    def test_reflection_dialog(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe.children[3], on=True)
            parameters = Parameters()
            parameters.center = numpy.array([1.0, 0.2, -0.9], float)
            parameters.normal = numpy.array([2.0, 4.1, -1.0], float)
            ReflectionDialog = context.application.plugins.get_action("ReflectionDialog")
            self.assert_(ReflectionDialog.analyze_selection(parameters))
            ReflectionDialog(parameters)
        self.run_test_application(fn)

    def test_unit_cell_to_cluster(self):
        def fn():
            context.application.model.file_open("input/sod.zml")
            parameters = Parameters()
            parameters.interval_b = numpy.array([-0.5, 2.5], float)
            parameters.interval_c = numpy.array([-1.5, 1.5], float)
            UnitCellToCluster = context.application.plugins.get_action("UnitCellToCluster")
            self.assert_(UnitCellToCluster.analyze_selection(parameters))
            UnitCellToCluster(parameters)
            # check the bond lengths
            Bond = context.application.plugins.get_node("Bond")
            universe = context.application.model.universe
            for bond in context.application.model.universe.children:
                if isinstance(bond, Bond):
                    delta = bond.children[0].target.transformation.t - bond.children[1].target.transformation.t
                    delta = universe.shortest_vector(delta)
                    distance = numpy.linalg.norm(delta)
                    self.assert_(distance < 4.0, "Incorrect bonds detected.")
        self.run_test_application(fn)

    def test_super_cell(self):
        def fn():
            context.application.model.file_open("input/periodic.zml")
            parameters = Parameters()
            parameters.repetitions_b = 2
            parameters.repetitions_c = 3
            SuperCell = context.application.plugins.get_action("SuperCell")
            self.assert_(SuperCell.analyze_selection(parameters))
            SuperCell(parameters)
        self.run_test_application(fn)

    def test_define_unit_cell_vectors(self):
        def fn():
            context.application.model.file_open("input/periodic.zml")
            context.application.model.universe.cell_active[:] = False
            context.application.main.select_nodes([
                context.application.model.universe.children[2],
                context.application.model.universe.children[4],
                context.application.model.universe.children[7],
            ])
            DefineUnitCellVectors = context.application.plugins.get_action("DefineUnitCellVectors")
            self.assert_(DefineUnitCellVectors.analyze_selection())
            DefineUnitCellVectors()
        self.run_test_application(fn)

    def test_wrap_cell_contents(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.model.universe.cell_active[:] = True
            WrapCellContents = context.application.plugins.get_action("WrapCellContents")
            self.assert_(WrapCellContents.analyze_selection())
            WrapCellContents()
            self.assertEqual(len(context.application.action_manager.undo_stack), 1)
            WrapCellContents() # This should not result in an effective thing to happen:
            self.assertEqual(len(context.application.action_manager.undo_stack), 1)
        self.run_test_application(fn)

    def test_calculate_average(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.select_nodes(context.application.model.universe.children[:2])
            CalculateAverage = context.application.plugins.get_action("CalculateAverage")
            self.assert_(CalculateAverage.analyze_selection())
            CalculateAverage()
        self.run_test_application(fn)

    def test_view_plugins(self):
        def fn():
            ViewPlugins = context.application.plugins.get_action("ViewPlugins")
            self.assert_(ViewPlugins.analyze_selection())
            ViewPlugins()
        self.run_test_application(fn)

    def test_about(self):
        def fn():
            About = context.application.plugins.get_action("About")
            self.assert_(About.analyze_selection())
            About()
        self.run_test_application(fn)

    def test_add_plane(self):
        def fn():
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()

            for index in xrange(3):
                context.application.main.select_nodes([context.application.model.universe])
                AddPoint = context.application.plugins.get_action("AddPoint")
                self.assert_(AddPoint.analyze_selection())
                AddPoint()
                context.application.model.universe.children[-1].transformation.t = numpy.random.uniform(-1, 1, 3)

            context.application.main.select_nodes(context.application.model.universe.children)
            AddPlane = context.application.plugins.get_action("AddPlane")
            self.assert_(AddPlane.analyze_selection())
            AddPlane()
        self.run_test_application(fn)

    def test_add_tetraeder(self):
        def fn():
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()

            for index in xrange(4):
                context.application.main.select_nodes([context.application.model.universe])
                AddPoint = context.application.plugins.get_action("AddPoint")
                self.assert_(AddPoint.analyze_selection())
                AddPoint()
                context.application.model.universe.children[-1].transformation.t = numpy.random.uniform(-5, 5, 3)

            context.application.main.select_nodes(context.application.model.universe.children)
            AddTetraeder = context.application.plugins.get_action("AddTetraeder")
            self.assert_(AddTetraeder.analyze_selection())
            AddTetraeder()
        self.run_test_application(fn)


class MolecularActions(ApplicationTestCase):
    def test_add_atom(self):
        def fn():
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()
            context.application.main.select_nodes([context.application.model.universe])
            AddAtom = context.application.plugins.get_action("AddAtom")
            self.assert_(AddAtom.analyze_selection())
            AddAtom()
        self.run_test_application(fn)

    def test_connect_single_bond(self):
        def fn():
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()
            context.application.main.select_nodes([context.application.model.universe])
            AddAtom = context.application.plugins.get_action("AddAtom")
            self.assert_(AddAtom.analyze_selection())
            AddAtom()
            context.application.main.select_nodes([context.application.model.universe])
            AddAtom = context.application.plugins.get_action("AddAtom")
            self.assert_(AddAtom.analyze_selection())
            AddAtom()
            context.application.main.select_nodes(context.application.model.universe.children)
            ConnectSingleBond = context.application.plugins.get_action("ConnectSingleBond")
            self.assert_(ConnectSingleBond.analyze_selection())
            ConnectSingleBond()
        self.run_test_application(fn)

    def test_connect_double_bond(self):
        def fn():
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()
            context.application.main.select_nodes([context.application.model.universe])
            AddAtom = context.application.plugins.get_action("AddAtom")
            self.assert_(AddAtom.analyze_selection())
            AddAtom()
            context.application.main.select_nodes([context.application.model.universe])
            AddAtom = context.application.plugins.get_action("AddAtom")
            self.assert_(AddAtom.analyze_selection())
            AddAtom()
            context.application.main.select_nodes(context.application.model.universe.children)
            ConnectDoubleBond = context.application.plugins.get_action("ConnectDoubleBond")
            self.assert_(ConnectDoubleBond.analyze_selection())
            ConnectDoubleBond()
        self.run_test_application(fn)

    def test_connect_triple_bond(self):
        def fn():
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()
            context.application.main.select_nodes([context.application.model.universe])
            AddAtom = context.application.plugins.get_action("AddAtom")
            self.assert_(AddAtom.analyze_selection())
            AddAtom()
            context.application.main.select_nodes([context.application.model.universe])
            AddAtom = context.application.plugins.get_action("AddAtom")
            self.assert_(AddAtom.analyze_selection())
            AddAtom()
            context.application.main.select_nodes(context.application.model.universe.children)
            ConnectTripleBond = context.application.plugins.get_action("ConnectTripleBond")
            self.assert_(ConnectTripleBond.analyze_selection())
            ConnectTripleBond()
        self.run_test_application(fn)

    def test_auto_connect_physical_tpa(self):
        def fn():
            context.application.model.file_open("input/tpa.zml")
            context.application.main.select_nodes([context.application.model.universe])
            AutoConnectPhysical = context.application.plugins.get_action("AutoConnectPhysical")
            self.assert_(AutoConnectPhysical.analyze_selection())
            AutoConnectPhysical()
        self.run_test_application(fn)

    def test_auto_connect_physical_lau(self):
        def fn():
            context.application.model.file_open("input/lau.zml")
            context.application.main.select_nodes([context.application.model.universe])
            AutoConnectPhysical = context.application.plugins.get_action("AutoConnectPhysical")
            self.assert_(AutoConnectPhysical.analyze_selection())
            AutoConnectPhysical()
        self.run_test_application(fn)

    def test_auto_connect_parameters_tpa(self):
        def fn():
            context.application.model.file_open("input/tpa.zml")
            universe = context.application.model.universe
            context.application.main.select_nodes([universe])
            parameters = Parameters()
            parameters.number1 = 6
            parameters.number2 = 6
            parameters.distance = 3.0
            parameters.bond_type = BOND_SINGLE
            AutoConnectParameters = context.application.plugins.get_action("AutoConnectParameters")
            self.assert_(AutoConnectParameters.analyze_selection(parameters))
            AutoConnectParameters(parameters)

            Bond = context.application.plugins.get_node("Bond")
            num_bonds = sum(isinstance(node,Bond) for node in universe.children)
            self.assertEqual(num_bonds,2*4)
        self.run_test_application(fn)

    def test_auto_connect_parameters_tpa2(self):
        def fn():
            context.application.model.file_open("input/tpa.zml")
            universe = context.application.model.universe
            context.application.main.select_nodes([universe] + universe.children)
            parameters = Parameters()
            parameters.number1 = 6
            parameters.number2 = 6
            parameters.distance = 3.0
            parameters.bond_type = BOND_SINGLE
            AutoConnectParameters = context.application.plugins.get_action("AutoConnectParameters")
            self.assert_(AutoConnectParameters.analyze_selection(parameters))
            AutoConnectParameters(parameters)

            Bond = context.application.plugins.get_node("Bond")
            num_bonds = sum(isinstance(node,Bond) for node in universe.children)
            self.assertEqual(num_bonds,2*4)
        self.run_test_application(fn)

    def test_auto_connect_parameters_lau(self):
        def fn():
            context.application.model.file_open("input/lau.zml")
            context.application.main.select_nodes([context.application.model.universe])
            parameters = Parameters()
            parameters.number1 = 14
            parameters.number2 = 14
            parameters.distance = 6.0
            parameters.bond_type = BOND_SINGLE
            AutoConnectParameters = context.application.plugins.get_action("AutoConnectParameters")
            self.assert_(AutoConnectParameters.analyze_selection(parameters))
            AutoConnectParameters(parameters)
        self.run_test_application(fn)

    def test_merge_overlapping_atoms_lau(self):
        def fn():
            context.application.model.file_open("input/lau_double.zml")
            context.application.main.select_nodes([context.application.model.universe])
            MergeOverlappingAtoms = context.application.plugins.get_action("MergeOverlappingAtoms")
            self.assert_(MergeOverlappingAtoms.analyze_selection())
            MergeOverlappingAtoms()
        self.run_test_application(fn)

    def test_center_of_mass(self):
        def fn():
            context.application.model.file_open("input/tpa.zml")
            context.application.main.select_nodes([context.application.model.universe])
            CenterOfMass = context.application.plugins.get_action("CenterOfMass")
            self.assert_(CenterOfMass.analyze_selection())
            CenterOfMass()
        self.run_test_application(fn)

    def test_center_of_mass_and_principal_axes(self):
        def fn():
            context.application.model.file_open("input/tpa.zml")
            context.application.main.select_nodes([context.application.model.universe])
            CenterOfMassAndPrincipalAxes = context.application.plugins.get_action("CenterOfMassAndPrincipalAxes")
            self.assert_(CenterOfMassAndPrincipalAxes.analyze_selection())
            CenterOfMassAndPrincipalAxes()
        self.run_test_application(fn)

    def test_rearrange_atoms(self):
        def fn():
            context.application.model.file_open("input/tpa.zml")
            context.application.main.select_nodes([context.application.model.universe])
            RearrangeAtoms = context.application.plugins.get_action("RearrangeAtoms")
            self.assert_(RearrangeAtoms.analyze_selection())
            RearrangeAtoms()
        self.run_test_application(fn)

    def test_saturate_with_hydrogens_tpa(self):
        def fn():
            context.application.model.file_open("input/tpa.zml")
            Atom = context.application.plugins.get_node("Atom")
            for child in context.application.model.universe.children[::-1]:
                if isinstance(child, Atom) and child.number == 1:
                    context.application.model.universe.children.remove(child)
            context.application.main.select_nodes([context.application.model.universe])
            AutoConnectPhysical = context.application.plugins.get_action("AutoConnectPhysical")
            self.assert_(AutoConnectPhysical.analyze_selection())
            AutoConnectPhysical()
            context.application.main.select_nodes([context.application.model.universe])
            SaturateWithHydrogens = context.application.plugins.get_action("SaturateWithHydrogens")
            self.assert_(SaturateWithHydrogens.analyze_selection())
            SaturateWithHydrogens()
        self.run_test_application(fn)

    def test_saturate_with_hydrogens_manual_tpa(self):
        def fn():
            context.application.model.file_open("input/tpa.xyz")
            Atom = context.application.plugins.get_node("Atom")
            for child in context.application.model.universe.children[::-1]:
                if isinstance(child, Atom) and child.number == 1:
                    context.application.model.universe.children.remove(child)
            context.application.main.select_nodes([context.application.model.universe])
            AutoConnectPhysical = context.application.plugins.get_action("AutoConnectPhysical")
            self.assert_(AutoConnectPhysical.analyze_selection())
            AutoConnectPhysical()

            parameters = Parameters()
            parameters.num_hydrogens = 2
            parameters.opening_angle = 1.9093

            context.application.main.select_nodes([context.application.model.universe.children[1]])
            SaturateHydrogensManual = context.application.plugins.get_action("SaturateHydrogensManual")
            self.assert_(SaturateHydrogensManual.analyze_selection(parameters))
            SaturateHydrogensManual(parameters)
        self.run_test_application(fn)

    def test_distribution_bond_lengths_precursor(self):
        def fn():
            context.application.model.file_open("input/precursor.zml")
            context.application.main.select_nodes([context.application.model.universe])

            parameters = Parameters()
            parameters.filter_atom1 = Expression()
            parameters.filter_bond12 = Expression()
            parameters.filter_atom2 = Expression()

            DistributionBondLengths = context.application.plugins.get_action("DistributionBondLengths")
            self.assert_(DistributionBondLengths.analyze_selection(parameters))
            DistributionBondLengths(parameters)
        self.run_test_application(fn)

    def test_distribution_bending_angles_precursor(self):
        def fn():
            context.application.model.file_open("input/precursor.zml")
            context.application.main.select_nodes([context.application.model.universe])

            parameters = Parameters()
            parameters.filter_atom1 = Expression()
            parameters.filter_bond12 = Expression()
            parameters.filter_atom2 = Expression("atom.number==8")
            parameters.filter_bond23 = Expression()
            parameters.filter_atom3 = Expression()

            DistributionBendingAngles = context.application.plugins.get_action("DistributionBendingAngles")
            self.assert_(DistributionBendingAngles.analyze_selection(parameters))
            DistributionBendingAngles(parameters)
        self.run_test_application(fn)

    def test_distribution_dihedral_angles_precursor(self):
        def fn():
            context.application.model.file_open("input/precursor.zml")
            context.application.main.select_nodes([context.application.model.universe])

            parameters = Parameters()
            parameters.filter_atom1 = Expression()
            parameters.filter_bond12 = Expression()
            parameters.filter_atom2 = Expression()
            parameters.filter_bond23 = Expression()
            parameters.filter_atom3 = Expression()
            parameters.filter_bond34 = Expression()
            parameters.filter_atom4 = Expression()

            DistributionDihedralAngles = context.application.plugins.get_action("DistributionDihedralAngles")
            self.assert_(DistributionDihedralAngles.analyze_selection(parameters))
            DistributionDihedralAngles(parameters)
        self.run_test_application(fn)

    def test_molden_labels(self):
        def fn():
            context.application.model.file_open("input/precursor.zml")
            context.application.main.select_nodes(context.application.model.universe.children)

            MoldenLabels = context.application.plugins.get_action("MoldenLabels")
            self.assert_(MoldenLabels.analyze_selection())
            MoldenLabels()
        self.run_test_application(fn)

    def test_clone_order(self):
        def fn():
            context.application.model.file_open("input/springs.zml")
            context.application.main.select_nodes(context.application.model.universe.children[:2])
            CloneOrder = context.application.plugins.get_action("CloneOrder")
            self.assert_(CloneOrder.analyze_selection())
            CloneOrder()
        self.run_test_application(fn)

    def test_clone_order2(self):
        def fn():
            context.application.model.file_open("input/azaallyl_thf_mm.zml")
            context.application.main.select_nodes(context.application.model.universe.children[2:])
            CloneOrder = context.application.plugins.get_action("CloneOrder")
            self.assert_(CloneOrder.analyze_selection())
            CloneOrder()
        self.run_test_application(fn)

    def test_strong_ring_distribution(self):
        def fn():
            context.application.model.file_open("input/springs.zml")
            context.application.main.select_nodes([context.application.model.universe.children[1]])

            StrongRingDistribution = context.application.plugins.get_action("StrongRingDistribution")
            self.assert_(StrongRingDistribution.analyze_selection())
            StrongRingDistribution()
        self.run_test_application(fn)

    def test_frame_molecules(self):
        def fn():
            context.application.model.file_open("input/methane_box22_125.xyz")
            universe = context.application.model.universe

            context.application.action_manager.record_primitives = False
            primitive.SetProperty(universe, "cell", numpy.identity(3, float)*22*angstrom)
            primitive.SetProperty(universe, "cell_active", numpy.array([True, True, True], bool))

            context.application.main.select_nodes([universe])
            AutoConnectPhysical = context.application.plugins.get_action("AutoConnectPhysical")
            self.assert_(AutoConnectPhysical.analyze_selection())
            AutoConnectPhysical()

            context.application.main.select_nodes([universe])
            FrameMolecules = context.application.plugins.get_action("FrameMolecules")
            self.assert_(FrameMolecules.analyze_selection())
            FrameMolecules()

            Bond = context.application.plugins.get_node("Bond")
            for frame in universe.children:
                for bond in frame.children:
                    if isinstance(bond, Bond):
                        bond.calc_vector_dimensions()
                        self.assert_(bond.length < 2*angstrom)
        self.run_test_application(fn)

    def test_frame_molecules2(self):
        def fn():
            context.application.model.file_open("input/ethane-ethane-pos.xyz")
            universe = context.application.model.universe

            context.application.action_manager.record_primitives = False
            context.application.main.select_nodes(universe.children)

            Frame = context.application.plugins.get_action("Frame")
            self.assert_(Frame.analyze_selection())
            Frame()

            context.application.main.select_nodes(universe.children)
            AutoConnectPhysical = context.application.plugins.get_action("AutoConnectPhysical")
            self.assert_(AutoConnectPhysical.analyze_selection())
            AutoConnectPhysical()

            context.application.main.select_nodes(universe.children)
            FrameMolecules = context.application.plugins.get_action("FrameMolecules")
            self.assert_(FrameMolecules.analyze_selection())
            FrameMolecules()
        self.run_test_application(fn)

    def test_select_bonded_neighbors(self):
        def fn():
            context.application.model.file_open("input/springs.zml")
            context.application.main.select_nodes(context.application.model.universe.children[0].children[0:1])
            SelectBondedNeighbors = context.application.plugins.get_action("SelectBondedNeighbors")
            self.assert_(SelectBondedNeighbors.analyze_selection())
            SelectBondedNeighbors()
        self.run_test_application(fn)

    def test_add_zeolite_tetraeders(self):
        def fn():
            context.application.model.file_open("input/precursor.zml")
            context.application.main.select_nodes([context.application.model.universe])
            AddZeoliteTetraeders = context.application.plugins.get_action("AddZeoliteTetraeders")
            self.assert_(AddZeoliteTetraeders.analyze_selection())
            AddZeoliteTetraeders()
        self.run_test_application(fn)


class BuilderActions(ApplicationTestCase):
    def test_connect_double_bond(self):
        def fn():
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()
            context.application.main.select_nodes([context.application.model.universe])
            AddAtom = context.application.plugins.get_action("AddAtom")
            self.assert_(AddAtom.analyze_selection())
            AddAtom()
            context.application.main.select_nodes([context.application.model.universe])
            AddAtom = context.application.plugins.get_action("AddAtom")
            self.assert_(AddAtom.analyze_selection())
            AddAtom()
            context.application.main.select_nodes(context.application.model.universe.children)
            ConnectSpring = context.application.plugins.get_action("ConnectSpring")
            self.assert_(ConnectSpring.analyze_selection())
            ConnectSpring()
        self.run_test_application(fn)

    def test_auto_connect_springs_lau(self):
        def fn():
            context.application.model.file_open("input/lau_double.zml")
            context.application.main.select_nodes([context.application.model.universe])
            AutoConnectSprings = context.application.plugins.get_action("AutoConnectSprings")
            self.assert_(AutoConnectSprings.analyze_selection())
            AutoConnectSprings()
        self.run_test_application(fn)

    def test_optimize_springs(self):
        def fn():
            context.application.model.file_open("input/springs.zml")
            context.application.main.select_nodes(
                context.application.model.universe.children[2:6] +
                context.application.model.universe.children[7:9]
            )

            parameters = Parameters()
            parameters.allow_rotation = True
            parameters.update_interval = 0.4
            parameters.update_steps = 1
            parameters.auto_close_report_dialog = True

            OptimizeSprings = context.application.plugins.get_action("OptimizeSprings")
            self.assert_(OptimizeSprings.analyze_selection(parameters))
            OptimizeSprings(parameters)
        self.run_test_application(fn)

    def test_optimize_springs_translation(self):
        def fn():
            context.application.model.file_open("input/springs.zml")
            context.application.main.select_nodes(
                context.application.model.universe.children[2:6] +
                context.application.model.universe.children[7:9]
            )

            parameters = Parameters()
            parameters.allow_rotation = False
            parameters.update_interval = 0.4
            parameters.update_steps = 1
            parameters.auto_close_report_dialog = True

            OptimizeSprings = context.application.plugins.get_action("OptimizeSprings")
            self.assert_(OptimizeSprings.analyze_selection(parameters))
            OptimizeSprings(parameters)
        self.run_test_application(fn)

    def test_optimize_springs_fixed(self):
        def fn():
            context.application.model.file_open("input/springs.zml")
            context.application.main.select_nodes(
                context.application.model.universe.children[7:9][::-1] +
                context.application.model.universe.children[2:6][::-1]
            )
            parameters = Parameters()
            parameters.allow_rotation = True
            parameters.update_interval = 0.4
            parameters.update_steps = 1
            parameters.auto_close_report_dialog = True

            OptimizeSprings = context.application.plugins.get_action("OptimizeSprings")
            self.assert_(OptimizeSprings.analyze_selection(parameters))
            OptimizeSprings(parameters)
        self.run_test_application(fn)

    def test_merge_atoms_connected_with_spring(self):
        def fn():
            context.application.model.file_open("input/springs.zml")
            context.application.main.select_nodes(
                context.application.model.universe.children[2:6] +
                context.application.model.universe.children[7:9]
            )

            MergeAtomsConnectedWithSpring = context.application.plugins.get_action("MergeAtomsConnectedWithSpring")
            self.assert_(MergeAtomsConnectedWithSpring.analyze_selection())
            MergeAtomsConnectedWithSpring()
        self.run_test_application(fn)

    def test_merge_atoms_connected_with_spring2(self):
        def fn():
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()
            AddAtom = context.application.plugins.get_action("AddAtom")
            ConnectSpring = context.application.plugins.get_action("ConnectSpring")
            for i in xrange(3):
                context.application.main.select_nodes([context.application.model.universe])
                self.assert_(AddAtom.analyze_selection())
                AddAtom()
            atoms = list(context.application.model.universe.children)
            context.application.main.select_nodes([atoms[0], atoms[1]])
            self.assert_(ConnectSpring.analyze_selection())
            ConnectSpring()
            context.application.main.select_nodes([atoms[1], atoms[2]])
            self.assert_(ConnectSpring.analyze_selection())
            ConnectSpring()
            context.application.main.select_nodes([atoms[2], atoms[0]])
            self.assert_(ConnectSpring.analyze_selection())
            ConnectSpring()

            nodes = list(context.application.model.universe.children)
            springs = [node for node in nodes if node not in atoms]
            context.application.main.select_nodes(springs)
            MergeAtomsConnectedWithSpring = context.application.plugins.get_action("MergeAtomsConnectedWithSpring")
            self.assert_(MergeAtomsConnectedWithSpring.analyze_selection())
            MergeAtomsConnectedWithSpring()

            self.assertEqual(len(context.application.model.universe.children), 1)
        self.run_test_application(fn)

    def test_triangle_conscan(self):
        def fn():
            context.application.model.file_open("input/precursor.zml")
            context.application.main.select_nodes(context.application.model.universe.children)

            parameters = Parameters()
            parameters.connect_description1 = (
                Expression("isinstance(node, Atom) and node.number == 8 and node.num_bonds() == 1"),
                Expression("node.get_radius()"),
            )
            parameters.repulse_description1 = (
                Expression("isinstance(node, Atom) and (node.number == 8 or node.number == 14)"),
                Expression("node.get_radius()*1.5"),
            )
            parameters.action_radius = 4*angstrom
            parameters.hit_tolerance = 0.1*angstrom
            parameters.allow_inversions = True
            parameters.minimum_triangle_size = 0.1*angstrom
            parameters.rotation2 = Undefined()
            parameters.auto_close_report_dialog = True

            ScanForConnections = context.application.plugins.get_action("ScanForConnections")
            self.assert_(ScanForConnections.analyze_selection(parameters))
            ScanForConnections(parameters)

            # Try to save the result to file an open it again.
            context.application.model.file_save("output/tmp.zml")
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()
            context.application.model.file_open("output/tmp.zml")

            # Do some consistency tests on the connection scanner results:
            for quality, transformation, pairs, inverse_pairs in context.application.model.folder.children[0].get_connections():
                self.assert_(len(pairs)>=3)
                if len(inverse_pairs) > 0:
                    self.assert_(len(pairs)==len(inverse_pairs))
        self.run_test_application(fn)

    def test_pair_conscan(self):
        def fn():
            context.application.model.file_open("input/precursor.zml")
            context.application.main.select_nodes(context.application.model.universe.children)

            rotation2 = Rotation()
            rotation2.set_rotation_properties(1*math.pi, [0, 1, 0], False)

            parameters = Parameters()
            parameters.connect_description1 = (
                Expression("isinstance(node, Atom) and node.number == 8 and node.num_bonds() == 1"),
                Expression("node.get_radius()"),
            )
            parameters.repulse_description1 = (
                Expression("isinstance(node, Atom) and (node.number == 8 or node.number == 14)"),
                Expression("node.get_radius()*1.5"),
            )
            parameters.action_radius = 4*angstrom
            parameters.hit_tolerance = 0.1*angstrom
            parameters.allow_inversions = Undefined()
            parameters.minimum_triangle_size = Undefined()
            parameters.rotation2 = rotation2
            parameters.auto_close_report_dialog = True

            ScanForConnections = context.application.plugins.get_action("ScanForConnections")
            self.assert_(ScanForConnections.analyze_selection(parameters))
            ScanForConnections(parameters)

            # Try to save the result to file an open it again.
            context.application.model.file_save("output/tmp.zml")
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()
            context.application.model.file_open("output/tmp.zml")

            # Do some consistency tests on the connection scanner results:
            for quality, transformation, pairs, inverse_pairs in context.application.model.folder.children[0].get_connections():
                self.assertArraysAlmostEqual(transformation.r, rotation2.r)
                self.assert_(len(pairs)>=2)
                if len(inverse_pairs) > 0:
                    self.assert_(len(pairs)==len(inverse_pairs))

        self.run_test_application(fn)

    def test_create_tube(self):
        def fn():
            context.application.model.file_open("input/silica_layer.zml")
            parameters = Parameters()
            parameters.n = 10
            parameters.m = 4
            parameters.flat = False
            parameters.max_length = 300*angstrom
            parameters.max_error = 0.01*angstrom
            parameters.tube_length = Undefined(0.01*angstrom)
            CreateTube = context.application.plugins.get_action("CreateTube")
            self.assert_(CreateTube.analyze_selection(parameters))
            CreateTube(parameters)
        self.run_test_application(fn)


class PrimitiveActions(ApplicationTestCase):
    def test_set_extra(self):
        def fn():
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()
            universe = context.application.model.root[0]
            context.application.action_manager.record_primitives = False
            p = primitive.SetExtra(universe, "foo", "bar")
            self.assert_(universe.extra["foo"] == "bar")
            p.undo()
            self.assert_("foo" not in universe.extra)
        self.run_test_application(fn)

    def test_unset_extra(self):
        def fn():
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()
            universe = context.application.model.root[0]
            universe.extra["foo"] = "bar"
            context.application.action_manager.record_primitives = False
            p = primitive.UnsetExtra(universe, "foo")
            self.assert_("foo" not in universe.extra)
            p.undo()
            self.assert_(universe.extra["foo"] == "bar")
        self.run_test_application(fn)


