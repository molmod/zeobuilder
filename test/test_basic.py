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


from common import *

from zeobuilder import context
from zeobuilder.actions.composed import Parameters
from zeobuilder.expressions import Expression
import zeobuilder.actions.primitive as primitive

from molmod import Rotation, Translation, Complete

import numpy


def test_file_new():
    def fn():
        FileNew = context.application.plugins.get_action("FileNew")
        FileNew()
    run_application(fn)

def test_add_box():
    def fn():
        FileNew = context.application.plugins.get_action("FileNew")
        FileNew()
        context.application.main.toggle_selection(context.application.model.universe, on=True)
        AddBox = context.application.plugins.get_action("AddBox")
        assert AddBox.analyze_selection()
        AddBox()
    run_application(fn)

def test_add_frame():
    def fn():
        FileNew = context.application.plugins.get_action("FileNew")
        FileNew()
        context.application.main.toggle_selection(context.application.model.universe, on=True)
        AddFrame = context.application.plugins.get_action("AddFrame")
        assert AddFrame.analyze_selection()
        AddFrame()
    run_application(fn)

def test_add_point():
    def fn():
        FileNew = context.application.plugins.get_action("FileNew")
        FileNew()
        context.application.main.toggle_selection(context.application.model.universe, on=True)
        AddPoint = context.application.plugins.get_action("AddPoint")
        assert AddPoint.analyze_selection()
        AddPoint()
    run_application(fn)

def test_add_sphere():
    def fn():
        FileNew = context.application.plugins.get_action("FileNew")
        FileNew()
        context.application.main.toggle_selection(context.application.model.universe, on=True)
        AddSphere = context.application.plugins.get_action("AddSphere")
        assert AddSphere.analyze_selection()
        AddSphere()
    run_application(fn)

def test_add_folder():
    def fn():
        FileNew = context.application.plugins.get_action("FileNew")
        FileNew()
        context.application.main.toggle_selection(context.application.model.folder, on=True)
        AddFolder = context.application.plugins.get_action("AddFolder")
        assert AddFolder.analyze_selection()
        AddFolder()
    run_application(fn)

def test_add_notes():
    def fn():
        FileNew = context.application.plugins.get_action("FileNew")
        FileNew()
        context.application.main.toggle_selection(context.application.model.folder, on=True)
        AddNotes = context.application.plugins.get_action("AddNotes")
        assert AddNotes.analyze_selection()
        AddNotes()
    run_application(fn)

def test_select_none():
    def fn():
        FileNew = context.application.plugins.get_action("FileNew")
        FileNew()
        context.application.main.toggle_selection(context.application.model.folder, on=True)
        SelectNone = context.application.plugins.get_action("SelectNone")
        assert SelectNone.analyze_selection()
        SelectNone()
    run_application(fn)

def test_select_targets():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.toggle_selection(context.application.model.universe.children[2].children[0], on=True)
        context.application.main.toggle_selection(context.application.model.universe.children[2].children[1], on=True)
        SelectTargets = context.application.plugins.get_action("SelectTargets")
        assert SelectTargets.analyze_selection()
        SelectTargets()
    run_application(fn)

def test_select_parents():
    def fn():
        FileNew = context.application.plugins.get_action("FileNew")
        FileNew()
        context.application.main.toggle_selection(context.application.model.folder, on=True)
        AddFolder = context.application.plugins.get_action("AddFolder")
        assert AddFolder.analyze_selection()
        AddFolder()
        context.application.main.toggle_selection(context.application.model.folder, on=False)
        context.application.main.toggle_selection(context.application.model.folder.children[0], on=True)
        SelectParents = context.application.plugins.get_action("SelectParents")
        assert SelectParents.analyze_selection()
        SelectParents()
    run_application(fn)

