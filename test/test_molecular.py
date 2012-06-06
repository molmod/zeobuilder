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


from common import *

from zeobuilder import context
from zeobuilder.actions.composed import Parameters
from zeobuilder.expressions import Expression
import zeobuilder.actions.primitive as primitive

from molmod import angstrom, Translation
from molmod.bonds import BOND_SINGLE

import numpy


def test_add_atom():
    def fn():
        FileNew = context.application.plugins.get_action("FileNew")
        FileNew()
        context.application.main.select_nodes([context.application.model.universe])
        AddAtom = context.application.plugins.get_action("AddAtom")
        assert AddAtom.analyze_selection()
        AddAtom()
    run_application(fn)

def test_connect_single_bond():
    def fn():
        FileNew = context.application.plugins.get_action("FileNew")
        FileNew()
        context.application.main.select_nodes([context.application.model.universe])
        AddAtom = context.application.plugins.get_action("AddAtom")
        assert AddAtom.analyze_selection()
        AddAtom()
        context.application.main.select_nodes([context.application.model.universe])
        AddAtom = context.application.plugins.get_action("AddAtom")
        assert AddAtom.analyze_selection()
        AddAtom()
        context.application.main.select_nodes(context.application.model.universe.children)
        ConnectSingleBond = context.application.plugins.get_action("ConnectSingleBond")
        assert ConnectSingleBond.analyze_selection()
        ConnectSingleBond()
    run_application(fn)

def test_connect_double_bond():
    def fn():
        FileNew = context.application.plugins.get_action("FileNew")
        FileNew()
        context.application.main.select_nodes([context.application.model.universe])
        AddAtom = context.application.plugins.get_action("AddAtom")
        assert AddAtom.analyze_selection()
        AddAtom()
        context.application.main.select_nodes([context.application.model.universe])
        AddAtom = context.application.plugins.get_action("AddAtom")
        assert AddAtom.analyze_selection()
        AddAtom()
        context.application.main.select_nodes(context.application.model.universe.children)
        ConnectDoubleBond = context.application.plugins.get_action("ConnectDoubleBond")
        assert ConnectDoubleBond.analyze_selection()
        ConnectDoubleBond()
    run_application(fn)

def test_connect_triple_bond():
    def fn():
        FileNew = context.application.plugins.get_action("FileNew")
        FileNew()
        context.application.main.select_nodes([context.application.model.universe])
        AddAtom = context.application.plugins.get_action("AddAtom")
        assert AddAtom.analyze_selection()
        AddAtom()
        context.application.main.select_nodes([context.application.model.universe])
        AddAtom = context.application.plugins.get_action("AddAtom")
        assert AddAtom.analyze_selection()
        AddAtom()
        context.application.main.select_nodes(context.application.model.universe.children)
        ConnectTripleBond = context.application.plugins.get_action("ConnectTripleBond")
        assert ConnectTripleBond.analyze_selection()
        ConnectTripleBond()
    run_application(fn)

def test_auto_connect_physical_tpa():
    def fn():
        context.application.model.file_open("test/input/tpa.zml")
        context.application.main.select_nodes([context.application.model.universe])
        AutoConnectPhysical = context.application.plugins.get_action("AutoConnectPhysical")
        assert AutoConnectPhysical.analyze_selection()
        AutoConnectPhysical()
    run_application(fn)

def test_auto_connect_physical_tpa_framed():
    def fn():
        context.application.model.file_open("test/input/tpa.xyz")
        # put it in a frame
        context.application.main.select_nodes(context.application.model.universe.children)
        Frame = context.application.plugins.get_action("Frame")
        assert Frame.analyze_selection()
        Frame()
        # add bonds
        context.application.main.select_nodes([context.application.model.universe])
        AutoConnectPhysical = context.application.plugins.get_action("AutoConnectPhysical")
        assert AutoConnectPhysical.analyze_selection()
        AutoConnectPhysical()
        # count the number of bonds that are direct children of the universe
        # object, should be zero
        Bond = context.application.plugins.get_node("Bond")
        for child in context.application.model.universe.children:
            assert not isinstance(child, Bond)
    run_application(fn)

