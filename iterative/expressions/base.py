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


from molmod.clusters import ClusterFactory, RuleCluster

import numpy

import copy


__all__ = [
    "Base", "RootMixin", "SanityError", "TerminusMixin", "CircularDependence",
    "ShakeError", "Root", "Helper", "Terminus", "Constraint",
]



class ShakeError(Exception):
    pass


class CircularDependence(Exception):
    pass


class SanityError(Exception):
    pass


#
# Base Class
#


class Base(object):
    output_dimension = 0

    def __init__(self):
        assert self.output_dimension == None or self.output_dimension > 0, "The output_dimension of an expression must be strictly positive."
        self.outputs = None

    def add_outputs(self):
        raise NotImplementedError

    def add_derivatives(self):
        raise NotImplementedError


#
# Mixin classes
#


class RootMixin(object):
    def __init__(self):
        self.state_variables = []
        self.state = None
        self.state_dimension = 0
        self.derivatives = None
        self.dependent_expressions = set([])

    def assert_no_circular_dependencies(self, parent_expressions=None):
        if parent_expressions == None:
            parent_expressions = set([])
        elif self in parent_expressions:
            raise CircularDependence
        new_parent_expressions = copy.copy(parent_expressions)
        new_parent_expressions.add(self)
        for dependent_expression in self.dependent_expressions:
            if isinstance(dependent_expression, RootMixin):
                dependent_expression.assert_no_circular_dependencies(new_parent_expressions)

    def clear_derivatives(self):
        self.derivatives[:] = 0.0



class TerminusMixin(object):
    def __init__(self):
        self.input_variables = []
        self.parent_expressions = set([])

    def register_input_variable(self, variable):
        self.input_variables.append(variable)
        variable.parent_expression.dependent_expressions.add(self)
        self.parent_expressions.add(variable.parent_expression)

    def sanity_check(self):
        if len(self.input_variables) == 0:
            raise ValueError, "A TerminusMixin must have input."


#
# Elementary classes
#