def test_select_children():
    def fn():
        FileNew = context.application.plugins.get_action("FileNew")
        FileNew()
        context.application.main.select_nodes([context.application.model.folder])
        AddFolder = context.application.plugins.get_action("AddFolder")
        assert AddFolder.analyze_selection()
        AddFolder()
        context.application.main.select_nodes([context.application.model.folder])
        SelectChildren = context.application.plugins.get_action("SelectChildren")
        assert SelectChildren.analyze_selection()
        SelectChildren()
    run_application(fn)

def test_select_children_by_expression():
    def fn():
        FileNew = context.application.plugins.get_action("FileNew")
        FileNew()
        context.application.main.select_nodes([context.application.model.folder])
        AddFolder = context.application.plugins.get_action("AddFolder")
        assert AddFolder.analyze_selection()
        AddFolder()
        context.application.main.select_nodes([context.application.model.folder])
        AddNotes = context.application.plugins.get_action("AddNotes")
        assert AddNotes.analyze_selection()
        AddNotes()
        context.application.main.select_nodes([context.application.model.folder])
        SelectChildrenByExpression = context.application.plugins.get_action("SelectChildrenByExpression")
        parameters = Parameters()
        parameters.recursive = SelectChildrenByExpression.SELECT_PLAIN
        parameters.expression = Expression("isinstance(node, Folder)")
        assert SelectChildrenByExpression.analyze_selection(parameters)
        SelectChildrenByExpression(parameters)
        assert context.application.model.folder.children[0].selected
        assert not context.application.model.folder.children[1].selected
    run_application(fn)

def test_save_selection():
    def fn():
        FileNew = context.application.plugins.get_action("FileNew")
        FileNew()
        context.application.main.toggle_selection(context.application.model.folder, on=True)
        AddFolder = context.application.plugins.get_action("AddFolder")
        assert AddFolder.analyze_selection()
        AddFolder()
        context.application.main.toggle_selection(context.application.model.folder, on=False)
        context.application.main.toggle_selection(context.application.model.folder.children[0], on=True)
        SaveSelection = context.application.plugins.get_action("SaveSelection")
        assert SaveSelection.analyze_selection()
        SaveSelection()
        assert context.application.model.folder.children[0] == context.application.model.folder.children[1].children[0].target
    run_application(fn)

def test_restore_selection():
    def fn():
        FileNew = context.application.plugins.get_action("FileNew")
        FileNew()
        context.application.main.toggle_selection(context.application.model.folder, on=True)
        AddFolder = context.application.plugins.get_action("AddFolder")
        assert AddFolder.analyze_selection()
        AddFolder()
        context.application.main.toggle_selection(context.application.model.folder, on=False)
        context.application.main.toggle_selection(context.application.model.folder.children[0], on=True)
        SaveSelection = context.application.plugins.get_action("SaveSelection")
        assert SaveSelection.analyze_selection()
        SaveSelection()
        context.application.main.toggle_selection(context.application.model.folder.children[0], on=False)
        context.application.main.toggle_selection(context.application.model.folder.children[1], on=True)
        RestoreSavedSelection = context.application.plugins.get_action("RestoreSavedSelection")
        assert RestoreSavedSelection.analyze_selection()
        RestoreSavedSelection()
        assert context.application.model.folder.children[0].selected
        assert not context.application.model.folder.children[1].selected
    run_application(fn)

def test_group_in_folder():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.toggle_selection(context.application.model.folder.children[0], on=False)
        context.application.main.toggle_selection(context.application.model.folder.children[1], on=True)
        GroupInFolder = context.application.plugins.get_action("GroupInFolder")
        assert GroupInFolder.analyze_selection()
        GroupInFolder()
    run_application(fn)

def test_frame():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.toggle_selection(context.application.model.universe.children[0], on=False)
        context.application.main.toggle_selection(context.application.model.universe.children[1], on=True)
        Frame = context.application.plugins.get_action("Frame")
        assert Frame.analyze_selection()
        Frame()
    run_application(fn)

