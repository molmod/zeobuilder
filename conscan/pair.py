# ConScan is a molecular connection scanner
# Copyright (C) 2007 - 2010 Toon Verstraelen <Toon.Verstraelen@UGent.be>
#
# This file is part of ConScan.
#
# ConScan is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# ConScan is distributed in the hope that it will be useful,
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


