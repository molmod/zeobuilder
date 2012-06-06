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


import iterative

import numpy


def define_cost_function1():
    cost_function = iterative.expr.Root(1, 5, True)

    frame1 = iterative.var.Frame(
        numpy.array([
            [ 1.0,  0.0,  0.0],
            [ 0.0,  1.0,  0.0],
            [ 0.0,  0.0,  1.0],
        ], float),
        numpy.array([1.0, 0.0, 0.0], float)
    )
    cost_function.register_state_variable(frame1)
    constraint1 = iterative.expr.Orthonormality(1e-6)
    constraint1.register_input_variable(frame1)

    frame2 = iterative.var.Frame(
        numpy.array([
            [ 0.0, -1.0 , 0.0],
            [ 1.0,  0.0,  0.0],
            [ 0.0,  0.0,  1.0],
        ], float),
        numpy.array([0.0, 0.0, -3.0], float)
    )
    cost_function.register_state_variable(frame2)
    constraint2 = iterative.expr.Orthonormality(1e-6)
    constraint2.register_input_variable(frame2)

    spring1 = iterative.expr.Spring(0.5)
    spring1.register_input_variable(frame1, numpy.array([ 0.0,  2.0,  1.2]))
    spring1.register_input_variable(frame2, numpy.array([-3.0,  2.0,  1.2]))

    spring2 = iterative.expr.Spring(0.5)
    spring2.register_input_variable(frame1, numpy.array([-1.0,  0.5,  0.0]))
    spring2.register_input_variable(frame2, numpy.array([ 0.0, -1.2,  0.5]))

    spring3 = iterative.expr.Spring(0.5)
    spring3.register_input_variable(frame1, numpy.array([ 0.7, -2.0, -0.3]))
    spring3.register_input_variable(frame2, numpy.array([ 1.5,  0.0, -2.7]))

    spring4 = iterative.expr.Spring(0.2)
    spring4.register_input_variable(iterative.expr.NoFrame(), numpy.array([ 0.7, -2.0, -0.3]))
    spring4.register_input_variable(frame2, numpy.array([ 1.5,  0.0, -2.7]))

    cost_function.parse_input()
    return cost_function


def define_cost_function2():
    cost_function = iterative.expr.Root(1, 5, True)

    frame1 = iterative.var.Translation(
        numpy.array([
            [ 1.0,  0.0,  0.0],
            [ 0.0,  1.0,  0.0],
            [ 0.0,  0.0,  1.0],
        ], float),
        numpy.array([1.0, 0.0, 0.0], float)
    )
    cost_function.register_state_variable(frame1)

    frame2 = iterative.var.Translation(
        numpy.array([
            [ 0.0, -1.0 , 0.0],
            [ 1.0,  0.0,  0.0],
            [ 0.0,  0.0,  1.0],
        ], float),
        numpy.array([0.0, 0.0, -3.0], float)
    )
    cost_function.register_state_variable(frame2)

    spring1 = iterative.expr.Spring(0.5)
    spring1.register_input_variable(frame1, numpy.array([ 0.0,  2.0,  1.2]))
    spring1.register_input_variable(frame2, numpy.array([-3.0,  2.0,  1.2]))

    spring2 = iterative.expr.Spring(0.5)
    spring2.register_input_variable(frame1, numpy.array([-1.0,  0.5,  0.0]))
    spring2.register_input_variable(frame2, numpy.array([ 0.0, -1.2,  0.5]))

    spring3 = iterative.expr.Spring(0.5)
    spring3.register_input_variable(frame1, numpy.array([ 0.7, -2.0, -0.3]))
    spring3.register_input_variable(frame2, numpy.array([ 1.5,  0.0, -2.7]))

    spring4 = iterative.expr.Spring(0.2)
    spring4.register_input_variable(iterative.expr.NoFrame(), numpy.array([ 0.7, -2.0, -0.3]))
    spring4.register_input_variable(frame2, numpy.array([ 1.5,  0.0, -2.7]))

    cost_function.parse_input()
    return cost_function


def report(status):
    pass
    #print status.step, status.value
    #for key, val in status.__dict__.iteritems():
    #    print "% 20s:  %s" % (key, val)
    #print "-"*100


def test_minimize_noincrease1_steepest_descent():
    cost_function = define_cost_function1()

    minimize = iterative.alg.SteepestDescent(
        cost_function,
        numpy.array([0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 1.0, 1.0, 1.0]*2, float),
        1e-5,
    )
    minimize.run(report)


def test_minimize_noincrease1_conjugate_gradient():
    cost_function = define_cost_function1()

    minimize = iterative.alg.ConjugateGradient(
        cost_function,
        numpy.array([0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 1.0, 1.0, 1.0]*2, float),
        1e-5,
    )
    minimize.run(report)


def test_minimize_noincrease2_steepest_descent():
    cost_function = define_cost_function2()

    minimize = iterative.alg.SteepestDescent(
        cost_function,
        numpy.array([1.0, 1.0, 1.0]*2, float),
        1e-5,
    )
    minimize.run(report)


def test_minimize_noincrease2_conjugate_gradient():
    cost_function = define_cost_function2()

    minimize = iterative.alg.ConjugateGradient(
        cost_function,
        numpy.array([1.0, 1.0, 1.0]*2, float),
        1e-5,
    )
    minimize.run(report)


def test_constraint_derivatives():
    expr = define_cost_function1()

    expr.constrain_derivatives = False
    expr.clear()
    expr.add_derivatives()
    a = expr.derivatives.copy()

    expr.constrain_derivatives = True
    expr.clear()
    expr.add_derivatives()
    b = expr.derivatives.copy()

    drel = ((a - b)**2).sum()/(numpy.linalg.norm(a)*numpy.linalg.norm(b))
    assert drel > 1e-5

    for cluster in expr.constraint_clusters:
        for constraint in cluster.rules:
            constraint.clear()
            constraint.add_derivatives()
        # project the derivative vector on the space spanned by the
        # tangents (derivatives) of the constraint functions.
        overlap = (numpy.dot(cluster.constraint_derivatives, cluster.state_derivatives)**2).sum()
        assert overlap < 1e-5