def test_ungroup():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.toggle_selection(context.application.model.folder.children[1], on=True)
        Ungroup = context.application.plugins.get_action("Ungroup")
        assert Ungroup.analyze_selection()
        Ungroup()
    run_application(fn)

def test_unframe_relative():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.toggle_selection(context.application.model.universe.children[3], on=True)
        UnframeRelative = context.application.plugins.get_action("UnframeRelative")
        assert UnframeRelative.analyze_selection()
        UnframeRelative()
    run_application(fn)

def test_unframe_absolute():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.toggle_selection(context.application.model.universe.children[3], on=True)
        UnframeAbsolute = context.application.plugins.get_action("UnframeAbsolute")
        assert UnframeAbsolute.analyze_selection()
        UnframeAbsolute()
    run_application(fn)

def test_one_level_higher_relative():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.toggle_selection(context.application.model.universe.children[3].children[0], on=True)
        OneLevelHigherRelative = context.application.plugins.get_action("OneLevelHigherRelative")
        assert OneLevelHigherRelative.analyze_selection()
        OneLevelHigherRelative()
    run_application(fn)

def test_one_level_higher_absolute():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.toggle_selection(context.application.model.universe.children[3].children[0], on=True)
        OneLevelHigherAbsolute = context.application.plugins.get_action("OneLevelHigherAbsolute")
        assert OneLevelHigherAbsolute.analyze_selection()
        OneLevelHigherAbsolute()
    run_application(fn)

def test_swap_vector():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.toggle_selection(context.application.model.universe.children[2], on=True)
        SwapVector = context.application.plugins.get_action("SwapVector")
        assert SwapVector.analyze_selection()
        SwapVector()
    run_application(fn)

def test_connect_arrow():
    def fn():
        FileNew = context.application.plugins.get_action("FileNew")
        FileNew()
        context.application.main.select_nodes([context.application.model.universe])
        AddPoint = context.application.plugins.get_action("AddPoint")
        assert AddPoint.analyze_selection()
        AddPoint()
        context.application.main.select_nodes([context.application.model.universe])
        AddPoint = context.application.plugins.get_action("AddPoint")
        assert AddPoint.analyze_selection()
        AddPoint()
        context.application.main.select_nodes(context.application.model.universe.children)
        #context.application.model.universe.children[1].transformation.t = numpy.array([1.0, 0.0, 0.0], float)
        ConnectArrow = context.application.plugins.get_action("ConnectArrow")
        assert ConnectArrow.analyze_selection()
        ConnectArrow()
    run_application(fn)

def test_define_center():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.toggle_selection(context.application.model.universe.children[0], on=True)
        DefineOrigin = context.application.plugins.get_action("DefineOrigin")
        assert DefineOrigin.analyze_selection()
        DefineOrigin()
    run_application(fn)

def test_align():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.toggle_selection(context.application.model.universe.children[0], on=True)
        Align = context.application.plugins.get_action("Align")
        assert Align.analyze_selection()
        Align()
    run_application(fn)

def test_define_center_and_align():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.toggle_selection(context.application.model.universe.children[0], on=True)
        DefineOriginAndAlign = context.application.plugins.get_action("DefineOriginAndAlign")
        assert DefineOriginAndAlign.analyze_selection()
        DefineOriginAndAlign()
    run_application(fn)

def test_center_to_children():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.toggle_selection(context.application.model.universe, on=True)
        CenterToChildren = context.application.plugins.get_action("CenterToChildren")
        assert CenterToChildren.analyze_selection()
        CenterToChildren()
    run_application(fn)

def test_align_unit_cell():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.toggle_selection(context.application.model.universe, on=True)
        AlignUnitCell = context.application.plugins.get_action("AlignUnitCell")
        assert AlignUnitCell.analyze_selection()
        AlignUnitCell()
    run_application(fn)

