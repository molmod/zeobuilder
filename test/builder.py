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
from zeobuilder.undefined import Undefined
from zeobuilder.expressions import Expression

from molmod import Rotation, angstrom

import numpy


__all__ = ["BuilderActions"]


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

            ScanForConnections = context.application.plugins.get_action("ScanForConnections")

            parameters = ScanForConnections.default_parameters()
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

            ScanForConnections = context.application.plugins.get_action("ScanForConnections")
            rotation2 = Rotation.from_properties(1*numpy.pi, [0, 1, 0], False)

            parameters = ScanForConnections.default_parameters()
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
            parameters.rotation2 = rotation2

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


