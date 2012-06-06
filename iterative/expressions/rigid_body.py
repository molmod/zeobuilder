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


from base import Terminus, Constraint, Helper
from iterative.variables.rigid_body import Frame, Translation

import numpy


__all__ = ["Orthonormality", "NoFrame", "Spring"]


class Error(Exception):
    pass


class Orthonormality(Constraint):
    output_dimension = 6

    def register_input_variable(self, variable):
        assert isinstance(variable, Frame), "An orthonormality constraint only supports a Frame variable."
        Constraint.register_input_variable(self, variable)

    def sanity_check(self):
        assert len(self.input_variables) == 1, "An orthonormality expression only supports one variable."
        Constraint.sanity_check(self)

    def add_outputs(self):
        rotation_matrix = self.input_variables[0].rotation_matrix
        counter = 0
        for a in range(3):
            self.outputs[counter] += numpy.dot(rotation_matrix[:,a], rotation_matrix[:,a]) - 1
            counter += 1
            for b in range(a+1,3):
                self.outputs[counter] += numpy.dot(rotation_matrix[:,a], rotation_matrix[:,b])
                counter += 1

    def add_derivatives(self):
        rotation_matrix = self.input_variables[0].rotation_matrix
        derivatives_row_iter = iter(self.derivatives[0])
        for a in range(3):
            for b in range(a,3):
                current_derivatives_row = derivatives_row_iter.next()
                value_counter = 0
                for alpha in range(3):
                    for beta in range(3):
                        # here comes the calculation of the derivatives matrix elements:
                        if a==b:
                            if b==beta:
                                current_derivatives_row[value_counter] += 2 * rotation_matrix[alpha, beta]
                        else:
                            if a==beta:
                                current_derivatives_row[value_counter] += rotation_matrix[alpha, b]
                            elif b==beta:
                                current_derivatives_row[value_counter] += rotation_matrix[alpha, a]
                        # that were the elements
                        value_counter += 1


class NoFrame(object):
    def apply_vector(self, c):
        return c


class Spring(Terminus):
    output_dimension = 1

    def __init__(self, rest_length=0.0):
        Terminus.__init__(self)
        self.coordinates = []
        self.frames = []
        if rest_length < 0.0:
            raise Error("The rest length of a spring must be zero or positive.")
        self.rest_length = rest_length

    def register_input_variable(self, variable, coordinate):
        if not (isinstance(variable, Frame) or isinstance(variable, Translation) or isinstance(variable, NoFrame)):
            raise Error("Expression requires iterative.var.Frame or iterative.var.Translation as variable")
        self.coordinates.append(coordinate)
        self.frames.append(variable)
        if not isinstance(variable, NoFrame):
            variable.add_mass(coordinate)
            Terminus.register_input_variable(self, variable)

    def sanity_check(self):
        if len(self.frames) != 2:
            raise Error("A Spring expression needs two frames.")
        if len(self.input_variables) > 2:
            raise Error("A Spring expression needs at most two input_variables.")
        if len(self.coordinates) != 2:
            raise Error("A Spring energy term must have two coordinates.")
        Terminus.sanity_check(self)

    def add_outputs(self):
        frame1, frame2 = self.frames
        coordinate1, coordinate2 = self.coordinates
        relative_vector = 0.0
        relative_vector = (
            frame1.apply_vector(coordinate1)
           -frame2.apply_vector(coordinate2)
        )
        self.outputs[0] += (numpy.linalg.norm(relative_vector) - self.rest_length)**2

    def add_derivatives(self):
        def helper(fa, fb, ca, cb):
            if self.rest_length == 0.0:
                alpha_column = 2 * (fa.apply_vector(ca) - fb.apply_vector(cb))
            else:
                delta = fa.apply_vector(ca) - fb.apply_vector(cb)
                norm = numpy.linalg.norm(delta)
                if norm > 0:
                    alpha_column = 2 * delta*(norm - self.rest_length)/norm
                else:
                    alpha_column = 2 * delta*(norm - self.rest_length)

            current_index = 0
            if not isinstance(fa, NoFrame):
                if isinstance(fa, Frame):
                    for alpha in range(3):
                        fa.derivatives[current_index:current_index+3] += alpha_column[alpha] * ca
                        current_index += 3
                fa.derivatives[current_index:current_index+3] += alpha_column

        frame1, frame2 = self.frames
        coordinate1, coordinate2 = self.coordinates
        helper(frame1, frame2, coordinate1, coordinate2)
        helper(frame2, frame1, coordinate2, coordinate1)






