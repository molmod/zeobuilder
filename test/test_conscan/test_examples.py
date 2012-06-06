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
# --



from conscan import Geometry, Connection, ProgressMessage, TriangleScanner, PairScanner

from molmod import Rotation, MolecularGraph
from molmod.periodic import periodic
from molmod.io import XYZFile

import numpy as np, random



class Sender(object):
    def __init__(self, silent=True):
        self.silent = silent
        self.connections = []

    def __call__(self, message):
        if not self.silent:
            if isinstance(message, ProgressMessage):
                print "--===***  %i/%i %10s  ***===--" % (message.progress, message.maximum, message.label)
                return
            elif isinstance(message, Connection):
                print "QUALITY:", message.quality
                print "DUPLICATE:", message.duplicate
                print "INVERTIBLE:", message.invertible
                print "PAIRS:", message.pairs
                print "FROWARD", str(message.transformation)[:-1]
                print "INVERSE", message.inverse_transformation
                self.connections.append(message)
            else:
                print message
            print "=~-~"*20
        if isinstance(message, Connection):
            self.connections.append(message)


def get_simple_model1():
    coordinates = np.array([
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 2.0],
        [1.0, 0.0, 2.0],
    ], float)
    connect_mask = np.array([False, True, True, True, True], bool)
    radii = np.array([1.0, 0.1, 0.1, 0.1, 0.1], float)*0.5
    return coordinates, connect_mask, radii

def get_simple_model2():
    coordinates = np.array([
        [0.0, 1.0, 1.0],
        [0.0, 1.0, 0.0],
        [2.0, 0.0, 1.0],
        [0.0, 0.0, 2.0],
        [1.0, 0.0, 2.0],
    ], float)
    connect_mask = np.array([True, True, True, False, True], bool)
    radii = np.array([0.1, 0.1, 0.1, 1.0, 0.1], float)*0.5
    return coordinates, connect_mask, radii


def test_triangle_ego_simple():
    geometry = Geometry(*get_simple_model1())
    sender = Sender()
    scanner = TriangleScanner(
        send=sender,
        geometry1=geometry,
        geometry2=None,
        action_radius=10.0,
        hit_tolerance=0.1,
        allow_inversions=True,
        minimum_trianlge_area=0.001**2,
    )
    scanner.run()
    assert len(sender.connections) == 7


def test_pair_ego_simple():
    geometry = Geometry(*get_simple_model1())
    sender = Sender()
    scanner = PairScanner(
        send=sender,
        geometry1=geometry,
        geometry2=None,
        action_radius=10.0,
        hit_tolerance=0.1,
        rotation2=None,
    )
    scanner.run()
    assert len(sender.connections) == 1


def test_pair_ego_simple_rot():
    geometry = Geometry(*get_simple_model1())
    rot = Rotation.from_properties(-0.5*np.pi, [-1, 1, 0], False)
    sender = Sender()
    scanner = PairScanner(
        send=sender,
        geometry1=geometry,
        geometry2=None,
        action_radius=10.0,
        hit_tolerance=0.1,
        rotation2=rot,
    )
    scanner.run()
    assert len(sender.connections) == 1


def test_triangle_simple():
    geometry1 = Geometry(*get_simple_model1())
    geometry2 = Geometry(*get_simple_model2())
    sender = Sender()
    scanner = TriangleScanner(
        send=sender,
        geometry1=geometry1,
        geometry2=geometry2,
        action_radius=10.0,
        hit_tolerance=0.1,
        allow_inversions=True,
        minimum_trianlge_area=0.001**2,
    )
    scanner.run()
    assert len(sender.connections) == 2


def test_pair_simple():
    geometry1 = Geometry(*get_simple_model1())
    geometry2 = Geometry(*get_simple_model2())
    sender = Sender()
    scanner = PairScanner(
        send=sender,
        geometry1=geometry1,
        geometry2=geometry2,
        action_radius=10.0,
        hit_tolerance=0.1,
        rotation2=None,
    )
    scanner.run()
    assert len(sender.connections) == 1


def test_pair_simple_rot():
    geometry1 = Geometry(*get_simple_model1())
    geometry2 = Geometry(*get_simple_model2())
    rot = Rotation.from_properties(-0.5*np.pi, [0, 1, 0], False)
    sender = Sender()
    scanner = PairScanner(
        send=sender,
        geometry1=geometry1,
        geometry2=geometry2,
        action_radius=10.0,
        hit_tolerance=0.1,
        rotation2=rot,
    )
    scanner.run()
    assert len(sender.connections) == 2


def get_precursor_model():
    m = XYZFile("test/input/mfi_precursor.xyz").get_molecule()
    mgraph = MolecularGraph.from_geometry(m)
    connect_masks = np.array([
        number == 8 and len(mgraph.neighbors[index]) == 1
        for index, number in enumerate(m.numbers)
    ], bool)
    radii = np.array([
        periodic[number].vdw_radius * {True: 0.3, False: 1.0}[connect_mask]
        for number, connect_mask in zip(m.numbers, connect_masks)
    ], float)
    radii += np.random.uniform(0, 0.1, radii.shape)
    return m.coordinates, connect_masks, radii


def test_triangle_ego_precursor():
    geometry = Geometry(*get_precursor_model())
    sender = Sender()
    scanner = TriangleScanner(
        send=sender,
        geometry1=geometry,
        geometry2=None,
        action_radius=5.0,
        hit_tolerance=0.1,
        allow_inversions=True,
        minimum_trianlge_area=0.001**2,
    )
    scanner.run()

def test_pair_ego_precursor():
    geometry = Geometry(*get_precursor_model())
    sender = Sender()
    scanner = PairScanner(
        send=sender,
        geometry1=geometry,
        geometry2=None,
        action_radius=5.0,
        hit_tolerance=0.1,
        rotation2=None,
    )
    scanner.run()

def test_pair_ego_precursor_rot():
    geometry = Geometry(*get_precursor_model())
    rot = Rotation.from_properties(-0.5*np.pi, [-1, 1, 0], False)
    sender = Sender()
    scanner = PairScanner(
        send=sender,
        geometry1=geometry,
        geometry2=None,
        action_radius=10.0,
        hit_tolerance=0.1,
        rotation2=rot,
    )
    scanner.run()


