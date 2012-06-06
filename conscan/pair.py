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


from interface import Connection
from base import Scanner

from molmod.transformations import Translation, Complete, Rotation

import numpy, sys, copy


__all__ = ["PairScanner"]


class PairScanner(Scanner):
    def __init__(self, send, geometry1, geometry2, action_radius, hit_tolerance, rotation2):
        Scanner.__init__(self, send, geometry1, geometry2, action_radius, hit_tolerance)
        if rotation2 is None:
            self.rotation2 = Rotation.identity()
        else:
            self.rotation2 = rotation2

    #
    # generate_connections
    #

    def compare_environments(self, environment1, environment2):
        #self.output("*** COMPARING: %s %s\n" % (point1.id.name, point2.id.name))
        for index1, delta1 in enumerate(environment1.deltas):
            for index2, delta2 in enumerate(environment2.deltas):
                # pairs of deltas must match within a certain accuracy AND avoiding duplicates
                diff_delta = delta1 - self.rotation2*delta2
                diff_distance = numpy.linalg.norm(diff_delta)
                if (
                    self.hit(diff_distance) and
                    environment1.id < environment1.neighbors[index1]
                ):
                    connection = Connection(set([
                        (environment1.id, environment2.id),
                        (environment1.neighbors[index1], environment2.neighbors[index2])
                    ]))
                    connection.t = environment1.coordinate - self.rotation2*environment2.coordinate + 0.5*diff_delta
                    self.connections.append(connection)


    #
    # compute_transformations
    #

    def compute_transformation(self, connection):
        transformation = Complete(self.rotation2.r, connection.t)
        del connection.t
        return transformation