def test_scale_unit_cell():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.toggle_selection(context.application.model.universe, on=True)
        ScaleUnitCell = context.application.plugins.get_action("ScaleUnitCell")
        assert ScaleUnitCell.analyze_selection()
        parameters = Parameters()
        parameters.matrix = numpy.array([
            [1.0, 0.0, 0.0],
            [0.0, 2.0, 0.0],
            [0.0, 0.0, 3.0],
        ])
        ScaleUnitCell(parameters)
    run_application(fn)

def test_move_3d_objects():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.toggle_selection(context.application.model.universe.children[0], on=True)
        context.application.cache.drag_destination = context.application.model.universe
        parameters = Parameters()
        parameters.child_index = 3
        Move3DObjects = context.application.plugins.get_action("Move3DObjects")
        assert Move3DObjects.analyze_selection(parameters)
        Move3DObjects(parameters)
    run_application(fn)

def test_move_3d_objects():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.toggle_selection(context.application.model.folder.children[0], on=True)
        context.application.cache.drag_destination = context.application.model.folder
        parameters = Parameters()
        parameters.child_index = 2
        MoveNon3DObjects = context.application.plugins.get_action("MoveNon3DObjects")
        assert MoveNon3DObjects.analyze_selection(parameters)
        MoveNon3DObjects(parameters)
    run_application(fn)

def test_drop_target():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.toggle_selection(context.application.model.universe.children[3], on=True)
        context.application.cache.drag_destination = context.application.model.universe.children[2].children[0]
        DropTarget = context.application.plugins.get_action("DropTarget")
        parameters = Parameters()
        parameters.child_index = -1
        assert DropTarget.analyze_selection(parameters)
        DropTarget(parameters)
    run_application(fn)

def test_undo_redo():
    def fn():
        FileNew = context.application.plugins.get_action("FileNew")
        FileNew()
        context.application.main.toggle_selection(context.application.model.universe, on=True)
        AddPoint = context.application.plugins.get_action("AddPoint")
        assert AddPoint.analyze_selection()
        AddPoint()
        Undo = context.application.plugins.get_action("Undo")
        assert Undo.analyze_selection()
        Undo()
        Redo = context.application.plugins.get_action("Redo")
        assert Redo.analyze_selection()
        Redo()
    run_application(fn)

def test_repeat():
    def fn():
        FileNew = context.application.plugins.get_action("FileNew")
        FileNew()
        context.application.main.select_nodes([context.application.model.universe])
        AddPoint = context.application.plugins.get_action("AddPoint")
        assert AddPoint.analyze_selection()
        AddPoint()
        context.application.main.select_nodes([context.application.model.universe])
        Repeat = context.application.plugins.get_action("Repeat")
        assert Repeat.analyze_selection()
        Repeat()
    run_application(fn)

def test_cut_paste():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.toggle_selection(context.application.model.universe.children[0], on=True)
        context.application.main.toggle_selection(context.application.model.universe.children[1], on=True)
        Cut = context.application.plugins.get_action("Cut")
        assert Cut.analyze_selection()
        Cut()
        context.application.main.toggle_selection(context.application.model.universe, on=True)
        Paste = context.application.plugins.get_action("Paste")
        assert Paste.analyze_selection()
        Paste()
    run_application(fn)

def test_copy_paste():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.toggle_selection(context.application.model.universe.children[0], on=True)
        context.application.main.toggle_selection(context.application.model.universe.children[1], on=True)
        Copy = context.application.plugins.get_action("Copy")
        assert Copy.analyze_selection()
        Copy()
        # It can take some time before the clipboard actually knows that
        # it has recieved something through the Copy() action.
        import time
        time.sleep(1)
        context.application.main.toggle_selection(context.application.model.universe.children[0], on=False)
        context.application.main.toggle_selection(context.application.model.universe.children[1], on=False)
        context.application.main.toggle_selection(context.application.model.universe, on=True)
        Paste = context.application.plugins.get_action("Paste")
        assert Paste.analyze_selection()
        Paste()
    run_application(fn)

