# Iterative is a toolkit for iterative algorithms on a set of state variables.
# Copyright (C) 2007 - 2008 Toon Verstraelen <Toon.Verstraelen@UGent.be>
#
# This file is part of Iterative.
#
# Iterative is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# Iterative is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
# --


import numpy, sys


class Criterion(object):
    def __call__(self, expression):
        raise NotImplementedError

    def __call__(self, expression):
        raise NotImplementedError


class AtLeastOne(Criterion):
    def __init__(self, criteria):
        self.criteria = criteria

    def __call__(self, expressions):
        for criterion in self.criteria:
            if criterion(expressions):
                return True
        return False

    def get_fraction(self):
        maximum = 0.0
        for criterion in self.criteria:
            fraction = self.criterion.get_fraction()
            if fraction > maximum:
                maximum = fraction
        return maximum


class AllOfThem(Criterion):
    def __init__(self, criteria):
        self.criteria = criteria

    def __call__(self, expressions):
        for criterion in self.criteria:
            if not criterion(expressions):
                return False
        return True

    def get_fraction(self):
        minimum = 1.0
        for criterion in self.criteria:
            fraction = self.criterion.get_fraction()
            if fraction < minimum:
                minimum = fraction
        return minimum


class NoIncrease(Criterion):
    def __init__(self):
        self.last = None
        self.next_to_last = None
        self.reference = None
        self.decrease = None

    def __call__(self, expression):
        self.next_to_last = self.last
        self.last = expression.outputs[0]
        if self.next_to_last is not None:
            self.decrease = self.next_to_last - self.last
            if self.reference is None:
                self.reference = abs(self.decrease)
            return self.decrease < 0
        else:
            return False

    def get_fraction(self):
        if self.reference is None:
            return 0.0
        else:
            result = 1 - self.decrease / self.reference
            if result > 1: result = 1
            if result < 0: result = 0
            return result


class LowGradient(Criterion):
    def __init__(self, threshold=1e-5):
        self.threshold = threshold
        self.first = None
        self.current = None

    def __call__(self, expression):
        self.current = abs(expression.derivatives).max()
        if self.first is None:
            self.first = self.current
        return abs(expression.derivatives).max() < self.threshold

    def get_fraction(self):
        if self.first is None:
            return 0
        else:
            result = (
                (numpy.log(self.current) - numpy.log(self.first))/
                (numpy.log(self.threshold) - numpy.log(self.first))
            )
            if result > 1: result = 1
            return result


class SmallStep(Criterion):
    def __init__(self, threshold):
        self.threshold = numpy.linalg.norm(threshold)
        self.first = None
        self.current = None

    def __call__(self, step):
        self.current = numpy.linalg.norm(step)
        if self.first is None or self.first < self.current:
            self.first = self.current
        return (self.current < self.threshold).all()

    def get_fraction(self):
        if self.first is None:
            return 0
        else:
            result = (
                (numpy.log(abs(self.current  )) - numpy.log(abs(self.first)))/
                (numpy.log(    self.threshold ) - numpy.log(abs(self.first)))
            ).min()
            if result > 1: result = 1
            return result


class IncreaseNSteps(Criterion):
    def __init__(self, max_steps):
        self.max_steps = max_steps
        self.steps = 0
        self.last = None
        self.next_to_last = None
        self.reference = None
        self.decrease = None

    def __call__(self, expression):
        self.next_to_last = self.last
        self.last = expression.outputs[0]
        if self.next_to_last is not None:
            self.decrease = self.next_to_last - self.last
            if self.reference is None:
                self.reference = abs(self.decrease)
            if self.decrease < 0:
                self.steps += 1
                return self.max_steps < self.steps
            else:
                self.steps = 0
        return False

    def get_fraction(self):
        if self.reference is None:
            return 0.0
        else:
            result = 1 - self.decrease / self.reference
            if result > 1: result = 1
            if result < 0: result = 0
            result =  0.5*(result + float(self.steps) / self.max_steps)
            if result > 1: result = 1
            return result


class NSteps(Criterion):
    def __init__(self, max_steps):
        self.steps = 0
        self.max_steps = max_steps
        assert max_steps > 0

    def __call__(self, expression):
        self.steps += 1
        return self.max_steps < self.steps

    def get_fraction(self):
        result = float(self.steps) / self.max_steps
        if result > 1: result = 1
        return result