def test_auto_connect_physical_lau():
    def fn():
        context.application.model.file_open("test/input/lau.zml")
        context.application.main.select_nodes([context.application.model.universe])
        AutoConnectPhysical = context.application.plugins.get_action("AutoConnectPhysical")
        assert AutoConnectPhysical.analyze_selection()
        AutoConnectPhysical()
    run_application(fn)

def test_auto_connect_parameters_tpa():
    def fn():
        context.application.model.file_open("test/input/tpa.zml")
        universe = context.application.model.universe
        context.application.main.select_nodes([universe])
        parameters = Parameters()
        parameters.number1 = 6
        parameters.number2 = 6
        parameters.distance = 3.0
        parameters.bond_type = BOND_SINGLE
        AutoConnectParameters = context.application.plugins.get_action("AutoConnectParameters")
        assert AutoConnectParameters.analyze_selection(parameters)
        AutoConnectParameters(parameters)

        Bond = context.application.plugins.get_node("Bond")
        num_bonds = sum(isinstance(node,Bond) for node in universe.children)
        assert num_bonds == 2*4
    run_application(fn)

def test_auto_connect_parameters_tpa2():
    def fn():
        context.application.model.file_open("test/input/tpa.zml")
        universe = context.application.model.universe
        context.application.main.select_nodes([universe] + universe.children)
        parameters = Parameters()
        parameters.number1 = 6
        parameters.number2 = 6
        parameters.distance = 3.0
        parameters.bond_type = BOND_SINGLE
        AutoConnectParameters = context.application.plugins.get_action("AutoConnectParameters")
        assert AutoConnectParameters.analyze_selection(parameters)
        AutoConnectParameters(parameters)

        Bond = context.application.plugins.get_node("Bond")
        num_bonds = sum(isinstance(node,Bond) for node in universe.children)
        assert num_bonds == 2*4
    run_application(fn)

def test_auto_connect_parameters_lau():
    def fn():
        context.application.model.file_open("test/input/lau.zml")
        context.application.main.select_nodes([context.application.model.universe])
        parameters = Parameters()
        parameters.number1 = 14
        parameters.number2 = 14
        parameters.distance = 6.0
        parameters.bond_type = BOND_SINGLE
        AutoConnectParameters = context.application.plugins.get_action("AutoConnectParameters")
        assert AutoConnectParameters.analyze_selection(parameters)
        AutoConnectParameters(parameters)
    run_application(fn)

def test_merge_overlapping_atoms_lau():
    def fn():
        context.application.model.file_open("test/input/lau_double.zml")
        context.application.main.select_nodes([context.application.model.universe])
        MergeOverlappingAtoms = context.application.plugins.get_action("MergeOverlappingAtoms")
        assert MergeOverlappingAtoms.analyze_selection()
        MergeOverlappingAtoms()
    run_application(fn)

def test_center_of_mass():
    def fn():
        context.application.model.file_open("test/input/tpa.zml")
        context.application.main.select_nodes([context.application.model.universe])
        CenterOfMass = context.application.plugins.get_action("CenterOfMass")
        assert CenterOfMass.analyze_selection()
        CenterOfMass()
    run_application(fn)

def test_center_of_mass_and_principal_axes():
    def fn():
        context.application.model.file_open("test/input/tpa.zml")
        context.application.main.select_nodes([context.application.model.universe])
        CenterOfMassAndPrincipalAxes = context.application.plugins.get_action("CenterOfMassAndPrincipalAxes")
        assert CenterOfMassAndPrincipalAxes.analyze_selection()
        CenterOfMassAndPrincipalAxes()
    run_application(fn)

def test_rearrange_atoms():
    def fn():
        context.application.model.file_open("test/input/tpa.zml")
        context.application.main.select_nodes([context.application.model.universe])
        RearrangeAtoms = context.application.plugins.get_action("RearrangeAtoms")
        assert RearrangeAtoms.analyze_selection()
        RearrangeAtoms()
    run_application(fn)

def test_saturate_with_hydrogens_tpa():
    def fn():
        context.application.model.file_open("test/input/tpa.zml")
        Atom = context.application.plugins.get_node("Atom")
        for child in context.application.model.universe.children[::-1]:
            if isinstance(child, Atom) and child.number == 1:
                context.application.model.universe.children.remove(child)
        context.application.main.select_nodes([context.application.model.universe])
        AutoConnectPhysical = context.application.plugins.get_action("AutoConnectPhysical")
        assert AutoConnectPhysical.analyze_selection()
        AutoConnectPhysical()
        context.application.main.select_nodes([context.application.model.universe])
        SaturateWithHydrogens = context.application.plugins.get_action("SaturateWithHydrogens")
        assert SaturateWithHydrogens.analyze_selection()
        SaturateWithHydrogens()
    run_application(fn)