def test_delete():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.toggle_selection(context.application.model.universe.children[0], on=True)
        Delete = context.application.plugins.get_action("Delete")
        assert Delete.analyze_selection()
        Delete()
    run_application(fn)

def test_duplicate():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.toggle_selection(context.application.model.universe.children[1], on=True)
        Duplicate = context.application.plugins.get_action("Duplicate")
        assert Duplicate.analyze_selection()
        Duplicate()
    run_application(fn)

def test_edit_properties():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        EditProperties = context.application.plugins.get_action("EditProperties")
        context.application.main.select_nodes([context.application.model.universe])
        assert EditProperties.analyze_selection()
        EditProperties()
        context.application.main.select_nodes([context.application.model.universe.children[0]])
        assert EditProperties.analyze_selection()
        EditProperties()
    run_application(fn)

def test_edit_properties2():
    def fn():
        context.application.model.file_open("test/input/tpa.xyz")
        EditProperties = context.application.plugins.get_action("EditProperties")
        context.application.main.select_nodes([context.application.model.universe])
        assert EditProperties.analyze_selection()
        EditProperties()
        context.application.main.select_nodes([context.application.model.universe.children[0]])
        assert EditProperties.analyze_selection()
        EditProperties()
    run_application(fn)

def test_transformation_reset():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.toggle_selection(context.application.model.universe.children[3], on=True)
        TransformationReset = context.application.plugins.get_action("TransformationReset")
        assert TransformationReset.analyze_selection()
        TransformationReset()
    run_application(fn)

def test_transformation_invert():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.toggle_selection(context.application.model.universe.children[3], on=True)
        TransformationInvert = context.application.plugins.get_action("TransformationInvert")
        assert TransformationInvert.analyze_selection()
        TransformationInvert()
    run_application(fn)

def test_rotate_dialog():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.toggle_selection(context.application.model.universe.children[3], on=True)
        parameters = Parameters()
        parameters.rotation = Rotation.from_properties(1.0, numpy.array([0.1, 1.4, 0.3]), False)
        RotateDialog = context.application.plugins.get_action("RotateDialog")
        assert RotateDialog.analyze_selection(parameters)
        RotateDialog(parameters)
    run_application(fn)

def test_rotate_about_axis_dialog():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.toggle_selection(context.application.model.universe.children[3], on=True)
        parameters = Parameters()
        parameters.center = Translation([2.0, 4.1, -1.0])
        parameters.rotation = Rotation.from_properties(1.0, numpy.array([0.1, 1.4, 0.3]), False)
        RotateAboutAxisDialog = context.application.plugins.get_action("RotateAboutAxisDialog")
        assert RotateAboutAxisDialog.analyze_selection(parameters)
        RotateAboutAxisDialog(parameters)
    run_application(fn)

def test_translate_dialog():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.toggle_selection(context.application.model.universe.children[3], on=True)
        parameters = Parameters()
        parameters.translation = Translation([2.0, 4.1, -1.0])
        TranslateDialog = context.application.plugins.get_action("TranslateDialog")
        assert TranslateDialog.analyze_selection(parameters)
        TranslateDialog(parameters)
    run_application(fn)

def test_reflection_dialog():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.toggle_selection(context.application.model.universe.children[3], on=True)
        parameters = Parameters()
        parameters.center = numpy.array([1.0, 0.2, -0.9], float)
        parameters.normal = numpy.array([2.0, 4.1, -1.0], float)
        ReflectionDialog = context.application.plugins.get_action("ReflectionDialog")
        assert ReflectionDialog.analyze_selection(parameters)
        ReflectionDialog(parameters)
    run_application(fn)

