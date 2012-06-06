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


from interface import Connection, ProgressMessage
from base import Scanner

from molmod import random_orthonormal, angle, Translation, Rotation, Complete

import copy, numpy


__all__ = ["TriangleConnection", "Triangle", "TriangleScanner"]


class TriangleConnection(Connection):
    def __init__(self, pairs, minimum_area):
        Connection.__init__(self, set([
            (environment1.id, environment2.id)
            for environment1, environment2
            in pairs
        ]))
        self.triangle1 = Triangle([pair[0] for pair in pairs], minimum_area)
        self.triangle2 = Triangle([pair[1] for pair in pairs], minimum_area)
        self.valid = self.triangle1.valid and self.triangle2.valid


class Triangle(object):
    def __init__(self, environments, minimum_area):
        assert len(environments) == 3
        assert minimum_area > 0
        self.environments = environments
        self.coordinates = [copy.deepcopy(environment.coordinate) for environment in environments]
        self.center = sum(coordinate for coordinate in self.coordinates) / 3.0
        self.deltas = []
        for first, second in ((0, 1), (1, 2), (2, 0)):
            self.deltas.append(self.coordinates[first] - self.coordinates[second])
        self.normal = numpy.cross(self.deltas[0], self.deltas[1])
        length_normal = numpy.linalg.norm(self.normal)
        self.area = 0.5*length_normal
        if self.area > minimum_area:
            self.normal /= length_normal
            self.valid = True
        else:
            self.valid = False

    def apply_to_coordinates(self, transformation):
        for coordinate in self.coordinates:
            coordinate[:] = transformation*coordinate


