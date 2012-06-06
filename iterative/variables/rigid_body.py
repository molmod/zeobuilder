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


from base import Variable, Helper, SanityError

import numpy


__all__ = ["Frame", "Translation"]


class Frame(Variable):
    dimension = 12

    def __init__(self, rotation_matrix, translation_vector):
        Variable.__init__(self)
        self.rotation_matrix = rotation_matrix
        self.translation_vector = translation_vector
        self.inertia_tensor = numpy.zeros((3,3), float)
        self.inertia_mass = numpy.zeros(3, float)

    def add_mass(self, coordinate):
        self.inertia_tensor += numpy.dot(coordinate, coordinate) - numpy.outer(coordinate, coordinate)
        self.inertia_mass += 1

    def sanity_check(self):
        Variable.sanity_check(self)
        if self.rotation_matrix.shape != (3,3):
            raise SanityError("The rotation_matrix must be a 3x3 matrix. The given array hase shape %s." % self.rotation_matrix.shape)
        if self.translation_vector.shape != (3,):
            raise SanityError("The translation_vector must be a vector of length 3. The given array has  shape=%s." % self.translation_vector.shape)

    def connect(self, state, derivatives, mass):
        Variable.connect(self, state, derivatives, mass)
        self.state[0: 9] = self.rotation_matrix.ravel()
        self.rotation_matrix = numpy.reshape(self.state[0: 9], (3,3))
        self.state[9: 12] = self.translation_vector
        self.translation_vector = self.state[9: 12]
        self.mass[0: 9] = self.inertia_tensor.ravel()
        self.inertia_tensor = numpy.reshape(self.mass[0: 9], (3,3))
        self.mass[9: 12] = self.inertia_mass
        self.inertia_mass = self.mass[9: 12]

    def extract_state(self, state_index, state):
        return numpy.reshape(state[state_index: state_index+9], (3,3)), state[state_index+9: state_index+12]

    def apply_vector(self, vector):
        return numpy.dot(self.rotation_matrix, vector) + self.translation_vector


class Translation(Variable):
    dimension = 3

    def __init__(self, rotation_matrix, translation_vector):
        Variable.__init__(self)
        self.rotation_matrix = rotation_matrix
        self.translation_vector = translation_vector
        self.inertia_mass = numpy.zeros(3, float)

    def add_mass(self, coordinate):
        self.inertia_mass += 1

    def sanity_check(self):
        Variable.sanity_check(self)
        if self.translation_vector.shape != (3,):
            raise SanityError("The translation_vector must be a vector of length 3. The given array has  shape=%s." % self.translation_vector.shape)

    def connect(self, state, derivatives, mass):
        Variable.connect(self, state, derivatives, mass)
        self.state[:] = self.translation_vector
        self.translation_vector = self.state
        self.mass[:] = self.inertia_mass
        self.inertia_mass = self.mass

    def extract_state(self, state_index, state):
        return state[state_index: state_index+3]

    def apply_vector(self, vector):
        return numpy.dot(self.rotation_matrix, vector) + self.translation_vector