def test_unit_cell_to_cluster():
    def fn():
        context.application.model.file_open("test/input/sod.zml")
        parameters = Parameters()
        parameters.interval_b = numpy.array([-0.5, 2.5], float)
        parameters.interval_c = numpy.array([-1.5, 1.5], float)
        UnitCellToCluster = context.application.plugins.get_action("UnitCellToCluster")
        assert UnitCellToCluster.analyze_selection(parameters)
        UnitCellToCluster(parameters)
        # check the bond lengths
        Bond = context.application.plugins.get_node("Bond")
        universe = context.application.model.universe
        for bond in context.application.model.universe.children:
            if isinstance(bond, Bond):
                delta = bond.children[0].target.transformation.t - bond.children[1].target.transformation.t
                delta = universe.shortest_vector(delta)
                distance = numpy.linalg.norm(delta)
                assert distance < 4.0
    run_application(fn)

def test_unit_cell_to_cluster2():
    def fn():
        context.application.model.file_open("test/input/silica_layer.zml")
        parameters = Parameters()
        parameters.interval_a = numpy.array([0.0, 3.0], float)
        parameters.interval_b = numpy.array([0.0, 3.0], float)
        UnitCellToCluster = context.application.plugins.get_action("UnitCellToCluster")
        assert UnitCellToCluster.analyze_selection(parameters)
        UnitCellToCluster(parameters)
        crd_cluster = [node.transformation.t for node in context.application.model.universe.children]

        context.application.model.file_open("test/input/silica_layer.zml")
        parameters = Parameters()
        parameters.repetitions_a = 3
        parameters.repetitions_b = 3
        SuperCell = context.application.plugins.get_action("SuperCell")
        assert SuperCell.analyze_selection(parameters)
        SuperCell(parameters)
        crd_super = [node.transformation.t for node in context.application.model.universe.children]

        # check that the number of atoms is the same
        assert len(crd_super) == len(crd_cluster)
        # check if the coordinates match
        for c_super in crd_super:
            for i in xrange(len(crd_cluster)):
                c_cluster = crd_cluster[i]
                delta = c_cluster - c_super
                delta = context.application.model.universe.shortest_vector(delta)
                if numpy.linalg.norm(delta) < 1e-3:
                    del crd_cluster[i]
                    break
        assert len(crd_cluster) == 0
    run_application(fn)

def test_super_cell():
    def fn():
        context.application.model.file_open("test/input/periodic.zml")
        parameters = Parameters()
        parameters.repetitions_b = 2
        parameters.repetitions_c = 3
        SuperCell = context.application.plugins.get_action("SuperCell")
        assert SuperCell.analyze_selection(parameters)
        SuperCell(parameters)
    run_application(fn)

def test_super_cell_nowrap():
    def fn():
        context.application.model.file_open("test/input/silica_layer.zml")
        parameters = Parameters()
        parameters.repetitions_a = 2
        parameters.repetitions_b = 3
        SuperCell = context.application.plugins.get_action("SuperCell")
        assert SuperCell.analyze_selection(parameters)
        SuperCell(parameters)
        crd_before = [node.transformation.t for node in context.application.model.universe.children]
        WrapCellContents = context.application.plugins.get_action("WrapCellContents")
        assert WrapCellContents.analyze_selection()
        WrapCellContents()
        # coordinates should not be changed
        crd_after = [node.transformation.t for node in context.application.model.universe.children]
        for i in xrange(len(crd_after)):
            assert abs(crd_before[i][0] - crd_after[i][0]) < 1e-5
            assert abs(crd_before[i][1] - crd_after[i][1]) < 1e-5
            assert abs(crd_before[i][2] - crd_after[i][2]) < 1e-5
    run_application(fn)

def test_super_cell_bonds():
    def fn():
        context.application.model.file_open("test/input/silica_layer.zml")
        AutoConnectPhysical = context.application.plugins.get_action("AutoConnectPhysical")
        assert AutoConnectPhysical.analyze_selection()
        AutoConnectPhysical()
        parameters = Parameters()
        parameters.repetitions_a = 2
        parameters.repetitions_b = 3
        SuperCell = context.application.plugins.get_action("SuperCell")
        assert SuperCell.analyze_selection(parameters)
        SuperCell(parameters)
        Bond = context.application.plugins.get_node("Bond")
        for node in context.application.model.universe.children:
            if isinstance(node, Bond):
                node.calc_vector_dimensions()
                assert node.length < 4.0
    run_application(fn)