def test_saturate_with_hydrogens_manual_tpa():
    def fn():
        context.application.model.file_open("test/input/tpa.xyz")
        Atom = context.application.plugins.get_node("Atom")
        for child in context.application.model.universe.children[::-1]:
            if isinstance(child, Atom) and child.number == 1:
                context.application.model.universe.children.remove(child)
        context.application.main.select_nodes([context.application.model.universe])
        AutoConnectPhysical = context.application.plugins.get_action("AutoConnectPhysical")
        assert AutoConnectPhysical.analyze_selection()
        AutoConnectPhysical()

        parameters = Parameters()
        parameters.num_hydrogens = 2
        parameters.valence_angle = 1.9093

        context.application.main.select_nodes([context.application.model.universe.children[1]])
        SaturateHydrogensManual = context.application.plugins.get_action("SaturateHydrogensManual")
        assert SaturateHydrogensManual.analyze_selection(parameters)
        SaturateHydrogensManual(parameters)
    run_application(fn)

def test_distribution_bond_lengths_precursor():
    def fn():
        context.application.model.file_open("test/input/precursor.zml")
        context.application.main.select_nodes([context.application.model.universe])

        parameters = Parameters()
        parameters.filter_atom1 = Expression()
        parameters.filter_bond12 = Expression()
        parameters.filter_atom2 = Expression()

        DistributionBondLengths = context.application.plugins.get_action("DistributionBondLengths")
        assert DistributionBondLengths.analyze_selection(parameters)
        DistributionBondLengths(parameters)
    run_application(fn)

def test_distribution_bending_angles_precursor():
    def fn():
        context.application.model.file_open("test/input/precursor.zml")
        context.application.main.select_nodes([context.application.model.universe])

        parameters = Parameters()
        parameters.filter_atom1 = Expression()
        parameters.filter_bond12 = Expression()
        parameters.filter_atom2 = Expression("atom.number==8")
        parameters.filter_bond23 = Expression()
        parameters.filter_atom3 = Expression()

        DistributionBendingAngles = context.application.plugins.get_action("DistributionBendingAngles")
        assert DistributionBendingAngles.analyze_selection(parameters)
        DistributionBendingAngles(parameters)
    run_application(fn)

def test_distribution_dihedral_angles_precursor():
    def fn():
        context.application.model.file_open("test/input/precursor.zml")
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
        assert DistributionDihedralAngles.analyze_selection(parameters)
        DistributionDihedralAngles(parameters)
    run_application(fn)

def test_molden_labels():
    def fn():
        context.application.model.file_open("test/input/precursor.zml")
        context.application.main.select_nodes(context.application.model.universe.children)

        MoldenLabels = context.application.plugins.get_action("MoldenLabels")
        assert MoldenLabels.analyze_selection()
        MoldenLabels()
    run_application(fn)

def test_clone_order():
    def fn():
        context.application.model.file_open("test/input/springs.zml")
        context.application.main.select_nodes(context.application.model.universe.children[:2])
        CloneOrder = context.application.plugins.get_action("CloneOrder")
        assert CloneOrder.analyze_selection()
        CloneOrder()
    run_application(fn)

def test_clone_order2():
    def fn():
        context.application.model.file_open("test/input/azaallyl_thf_mm.zml")
        context.application.main.select_nodes(context.application.model.universe.children[2:])
        CloneOrder = context.application.plugins.get_action("CloneOrder")
        assert CloneOrder.analyze_selection()
        CloneOrder()
    run_application(fn)

def test_strong_ring_distribution():
    def fn():
        context.application.model.file_open("test/input/springs.zml")
        context.application.main.select_nodes([context.application.model.universe.children[1]])

        StrongRingDistribution = context.application.plugins.get_action("StrongRingDistribution")
        assert StrongRingDistribution.analyze_selection()
        StrongRingDistribution()
    run_application(fn)

