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


from base import Algorithm
from iterative.stop_criteria import SmallStep

import math, numpy, sys


__all__ = [
    "Minimize", "SteepestDescent", "ConjugateGradient", "DefaultMinimize"
]


class Minimize(Algorithm):
    def __init__(self, root_expression, max_step, step_threshold):
        assert root_expression.output_dimension == 1, "One can only minimize one variable at a time."
        Algorithm.__init__(self, root_expression, SmallStep(step_threshold))
        self.max_step = max_step

    def initialize(self):
        self.root_expression.clear()

    def finalize(self):
        pass

    def limit_step(self, step):
        step /= self.max_step
        norm = numpy.linalg.norm(step)
        if norm > 1:
            step /= numpy.linalg.norm(step)
        step *= self.max_step

    def line_search(self, step):
        """Shrinks the step size until a lower output value is encountered.

        If the step becomes smaller than a threshold step, the iteration
        will be interupted.
        """
        self.limit_step(step)
        self.status.num_shakes = 0

        self.root_expression.clear_outputs()
        self.root_expression.add_outputs()
        self.original_state = self.root_expression.state.copy()
        self.original_value = self.root_expression.outputs[0]

        stop = True
        while not self.stop_criterion(step):
            self.root_expression.state[:] = self.original_state + step
            self.status.num_shakes += self.root_expression.shake()
            self.root_expression.clear_outputs()
            self.root_expression.add_outputs()
            if self.original_value > self.root_expression.outputs[0]:
                stop = False
                break
            else:
                self.root_expression.state[:] = self.original_state
                self.root_expression.outputs[0] = self.original_value
            step *= 0.5
        self.status.progress = self.stop_criterion.get_fraction()
        self.status.value = self.root_expression.outputs[0]
        return stop


class SteepestDescent(Minimize):
    def iterate(self):
        self.root_expression.clear_derivatives()
        self.root_expression.add_derivatives()
        step = -self.root_expression.derivatives/self.root_expression.mass
        stop = self.line_search(step)

        self.status.progress = self.stop_criterion.get_fraction()
        self.status.value = self.root_expression.outputs[0]

        return stop


class ConjugateGradient(Minimize):
    def initialize(self):
        Minimize.initialize(self)
        self.root_expression.clear_derivatives()
        self.root_expression.add_derivatives()
        self.gradient = self.root_expression.derivatives.copy()
        self.direction = -self.gradient.copy() # direction is negative of conjugate gradient

        self.delta_gradient = numpy.zeros(self.gradient.shape, float)
        self.backup = numpy.zeros(self.root_expression.state.shape, float)

    def iterate(self):
        # obtain the 'second order derivative in the search direction' numerically,
        # ~= numpy.dot(direction, numpy.dot(hessian, direction))
        epsilon = 1e-12
        self.backup[:] = self.root_expression.state
        self.root_expression.state[:] += self.direction/numpy.linalg.norm(self.direction)*epsilon
        self.root_expression.clear_derivatives()
        self.root_expression.add_derivatives()
        self.delta_gradient[:] = self.root_expression.derivatives
        curvature = numpy.dot(self.direction, (self.delta_gradient-self.gradient))/epsilon
        self.root_expression.state[:] = self.backup

        if curvature <= 0:
            step = -self.gradient/numpy.linalg.norm(self.gradient)
            stop = self.line_search(step)

            if stop: return True

            self.root_expression.clear_derivatives()
            self.root_expression.add_derivatives()
            self.gradient[:] = self.root_expression.derivatives
            self.direction[:] = -self.gradient
        else:
            alpha = numpy.dot(self.gradient, self.gradient)/curvature

            step = alpha*self.direction/numpy.linalg.norm(self.direction)
            stop = self.line_search(step)

            if stop: return True

            self.root_expression.clear_derivatives()
            self.root_expression.add_derivatives()
            new_gradient = self.root_expression.derivatives

            beta = (
                numpy.dot(new_gradient, new_gradient - self.gradient)/
                numpy.dot(self.gradient, self.gradient)
            )
            self.gradient[:] = new_gradient
            self.direction *= beta
            self.direction -= self.gradient

        return False


DefaultMinimize = ConjugateGradient




