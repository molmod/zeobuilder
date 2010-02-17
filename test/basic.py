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


from application_test_case import ApplicationTestCase

from zeobuilder import context
from zeobuilder.actions.composed import Parameters
from zeobuilder.expressions import Expression

from molmod import Rotation, Translation, Complete

import numpy


__all__ = ["BasicActions"]


class BasicActions(ApplicationTestCase):
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
            parameters.matrix = numpy.array([
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
            EditProperties = context.application.plugins.get_action("EditProperties")
            context.application.main.select_nodes([context.application.model.universe])
            self.assert_(EditProperties.analyze_selection())
            EditProperties()
            context.application.main.select_nodes([context.application.model.universe.children[0]])
            self.assert_(EditProperties.analyze_selection())
            EditProperties()
        self.run_test_application(fn)

    def test_edit_properties2(self):
        def fn():
            context.application.model.file_open("input/tpa.xyz")
            EditProperties = context.application.plugins.get_action("EditProperties")
            context.application.main.select_nodes([context.application.model.universe])
            self.assert_(EditProperties.analyze_selection())
            EditProperties()
            context.application.main.select_nodes([context.application.model.universe.children[0]])
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
            parameters.rotation = Rotation.from_properties(1.0, numpy.array([0.1, 1.4, 0.3]), False)
            RotateDialog = context.application.plugins.get_action("RotateDialog")
            self.assert_(RotateDialog.analyze_selection(parameters))
            RotateDialog(parameters)
        self.run_test_application(fn)

    def test_rotate_about_axis_dialog(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe.children[3], on=True)
            parameters = Parameters()
            parameters.center = Translation([2.0, 4.1, -1.0])
            parameters.rotation = Rotation.from_properties(1.0, numpy.array([0.1, 1.4, 0.3]), False)
            RotateAboutAxisDialog = context.application.plugins.get_action("RotateAboutAxisDialog")
            self.assert_(RotateAboutAxisDialog.analyze_selection(parameters))
            RotateAboutAxisDialog(parameters)
        self.run_test_application(fn)

    def test_translate_dialog(self):
        def fn():
            context.application.model.file_open("input/core_objects.zml")
            context.application.main.toggle_selection(context.application.model.universe.children[3], on=True)
            parameters = Parameters()
            parameters.translation = Translation([2.0, 4.1, -1.0])
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

    def test_unit_cell_to_cluster2(self):
        def fn():
            context.application.model.file_open("input/silica_layer.zml")
            parameters = Parameters()
            parameters.interval_a = numpy.array([0.0, 3.0], float)
            parameters.interval_b = numpy.array([0.0, 3.0], float)
            UnitCellToCluster = context.application.plugins.get_action("UnitCellToCluster")
            self.assert_(UnitCellToCluster.analyze_selection(parameters))
            UnitCellToCluster(parameters)
            crd_cluster = [node.transformation.t for node in context.application.model.universe.children]

            context.application.model.file_open("input/silica_layer.zml")
            parameters = Parameters()
            parameters.repetitions_a = 3
            parameters.repetitions_b = 3
            SuperCell = context.application.plugins.get_action("SuperCell")
            self.assert_(SuperCell.analyze_selection(parameters))
            SuperCell(parameters)
            crd_super = [node.transformation.t for node in context.application.model.universe.children]

            # check that the number of atoms is the same
            self.assertEqual(len(crd_super), len(crd_cluster))
            # check if the coordinates match
            for c_super in crd_super:
                for i in xrange(len(crd_cluster)):
                    c_cluster = crd_cluster[i]
                    delta = c_cluster - c_super
                    delta = context.application.model.universe.shortest_vector(delta)
                    if numpy.linalg.norm(delta) < 1e-3:
                        del crd_cluster[i]
                        break
            self.assertEqual(len(crd_cluster), 0)
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

    def test_super_cell_nowrap(self):
        def fn():
            context.application.model.file_open("input/silica_layer.zml")
            parameters = Parameters()
            parameters.repetitions_a = 2
            parameters.repetitions_b = 3
            SuperCell = context.application.plugins.get_action("SuperCell")
            self.assert_(SuperCell.analyze_selection(parameters))
            SuperCell(parameters)
            crd_before = [node.transformation.t for node in context.application.model.universe.children]
            WrapCellContents = context.application.plugins.get_action("WrapCellContents")
            self.assert_(WrapCellContents.analyze_selection())
            WrapCellContents()
            # coordinates should not be changed
            crd_after = [node.transformation.t for node in context.application.model.universe.children]
            for i in xrange(len(crd_after)):
                self.assertAlmostEqual(crd_before[i][0], crd_after[i][0])
                self.assertAlmostEqual(crd_before[i][1], crd_after[i][1])
                self.assertAlmostEqual(crd_before[i][2], crd_after[i][2])
        self.run_test_application(fn)

    def test_super_cell_bonds(self):
        def fn():
            context.application.model.file_open("input/silica_layer.zml")
            AutoConnectPhysical = context.application.plugins.get_action("AutoConnectPhysical")
            self.assert_(AutoConnectPhysical.analyze_selection())
            AutoConnectPhysical()
            parameters = Parameters()
            parameters.repetitions_a = 2
            parameters.repetitions_b = 3
            SuperCell = context.application.plugins.get_action("SuperCell")
            self.assert_(SuperCell.analyze_selection(parameters))
            SuperCell(parameters)
            Bond = context.application.plugins.get_node("Bond")
            for node in context.application.model.universe.children:
                if isinstance(node, Bond):
                    node.calc_vector_dimensions()
                    self.assert_(node.length < 4.0)
        self.run_test_application(fn)

    def test_define_unit_cell_vectors(self):
        def fn():
            context.application.model.file_open("input/periodic.zml")
            context.application.model.universe.cell = \
                context.application.model.universe.cell.copy_with(active=numpy.zeros(3, bool))
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
            from molmod import UnitCell
            context.application.model.file_open("input/core_objects.zml")
            unit_cell = UnitCell(numpy.identity(3, float), numpy.ones(3, bool))
            context.application.model.universe.cell = unit_cell
            WrapCellContents = context.application.plugins.get_action("WrapCellContents")
            self.assert_(WrapCellContents.analyze_selection())
            WrapCellContents()
            self.assertEqual(len(context.application.action_manager.undo_stack), 1)
            WrapCellContents() # This should not result in an effective thing to happen:
            self.assertEqual(len(context.application.action_manager.undo_stack), 1)
        self.run_test_application(fn)

    def test_wrap_cell_contents2(self):
        def fn():
            context.application.model.file_open("input/silica_layer.zml")
            crd_before = [node.transformation.t for node in context.application.model.universe.children]
            WrapCellContents = context.application.plugins.get_action("WrapCellContents")
            self.assert_(WrapCellContents.analyze_selection())
            WrapCellContents()
            # coordinates should not be changed
            crd_after = [node.transformation.t for node in context.application.model.universe.children]
            for i in xrange(len(crd_after)):
                self.assertAlmostEqual(crd_before[i][0], crd_after[i][0])
                self.assertAlmostEqual(crd_before[i][1], crd_after[i][1])
                self.assertAlmostEqual(crd_before[i][2], crd_after[i][2])
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

    def test_camera_settings(self):
        def fn():
            CameraSettings = context.application.plugins.get_action("CameraSettings")
            self.assert_(CameraSettings.analyze_selection())
            CameraSettings()
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
            import zeobuilder.actions.primitive
            from molmod import Translation

            for index in xrange(3):
                context.application.main.select_nodes([context.application.model.universe])
                Point = context.application.plugins.get_node("Point")
                point = Point(transformation=Translation(numpy.random.uniform(-1, 1, 3)))
                context.application.model.universe.add(point)

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
                Point = context.application.plugins.get_node("Point")
                point = Point(transformation=Translation(numpy.random.uniform(-5, 5, 3)))
                context.application.model.universe.add(point)

            context.application.main.select_nodes(context.application.model.universe.children)
            AddTetraeder = context.application.plugins.get_action("AddTetraeder")
            self.assert_(AddTetraeder.analyze_selection())
            AddTetraeder()
        self.run_test_application(fn)