def test_frame_molecules():
    def fn():
        from molmod import UnitCell
        context.application.model.file_open("test/input/methane_box22_125.xyz")
        universe = context.application.model.universe

        context.application.action_manager.record_primitives = False
        unit_cell = UnitCell(numpy.identity(3, float)*22*angstrom, numpy.ones(3, bool))
        primitive.SetProperty(universe, "cell", unit_cell)

        context.application.main.select_nodes([universe])
        AutoConnectPhysical = context.application.plugins.get_action("AutoConnectPhysical")
        assert AutoConnectPhysical.analyze_selection()
        AutoConnectPhysical()

        context.application.main.select_nodes([universe])
        FrameMolecules = context.application.plugins.get_action("FrameMolecules")
        assert FrameMolecules.analyze_selection()
        FrameMolecules()

        Bond = context.application.plugins.get_node("Bond")
        for frame in universe.children:
            for bond in frame.children:
                if isinstance(bond, Bond):
                    bond.calc_vector_dimensions()
                    assert bond.length < 2*angstrom
    run_application(fn)

def test_frame_molecules2():
    def fn():
        context.application.model.file_open("test/input/ethane-ethane-pos.xyz")
        universe = context.application.model.universe

        context.application.action_manager.record_primitives = False
        context.application.main.select_nodes(universe.children)

        Frame = context.application.plugins.get_action("Frame")
        assert Frame.analyze_selection()
        Frame()

        context.application.main.select_nodes(universe.children)
        AutoConnectPhysical = context.application.plugins.get_action("AutoConnectPhysical")
        assert AutoConnectPhysical.analyze_selection()
        AutoConnectPhysical()

        context.application.main.select_nodes(universe.children)
        FrameMolecules = context.application.plugins.get_action("FrameMolecules")
        assert FrameMolecules.analyze_selection()
        FrameMolecules()
    run_application(fn)

def test_frame_molecules_periodic():
    def fn():
        context.application.model.file_open("test/input/DOH_2xAl_Cu.zml")
        universe = context.application.model.universe

        context.application.main.select_nodes([universe])
        FrameMolecules = context.application.plugins.get_action("FrameMolecules")
        assert FrameMolecules.analyze_selection()
        FrameMolecules()

        # nothing should have happend. there should not be one frame.
        assert len(universe.children) > 1
    run_application(fn)

def test_frame_molecules_periodic2():
    def fn():
        context.application.model.file_open("test/input/sdock_testing.zml")
        universe = context.application.model.universe

        context.application.main.select_nodes([universe])
        FrameMolecules = context.application.plugins.get_action("FrameMolecules")
        assert FrameMolecules.analyze_selection()
        FrameMolecules()

        # there should not be two frames.
        assert len(universe.children) > 2
    run_application(fn)

def test_select_bonded_neighbors():
    def fn():
        context.application.model.file_open("test/input/springs.zml")
        context.application.main.select_nodes(context.application.model.universe.children[0].children[0:1])
        SelectBondedNeighbors = context.application.plugins.get_action("SelectBondedNeighbors")
        assert SelectBondedNeighbors.analyze_selection()
        SelectBondedNeighbors()
    run_application(fn)

def test_add_zeolite_tetraeders():
    def fn():
        context.application.model.file_open("test/input/precursor.zml")
        context.application.main.select_nodes([context.application.model.universe])
        AddZeoliteTetraeders = context.application.plugins.get_action("AddZeoliteTetraeders")
        assert AddZeoliteTetraeders.analyze_selection()
        AddZeoliteTetraeders()
    run_application(fn)

def test_com_praxes_diatomic():
    def fn():
        FileNew = context.application.plugins.get_action("FileNew")
        FileNew()
        Atom = context.application.plugins.get_node("Atom")
        Frame = context.application.plugins.get_node("Frame")
        frame = Frame()
        context.application.model.universe.add(frame)
        atom1 = Atom()
        atom2 = Atom(transformation=Translation([1.1,0.1,0.03]))
        frame.add(atom1)
        frame.add(atom2)
        CenterOfMassAndPrincipalAxes = context.application.plugins.get_action("CenterOfMassAndPrincipalAxes")
        context.application.main.select_nodes([context.application.model.universe.children[0]])
        assert CenterOfMassAndPrincipalAxes.analyze_selection()
        CenterOfMassAndPrincipalAxes()
    run_application(fn)

