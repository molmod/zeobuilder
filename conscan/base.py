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


from molmod import PairSearchIntra, Rotation

from interface import ProgressMessage

import math, numpy, copy


__all__ = ["Scanner"]


class Environment(object):
    def __init__(self, id, coordinate):
        self.id = id
        self.coordinate = coordinate
        deltas = []
        distances = []




class EmptyGeometry(Exception):
    pass


class Scanner(object):
    def __init__(self, send, geometry1, geometry2, action_radius, hit_tolerance):
        self.send = send
        self.geometry1 = geometry1
        self.geometry2 = geometry2
        self.action_radius = action_radius
        self.hit_tolerance = hit_tolerance

        self.egoscan = (geometry2 is None)
        if self.egoscan:
            self.geometry2 = geometry1

    def hit(self, difference):
        return abs(difference) < self.hit_tolerance

    def run(self):
        # find the connections
        self.generate_connections()
        self.compute_transformations()
        self.evaluate_connections()
        self.eliminate_duplicate_connections()
        # send them to the parent process
        self.connections.sort(key=(lambda c: -c.quality))
        maximum = len(self.connections)
        for progress, connection in enumerate(self.connections):
            self.send(ProgressMessage("send_con", progress, maximum))
            self.send(connection)
        self.send(ProgressMessage("send_con", maximum, maximum))

    #
    # generate_connections
    #

    def generate_connections(self):
        self.connections = []
        self.compute_environmental_descriptions()
        self.compare_environments_pairwise()

    def compute_environmental_descriptions(self):
        def setup_env(geometry, action_radius):
            environments = {}
            def add_to_environments(ia, ib, delta, distance):
                env_a = environments.get(ia)
                if env_a is None:
                    env_a = Environment(ia, geometry.coordinates[ia])
                    env_a.deltas = []
                    env_a.distances = []
                    env_a.neighbors = []
                    env_a.reverse_neighbors = {}
                    environments[ia] = env_a
                env_a.deltas.append(delta)
                env_a.distances.append(distance)
                env_a.neighbors.append(ib)
                env_a.reverse_neighbors[ib] = len(env_a.reverse_neighbors)

            # now compare 'all' distances
            lookup = geometry.connect_masks.nonzero()[0]
            psi = PairSearchIntra(geometry.coordinates[geometry.connect_masks], action_radius)
            for i1, i2, delta, distance in psi:
                add_to_environments(lookup[i1], lookup[i2],  delta, distance)
                add_to_environments(lookup[i2], lookup[i1], -delta, distance)

            # At this time we have for each object a set of vectors that
            # point to other objects within the range of radius. Now we will
            # compute some aditional information
            for env in environments.itervalues():
                env.n = len(env.deltas)
                env.deltas = numpy.array(env.deltas)
                env.distances = numpy.array(env.distances)
                env.neighbors = numpy.array(env.neighbors)
                env.directions = (env.deltas.transpose() / (env.distances + (env.distances == 0.0))).transpose()

            return environments

        def assign_env(geometry, number):
            environments = setup_env(geometry, self.action_radius)

            def overlap(environment):
                for distance in environment.distances:
                    if self.hit(distance):
                        return True
                return False

            # eliminate all environments that might overlap with others
            geometry.environments = dict(
                (id, environment) for id, environment in environments.iteritems()
                if not overlap(environment)
            )

            if len(geometry.environments) == 0:
                raise EmptyGeometry("No usable points were found in geometry %i" % number)

            #self.output("     '" + geometry.root.name + "' has " + str(len(geometry.environments) + len(dupes)) + " - " + str(len(dupes)) + " = " + str(len(geometry.environments)) + " environments to be checked for connection.\n")
            #for environment in geometry.environments:
            #    self.output("          identifier %s\tneighbors %s\n" % (environment.id, environment.neighbors))

        if self.egoscan:
            self.send(ProgressMessage("calc_env", 0, 1))
            assign_env(self.geometry1, 1)
            self.send(ProgressMessage("calc_env", 1, 1))
        else:
            self.send(ProgressMessage("calc_env", 0, 2))
            assign_env(self.geometry1, 1)
            self.send(ProgressMessage("calc_env", 1, 2))
            assign_env(self.geometry2, 2)
            self.send(ProgressMessage("calc_env", 2, 2))

        #self.output("     Number of envorinments computed: %i\n" % len(self.environment))


    def compare_environments_pairwise(self):
        #self.output("     Number of environment comparisons: %i\n" % (len(self.geometrys[0].environment) * len(self.geometrys[1].environment)))

        environments1 = self.geometry1.environments
        environments2 = self.geometry2.environments
        maximum = len(environments1)
        for progress, environment1 in enumerate(environments1.itervalues()):
            self.send(ProgressMessage("comp_env", progress, maximum))
            for environment2 in environments2.itervalues():
                self.compare_environments(environment1, environment2)
        self.send(ProgressMessage("comp_env", maximum, maximum))

        #self.output("     Number of accepted triangles: %i\n" % len(self.connections))
        #self.output("     Average of accepted triangles per environment-pair: %.2f\n" % (len(self.connections) / (len(self.geometrys[0].environment) * len(self.geometrys[1].environment))))

    def compare_environments(self, environment1, environment2):
        raise NotImplementedError

    #
    # compute_transformations
    #

    def compute_transformations(self):
        maximum = len(self.connections)
        for progress, connection in enumerate(self.connections):
            self.send(ProgressMessage("calc_trans", progress, maximum))
            connection.set_transformation(self.compute_transformation(connection))
        self.send(ProgressMessage("calc_trans", maximum, maximum))

    def compute_transformation(self, connection):
        raise NotImplementedError

    #
    # evaluate_connections
    #

    def evaluate_connections(self):
        maximum = len(self.connections)
        if maximum > 0:
            for progress, connection in enumerate(self.connections):
                self.send(ProgressMessage("eval_con", progress, maximum))
                connection.compute_quality(self.geometry1, self.geometry2)
        self.send(ProgressMessage("eval_con", maximum, maximum))

    #
    # eliminate_duplicate_connections
    #

    def eliminate_duplicate_connections(self):
        # Stage 1 searches for duplicates that arise because certain pairs of
        # matching triangles simply lead to the same relative orientation. Two
        # connections are compared based on the overlapping atom pairs. These
        # were determined before during the evaluation of the quality function.
        # When a duplicate is detected, the one with the highest quality is
        # retained.
        stage1 = {}
        progress = 0
        maximum = len(self.connections)
        for connection in self.connections:
            self.send(ProgressMessage("elim_dup", progress, maximum))
            if isinstance(connection.transformation, Rotation):
                key = (connection.pairs, numpy.linalg.det(connection.transformation.r) > 0)
            else:
                key = connection.pairs
            existing = stage1.get(key)
            if existing is None:
                progress += 1
                stage1[key] = connection
            else:
                maximum -= 1
                if existing.quality < connection.quality:
                    stage1[key] = connection
        self.send(ProgressMessage("elim_dup", maximum, maximum))

        if self.egoscan:
            # Stage 2 is only performed when connections between a building block
            # and exact copies are searched. In that case, it might happen that
            # two connection are the same when in one of both connections, the
            # two building blocks are exchanged. The square of the associated
            # transformation is the identity matrix.
            stage2 = {}
            while len(stage1) > 0:
                self.send(ProgressMessage("elim_dup", len(stage2), len(stage1) + len(stage2)))
                key, connection = stage1.popitem()
                if isinstance(connection.transformation, Rotation):
                    pairs = key[0]
                else:
                    pairs = key
                inverse_pairs = frozenset((second, first) for first, second in connection.pairs)
                if isinstance(connection.transformation, Rotation):
                    inverse_key = (inverse_pairs, key[1])
                else:
                    inverse_key = inverse_pairs
                if inverse_key in stage1:
                    del stage1[inverse_key]
                    connection.invertible = True
                stage2[key] = connection
            self.send(ProgressMessage("elim_dup", len(stage2), len(stage1) + len(stage2)))
        else:
            stage2 = stage1

        self.connections = stage2.values()


