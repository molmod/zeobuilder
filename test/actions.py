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
from zeobuilder.transformations import Rotation, Translation, Complete

import gtk, numpy


__all__ = ["CoreActions"]


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
            context.application.main.toggle_selection(context.application.model.folder, on=True)
            AddFolder = context.application.plugins.get_action("AddFolder")
            self.assert_(AddFolder.analyze_selection())
            AddFolder()
            SelectChildren = context.application.plugins.get_action("SelectChildren")
            self.assert_(SelectChildren.analyze_selection())
            SelectChildren()
        self.run_test_application(fn)

    def test_select_children_by_expression(self):
        def fn():
            FileNew = context.application.plugins.get_action("FileNew")
            FileNew()
            context.application.main.toggle_selection(context.application.model.folder, on=True)
            AddFolder = context.application.plugins.get_action("AddFolder")
            self.assert_(AddFolder.analyze_selection())
            AddFolder()
            AddNotes = context.application.plugins.get_action("AddNotes")
            self.assert_(AddNotes.analyze_selection())
            AddNotes()
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
            context.application.main.toggle_selection(context.application.model.universe, on=True)
            AddPoint = context.application.plugins.get_action("AddPoint")
            self.assert_(AddPoint.analyze_selection())
            AddPoint()
            AddPoint = context.application.plugins.get_action("AddPoint")
            self.assert_(AddPoint.analyze_selection())
            AddPoint()
            #context.application.model.universe.children[1].transformation.translation_vector = numpy.array([1.0, 0.0, 0.0], float)
            context.application.main.toggle_selection(context.application.model.universe, on=False)
            context.application.main.toggle_selection(context.application.model.universe.children[0], on=True)
            context.application.main.toggle_selection(context.application.model.universe.children[1], on=True)
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
            context.application.main.toggle_selection(context.application.model.universe, on=True)
            AddPoint = context.application.plugins.get_action("AddPoint")
            self.assert_(AddPoint.analyze_selection())
            AddPoint()
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
            parameters.complete.translation_vector = numpy.array([2.0, 4.1, -1.0], float)
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
            parameters.translation.translation_vector = numpy.array([2.0, 4.1, -1.0], float)
            TranslateDialog = context.application.plugins.get_action("TranslateDialog")
            self.assert_(TranslateDialog.analyze_selection(parameters))
            TranslateDialog(parameters)
        self.run_test_application(fn)

    def test_unit_cell_to_cluster(self):
        def fn():
            context.application.model.file_open("input/periodic.zml")
            context.application.main.toggle_selection(context.application.model.universe, on=True)
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
            context.application.main.toggle_selection(context.application.model.universe, on=True)
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

    #def test_connect_bonds_automatically_precursor(self):
    #    from zeobuilder.actions.composed.connect.automated import ConnectAtomsAutomaticallyPhysical
    #    self.load_file("precursor_atoms.zml")
    #    self.set_input_nodes([self.application.model.root[0]])
    #    self.assert_(ConnectAtomsAutomaticallyPhysical.analyse_nodes())
    #    ConnectAtomsAutomaticallyPhysical()

    #def test_connect_bonds_automatically_mfi(self):
    #    from zeobuilder.actions.composed.connect.automated import ConnectAtomsAutomaticallyPhysical
    #    self.load_file("mfi_atoms.zml")
    #    self.set_input_nodes([self.application.model.root[0]])
    #    self.assert_(ConnectAtomsAutomaticallyPhysical.analyse_nodes())
    #    ConnectAtomsAutomaticallyPhysical()

    #def test_connect_merge_overlapping_atoms_mfi(self):
    #    from zeobuilder.actions.composed.atomic import MergeOverlappingAtoms
    #    self.load_file("mfi_atoms.zml")
    #    self.set_input_nodes([self.application.model.root[0]])
    #    self.assert_(MergeOverlappingAtoms.analyse_nodes())
    #    MergeOverlappingAtoms()

    #def test_triangular_scan_for_connections(self):
    #    from zeobuilder.actions.composed.scan import TriangularScanForConnections
    #    self.load_file("two_precursors.zml")
    #    self.set_input_nodes([self.application.model.root[0].children[0],
    #                              self.application.model.root[0].children[1]])
    #    self.assert_(TriangularScanForConnections.analyse_nodes())
    #    TriangularScanForConnections()

    #def test_planar_scan_for_connections(self):
    #    from zeobuilder.actions.composed.scan import PlanarScanForConnections
    #    self.load_file("two_precursors.zml")
    #    self.set_input_nodes([self.application.model.root[0].children[0],
    #                              self.application.model.root[0].children[1]])
    #    self.assert_(PlanarScanForConnections.analyse_nodes())
    #    PlanarScanForConnections()

    #def test_minmimize_distances(self):
    #    from zeobuilder.actions.composed.iterate import MinimizeDistances
    #    from zeobuilder.actions.composed.base import Parameters
    #    from zeobuilder.model_objects.minimiser import Minimiser
    #    self.load_file("two_precursors.zml")
    #
    #    parameters = Parameters()
    #    parameters.preconstrain = True
    #    parameters.step_size = 0.3
    #    parameters.step_convergence = 1e-7
    #    parameters.constraint_convergence = 1e-10
    #    parameters.max_num_shakes = 5
    #    parameters.update_interval = 0.4
    #
    #    self.set_input_nodes([node for node in self.application.model.root[0].children if isinstance(node, Minimiser)])
    #    MinimizeDistances.analyse_nodes(parameters)
    #    MinimizeDistances(parameters=parameters)