def test_define_unit_cell_vectors():
    def fn():
        context.application.model.file_open("test/input/periodic.zml")
        context.application.model.universe.cell = \
            context.application.model.universe.cell.copy_with(active=numpy.zeros(3, bool))
        context.application.main.select_nodes([
            context.application.model.universe.children[2],
            context.application.model.universe.children[4],
            context.application.model.universe.children[7],
        ])
        DefineUnitCellVectors = context.application.plugins.get_action("DefineUnitCellVectors")
        assert DefineUnitCellVectors.analyze_selection()
        DefineUnitCellVectors()
    run_application(fn)

def test_wrap_cell_contents():
    def fn():
        from molmod import UnitCell
        context.application.model.file_open("test/input/core_objects.zml")
        unit_cell = UnitCell(numpy.identity(3, float), numpy.ones(3, bool))
        context.application.model.universe.cell = unit_cell
        WrapCellContents = context.application.plugins.get_action("WrapCellContents")
        assert WrapCellContents.analyze_selection()
        WrapCellContents()
        assert len(context.application.action_manager.undo_stack) == 1
        WrapCellContents() # This should not result in an effective thing to happen:
        assert len(context.application.action_manager.undo_stack) == 1
    run_application(fn)

def test_wrap_cell_contents2():
    def fn():
        context.application.model.file_open("test/input/silica_layer.zml")
        crd_before = [node.transformation.t for node in context.application.model.universe.children]
        WrapCellContents = context.application.plugins.get_action("WrapCellContents")
        assert WrapCellContents.analyze_selection()
        WrapCellContents()
        # coordinates should not be changed
        crd_after = [node.transformation.t for node in context.application.model.universe.children]
        for i in xrange(len(crd_after)):
            assert abs(crd_before[i][0] - crd_after[i][0]) < 1e-5
            assert abs(crd_before[i][1] - crd_after[i][1]) < 1e-5
            assert abs(crd_before[i][2] - crd_after[i][2]) < 1e-5
    run_application(fn)

def test_calculate_average():
    def fn():
        context.application.model.file_open("test/input/core_objects.zml")
        context.application.main.select_nodes(context.application.model.universe.children[:2])
        CalculateAverage = context.application.plugins.get_action("CalculateAverage")
        assert CalculateAverage.analyze_selection()
        CalculateAverage()
    run_application(fn)

def test_view_plugins():
    def fn():
        ViewPlugins = context.application.plugins.get_action("ViewPlugins")
        assert ViewPlugins.analyze_selection()
        ViewPlugins()
    run_application(fn)

def test_camera_settings():
    def fn():
        CameraSettings = context.application.plugins.get_action("CameraSettings")
        assert CameraSettings.analyze_selection()
        CameraSettings()
    run_application(fn)

def test_about():
    def fn():
        About = context.application.plugins.get_action("About")
        assert About.analyze_selection()
        About()
    run_application(fn)

def test_add_plane():
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
        assert AddPlane.analyze_selection()
        AddPlane()
    run_application(fn)

def test_add_tetraeder():
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
        assert AddTetraeder.analyze_selection()
        AddTetraeder()
    run_application(fn)

def test_random_rotation():
    def fn():
        FileNew = context.application.plugins.get_action("FileNew")
        FileNew()
        context.application.main.select_nodes([context.application.model.universe])
        Frame = context.application.plugins.get_node("Frame")
        frame = Frame(transformation=Translation(numpy.random.uniform(-5, 5, 3)))
        context.application.model.universe.add(frame)
        frame.set_transformation(Rotation.random())
    run_application(fn)