class TriangleScanner(Scanner):
    def __init__(self, send, geometry1, geometry2, action_radius, hit_tolerance, allow_inversions, minimum_trianlge_area):
        Scanner.__init__(self, send, geometry1, geometry2, action_radius, hit_tolerance)
        self.allow_inversions = allow_inversions
        self.minimum_trianlge_area = minimum_trianlge_area

    #
    # generate_connections
    #

    def compare_environments(self, environment1, environment2):
        #print "*** COMPARING: %3i with %3i" % (environment1.id, environment2.id)
        # first do a distance compare test
        matching_pairs = []
        for index1, distance1 in enumerate(environment1.distances):
            for index2, distance2 in enumerate(environment2.distances):
                # avoiding duplicates part 1
                if environment1.id < environment1.neighbors[index1]:
                    # pairs of distances must match within a certain accuracy
                    #print "(%i,%i) = %6.3f with (%i,%i) = %6.3f" % (environment1.id, environment1.neighbors[index1], distance1, environment2.id, environment2.neighbors[index2], distance2),
                    if self.hit(distance1 - distance2):
                    #    print "    match"
                        matching_pairs.append((environment1.neighbors[index1], environment2.neighbors[index2]))
                    #else:
                    #    print

        # the pairs of matching distances can be further examined for the third side of the triangle
        n = len(matching_pairs)
        for pair1 in matching_pairs:
            for pair2 in matching_pairs:
                # if two sides of one of the triangles coincide, skip this combination
                if (pair1[0] == pair2[0]) or (pair1[1] == pair2[1]): continue
                # avoiding duplicates part 2
                if (pair1[1] >= pair2[1]): continue
                third_sides = [-1.0, -1.0]
                for k, geometry in enumerate([self.geometry1, self.geometry2]):
                    pointa = geometry.environments[pair1[k]]
                    if pair2[k] in pointa.neighbors:
                        third_sides[k] = pointa.distances[pointa.reverse_neighbors[pair2[k]]]
                    else:
                        third_sides = None
                        break
                if third_sides is None: continue
                if self.hit(third_sides[0] - third_sides[1]):
                    new_connection = TriangleConnection(
                        [
                            (self.geometry1.environments[pair1[0]], self.geometry2.environments[pair1[1]]),
                            (self.geometry1.environments[pair2[0]], self.geometry2.environments[pair2[1]]),
                            (environment1, environment2)
                        ], self.minimum_trianlge_area
                    )
                    #print "           %s\n" % [(pair[0].id, pair[1].id) for pair in new_connection.pairs])
                    if new_connection.valid:
                        self.connections.append(new_connection)
                    #poking for bugs:
                    #connection_id = sets.ImmutableSet([sets.ImmutableSet([pair[0].id, pair[1].id]) for pair in new_connection.pairs])
                    #if connection_id in self.connection_by_id:
                    #    self.connection_by_id[connection_id].add(new_connection)
                    #else:
                    #    self.connection_by_id[connection_id] = sets.Set([new_connection])

    #
    # compute_transformations
    #

    def compute_transformation(self, connection):
        #print connection.pairs
        triangle1 = connection.triangle1
        triangle2 = connection.triangle2

        triangles = [triangle1, triangle2]

        #print "BEFORE TRANSFORMING\n"
        #for triangle in triangles:
        #    #print "-------"
        #    for coordinate in triangle.coordinates:
        #        #print coordinate
        #print "---------"

        # *** t1: translation of triangle in geometry2 to origin
        t1 = Translation(-triangle2.center)
        #print triangle2.center
        triangle2.apply_to_coordinates(t1)
        # also move triangle1 to the origin
        t_tmp = Translation(-triangle1.center) # was t0
        triangle1.apply_to_coordinates(t_tmp)
        #print "AFTER CENTERING (T1 and T0)"
        #for triangle in triangles:
        #    #print "-------"
        #    for coordinate in triangle.coordinates:
        #        #print coordinate

        # *** r2: make the two triangles coplanar
        #print "NORMALS"
        #print triangle1.normal
        #print triangle2.normal
        rotation_axis = numpy.cross(triangle2.normal, triangle1.normal)
        if numpy.dot(rotation_axis, rotation_axis) < 1e-8:
            rotation_axis = random_orthonormal(triangle2.normal)
        rotation_angle = angle(triangle2.normal, triangle1.normal)
        #print "R2 %s, %s" % (rotation_angle/numpy.pi*180, rotation_axis)
        r2 = Rotation.from_properties(rotation_angle, rotation_axis, False)
        triangle2.apply_to_coordinates(r2)
        #print "AFTER R2"
        #for triangle in triangles:
        #    #print "-------"
        #    for coordinate in triangle.coordinates:
        #        #print coordinate

        # bring both triangles in the x-y plane, by a rotation around an axis
        # orthogonal to the Z-axis.
        rotation_axis = numpy.array([triangle1.normal[1], -triangle1.normal[0], 0.0], float)
        if numpy.dot(rotation_axis, rotation_axis) < 1e-8:
            rotation_axis = numpy.array([1.0, 0.0, 0.0], float)
        cos_angle = triangle1.normal[2]
        if cos_angle >= 1.0: rotation_angle = 0
        elif cos_angle <= -1.0: rotation_angle = numpy.pi
        else: rotation_angle = numpy.arccos(cos_angle)
        #print "RT %s, %s" % (rotation_angle/numpy.pi*180, rotation_axis)
        r_flat = Rotation.from_properties(rotation_angle, rotation_axis, False)
        triangle1.apply_to_coordinates(r_flat)
        triangle2.apply_to_coordinates(r_flat)

        #print "AFTER RT"
        #for triangle in triangles:
        #    #print "-------"
        #    for coordinate in triangle.coordinates:
        #        #print coordinate


        # *** r3: second rotation that makes both triangle coinced
        H = lambda a, b, c, d: a*c + b*d + (a+b)*(c+d)
        c = (H(
            triangle1.coordinates[0][0], triangle1.coordinates[1][0],
            triangle2.coordinates[0][0], triangle2.coordinates[1][0]
        ) + H(
            triangle1.coordinates[0][1], triangle1.coordinates[1][1],
            triangle2.coordinates[0][1], triangle2.coordinates[1][1]
        ))
        s = (H(
            triangle1.coordinates[0][1], triangle1.coordinates[1][1],
            triangle2.coordinates[0][0], triangle2.coordinates[1][0]
        ) - H(
            triangle1.coordinates[0][0], triangle1.coordinates[1][0],
            triangle2.coordinates[0][1], triangle2.coordinates[1][1]
        ))
        #if c > s: c, s = -c, -s
        #print "cos=%f sin=%f" % (c, s)
        rotation_angle = numpy.arctan2(s, c)
        #print "R3 %s, %s" % (rotation_angle/numpy.pi*180, triangle1.normal)
        r3 = Rotation.from_properties(rotation_angle, triangle1.normal, False)
        r_tmp = Rotation.from_properties(rotation_angle, numpy.array([0, 0, 1], float), False)
        triangle2.apply_to_coordinates(r_tmp)
        #print "AFTER R3"
        #for triangle in triangles:
        #    #print "-------"
        #    for coordinate in triangle.coordinates:
        #        #print coordinate

        # t4: translate the triangle to the definitive coordinate
        t4 = Translation(triangle1.center)
        #print "AFTER T4"
        #for triangle in triangles:
        #    #print "-------"
        #    for coordinate in triangle.coordinates:
        #        #print coordinate

        return t4*r3*r2*t1

    def compute_transformations(self):
        Scanner.compute_transformations(self)
        if self.allow_inversions:
            # derive the connections with inversion rotations, based on those
            # without inversion rotations
            new_connections = []
            maximum = len(self.connections)
            for progress, connection in enumerate(self.connections):
                self.send(ProgressMessage("mirror", progress, maximum))
                new = copy.deepcopy(connection)
                mirror = (
                    Translation(connection.triangle1.center)*
                    Rotation.from_properties(numpy.pi, connection.triangle1.normal, True)*
                    Translation(-connection.triangle1.center)
                )
                new.set_transformation(mirror*new.transformation)
                new_connections.append(new)
            self.connections.extend(new_connections)
            self.send(ProgressMessage("mirror", maximum, maximum))