class Root(Base, RootMixin):
    def __init__(self, output_dimension, max_num_shakes=5, constrain_derivatives=True):
        # set the output_dimension
        self.output_dimension = output_dimension
        # call the ancestors
        Base.__init__(self)
        RootMixin.__init__(self)
        # set the parameters
        self.max_num_shakes = max_num_shakes
        self.constrain_derivatives = constrain_derivatives
        # lists that will contain the dependent sub expressions
        self.sub_expressions = []
        self.helpers = []
        self.termini = []
        self.constraints = []

    def register_state_variable(self, variable):
        self.state_variables.append(variable)
        self.state_dimension += variable.dimension
        variable.parent_expression = self

    def parse_input(self):
        self.assert_no_circular_dependencies()
        self.sort_sub_expressions()
        self.sanity_check()
        self.allocate()
        self.connect()

    def sort_sub_expressions(self):
        # the expressions will be sorted so that we do not need extensive and
        # complex recursive algorithms
        # create dependencies
        dependencies = {self: set([])}
        former_expressions = set(self.dependent_expressions)
        while len(former_expressions) > 0:
            new_expressions = set([])
            for expression in former_expressions:
                if isinstance(expression, TerminusMixin):
                    if expression not in dependencies:
                        dependencies[expression] = set([])
                    dependencies[expression] |= expression.parent_expressions
                    for parent_expression in expression.parent_expressions:
                        dependencies[expression] |= dependencies[parent_expression]
                if isinstance(expression, RootMixin):
                    new_expressions |= expression.dependent_expressions
            former_expressions = new_expressions
        del dependencies[self]
        # sort the expressions
        def compare_function(expression1, expression2):
            if expression2 in dependencies[expression1]: return 1
            elif expression1 in dependencies[expression2]: return -1
            else: return 0
        self.sub_expressions = dependencies.keys()
        self.sub_expressions.sort(compare_function)
        # divide them in categories
        for expression in self.sub_expressions:
            if isinstance(expression, Helper):
                self.helpers.append(expression)
            elif isinstance(expression, Terminus):
                self.termini.append(expression)
            elif isinstance(expression, Constraint):
                self.constraints.append(expression)

    def sanity_check(self):
        if len(self.state_variables) == 0:
            raise SanityError("A RootMixin expression must have state variables.")
        for variable in self.state_variables:
            variable.sanity_check()
        for expression in self.sub_expressions:
            expression.sanity_check()
        for terminus in self.termini:
            if terminus.output_dimension != self.output_dimension:
                raise SanityError("All termini must have the same output_dimension as the root expression.")
        for constraint in self.constraints:
            if len(constraint.parent_expressions) != 1 or iter(constraint.parent_expressions).next() != self:
                raise SanityError("All constraints can have only the root_expression as their parent_expression.")

    def allocate(self):
        self.state = numpy.zeros(self.state_dimension, float)
        self.derivatives = numpy.zeros(self.state_dimension, float)
        self.mass = numpy.zeros(self.state_dimension, float)
        self.outputs = numpy.zeros(self.output_dimension, float)
        for helper in self.helpers:
            helper.allocate_state_variables()

    def connect(self):
        self.connect_state_variables()
        for helper in self.helpers:
            helper.connect_state_variables()
        for terminus in self.termini:
            terminus.connect_outputs(self.outputs)

    def connect_state_variables(self):
        # before we connect the state variables, we must assign indices to
        # the variables. This is regulated by the constraints that apply.

        # first cluster the variables into groups. They are grouped by the constraints.
        # for example: constraint A(1, 2) and B(2, 3) will make variables 1, 2, 3 related
        # trhough the constraintderivatives matrix. All nonrelated variables will be put together
        # at the end of the state vector.
        cf = ClusterFactory(RuleCluster)
        for constraint in self.constraints:
            cf.add_related(RuleCluster(constraint.input_variables, [constraint]))
        self.constraint_clusters = cf.get_clusters()
        del cf

        # assign state indices to the variables
        state_index = 0
        excess_index = 0
        self.unconstrained_variables = set(self.state_variables)
        for cluster in self.constraint_clusters:
            cluster.state_index = state_index
            for variable in cluster.items:
                self.unconstrained_variables.remove(variable)
                variable.state_index = state_index
                state_index += variable.dimension
            cluster.input_dimension = sum([variable.dimension for variable in cluster.items])
            cluster.output_dimension = sum([constraint.output_dimension for constraint in cluster.rules])
            cluster.inputs = self.state[cluster.state_index: cluster.state_index + cluster.input_dimension]
            cluster.state_derivatives = self.derivatives[cluster.state_index: cluster.state_index + cluster.input_dimension]
            cluster.outputs = numpy.zeros(cluster.output_dimension, float)
            cluster.constraint_derivatives = numpy.zeros((cluster.output_dimension, cluster.input_dimension), float)
            output_index = 0
            for constraint in cluster.rules:
                constraint.sanity_check()
                constraint.connect_outputs(output_index, cluster.outputs)
                constraint.connect_derivatives([
                    cluster.constraint_derivatives[
                        output_index: output_index + constraint.output_dimension,
                        variable.state_index - cluster.state_index: variable.state_index - cluster.state_index + variable.dimension
                    ] for variable in constraint.input_variables
                ])
                output_index += constraint.output_dimension

        for variable in self.unconstrained_variables:
            variable.state_index = state_index
            state_index += variable.dimension

        for variable in self.state_variables:
            variable.connect(self.state, self.derivatives, self.mass)

    def get_state_indices(self):
        return numpy.array([variable.state_index for variable in self.state_variables], int)

    def clear(self):
        RootMixin.clear_derivatives(self)
        for helper in self.helpers:
            helper.clear()
        self.clear_outputs()

    def clear_outputs(self):
        self.outputs[:] = 0.0

    def add_outputs(self):
        for helper in self.helpers:
            helper.calculate_state()
        for terminus in self.termini:
            terminus.add_outputs()

    def add_derivatives(self):
        for terminus in self.termini:
            terminus.add_derivatives()
        for helper in self.helpers[::-1]:
            helper.transform_derivatives()
        if self.constrain_derivatives:
            for cluster in self.constraint_clusters:
                for constraint in cluster.rules:
                    constraint.clear()
                    constraint.add_derivatives()
                # project the derivative vector on the space spanned by the
                # tangents (derivatives) of the constraint functions.
                ortho_move = numpy.dot(cluster.constraint_derivatives, numpy.transpose(cluster.constraint_derivatives))
                x,resids,rank,s = numpy.linalg.lstsq(cluster.constraint_derivatives.transpose(), cluster.state_derivatives)
                cluster.state_derivatives[:] -= numpy.dot(cluster.constraint_derivatives.transpose(), x)

    def shake(self):
        # returns the mean number of shakes per constraint cluster
        if len(self.constraint_clusters) == 0: return 0
        total_num_shakes = 0
        # nr stands for newton-raphson
        for cluster in self.constraint_clusters:
            num_shakes = 0
            while True:
                converged = True
                for constraint in cluster.rules:
                    constraint.clear()
                    constraint.add_outputs()
                    converged &= constraint.converged()
                if converged: break
                for constraint in cluster.rules:
                    constraint.add_derivatives()

                ortho_move = numpy.dot(cluster.constraint_derivatives, numpy.transpose(cluster.constraint_derivatives))
                delta_mu = -numpy.linalg.solve(ortho_move, cluster.outputs)
                cluster.inputs += numpy.dot(numpy.transpose(cluster.constraint_derivatives), delta_mu)
                num_shakes += 1
                if num_shakes > self.max_num_shakes:
                    raise ShakeError("The number of NR corrections exceeded the given limit (%i). This probably means that the step size is too large." % (self.max_num_shakes))
            total_num_shakes += num_shakes
        return total_num_shakes


class Helper(RootMixin, TerminusMixin):
    def __init__(self):
        RootMixin.__init__(self)
        TerminusMixin.__init__(self)

    def allocate_state_variables(self):
        self.state_dimension = sum(variable.dimension for variable in self.state_variables)
        self.state = numpy.zeros(self.state_dimension, float)
        self.derivatives = numpy.zeros(self.state_dimension, float)
        self.mass = numpy.zeros(self.state_dimension, float)

    def connect_state_variables(self):
        state_index = 0
        for variable in self.state_variables:
            variable.state_index = state_index
            variable.connect(self.state, self.derivatives, self.mass)
            state_index += variable.dimension

    #def calculate_state(self):
    #    raise NotImplementedError

    #def transform_derivatives(self):
    #    raise NotImplementedError


class Terminus(Base, TerminusMixin):
    def __init__(self):
        Base.__init__(self)
        TerminusMixin.__init__(self)

    def connect_outputs(self, outputs):
        self.outputs = outputs


class Constraint(Base, TerminusMixin):
    def __init__(self, convergence_threshold):
        Base.__init__(self)
        TerminusMixin.__init__(self)
        self.convergence_threshold2 = convergence_threshold**2

    def connect_outputs(self, output_index, outputs):
        self.outputs = outputs[output_index: output_index + self.output_dimension]

    def connect_derivatives(self, derivatives):
        self.derivatives = derivatives

    def clear(self):
        self.outputs[:] = 0.0
        for matrix in self.derivatives:
            matrix[:] = 0.0

    def converged(self):
        return (numpy.dot(self.outputs, self.outputs) / self.output_dimension) < self.convergence_threshold2




