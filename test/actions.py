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


from application_test_case import ApplicationTestCase

from zeobuilder import context
from zeobuilder.actions.composed import Parameters
from zeobuilder.undefined import Undefined

from molmod.transformations import Rotation, Translation, Complete
from molmod.data import BOND_SINGLE
from molmod.units import from_angstrom

import gtk, numpy


__all__ = ["CoreActions", "MolecularActions", "BuilderActions"]


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
            parameters.expression = "isinstance(node, Folder)"
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
            DefineCenter = context.application.plugins.get_action("DefineCenter")
            self.assert_(DefineCenter.analyze_selection())
            DefineCenter()
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
            DefineCenterAndAlign = context.application.plugins.get_action("DefineCenterAndAlign")
            self.assert_(DefineCenterAndAlign.analyze_selection())
            DefineCenterAndAlign()
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

    def test_transformation_reset(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe.children[3], on=True)
            TransformationReset = context.application.plugins.get_action("TransformationReset")
            self.assert_(TransformationReset.analyze_selection())
            TransformationReset()
        self.run_test_application(fn)

    def test_transformation_reset(self):
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
            RotateAroundCenterDialog = context.application.plugins.get_action("RotateAroundCenterDialog")
            self.assert_(RotateAroundCenterDialog.analyze_selection(parameters))
            RotateAroundCenterDialog(parameters)
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

    def test_unit_cell_to_cluster(self):
        def fn():
            context.application.model.file_open("input/periodic.zml")
            parameters = Parameters()
            parameters.interval_b = numpy.array([0.0, 2.0], float)
            parameters.interval_c = numpy.array([0.0, 2.0], float)
            UnitCellToCluster = context.application.plugins.get_action("UnitCellToCluster")
            self.assert_(UnitCellToCluster.analyze_selection(parameters))
            UnitCellToCluster(parameters)
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

    def test_add_periodicities(self):
        def fn():
            context.application.model.file_open("input/periodic.zml")
            context.application.main.toggle_selection(context.application.model.universe.children[2], on=True)
            AddPeriodicities = context.application.plugins.get_action("AddPeriodicities")
            self.assert_(AddPeriodicities.analyze_selection())
            AddPeriodicities()
        self.run_test_application(fn)

    def test_calculate_average(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.select_nodes(context.application.model.universe.children[:2])
            CalculateAverage = context.application.plugins.get_action("CalculateAverage")
            self.assert_(CalculateAverage.analyze_selection())
            CalculateAverage()
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
            context.application.main.select_nodes([context.application.model.universe])
            parameters = Parameters()
            parameters.number1 = 6
            parameters.number2 = 6
            parameters.distance = 3.0
            parameters.bond_type = BOND_SINGLE
            AutoConnectParameters = context.application.plugins.get_action("AutoConnectParameters")
            self.assert_(AutoConnectParameters.analyze_selection(parameters))
            AutoConnectParameters(parameters)
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
            ConnectMinimizer = context.application.plugins.get_action("ConnectMinimizer")
            self.assert_(ConnectMinimizer.analyze_selection())
            ConnectMinimizer()
        self.run_test_application(fn)

    def test_auto_connect_minimizers_lau(self):
        def fn():
            context.application.model.file_open("input/lau_double.zml")
            context.application.main.select_nodes([context.application.model.universe])
            AutoConnectMinimizers = context.application.plugins.get_action("AutoConnectMinimizers")
            self.assert_(AutoConnectMinimizers.analyze_selection())
            AutoConnectMinimizers()
        self.run_test_application(fn)

    def test_minimize_distances(self):
        def fn():
            context.application.model.file_open("input/minimizers.zml")
            context.application.main.select_nodes(context.application.model.universe.children[2:])

            parameters = Parameters()
            parameters.update_interval = 0.4
            parameters.update_steps = 1
            parameters.auto_close_report_dialog = True

            MinimizeDistances = context.application.plugins.get_action("MinimizeDistances")
            self.assert_(MinimizeDistances.analyze_selection(parameters))
            MinimizeDistances(parameters)
        self.run_test_application(fn)

    def test_triangle_conscan(self):
        def fn():
            context.application.model.file_open("input/precursor.zml")
            context.application.main.select_nodes(context.application.model.universe.children)

            parameters = Parameters()
            parameters.connect_description1 = ("isinstance(node, Atom) and node.number == 8 and node.num_bonds() == 1", "node.get_radius()", "1")
            parameters.repulse_description1 = ("isinstance(node, Atom) and (node.number == 8 or node.number == 14)", "node.get_radius()", "-1")
            parameters.action_radius = from_angstrom(4)
            parameters.overlap_tolerance = from_angstrom(0.1)
            parameters.allow_inversions = True
            parameters.triangle_side_tolerance = from_angstrom(0.1)
            parameters.minimum_triangle_size = from_angstrom(0.1)
            parameters.translation_tolerance_a = from_angstrom(0.1)
            parameters.rotation_tolerance = 0.05
            parameters.rotation2 = Undefined()
            parameters.distance_tolerance = Undefined()
            parameters.translation_tolerance_b = Undefined()
            parameters.auto_close_report_dialog = True

            ScanForConnections = context.application.plugins.get_action("ScanForConnections")
            self.assert_(ScanForConnections.analyze_selection(parameters))
            ScanForConnections(parameters)
        self.run_test_application(fn)

