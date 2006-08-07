# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2005 Toon Verstraelen
#
# This file is part of Zeobuilder.
#
# Zeobuilder is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# --

from zeobuilder.transformations import Complete

import numpy, copy, random, math
import unittest


__all__ = ["Apply"]


class Apply(unittest.TestCase):
    def setUp(self):
        self.test_transformations = []
        for i in xrange(20):
            test_transformation = Complete()
            test_transformation.set_rotation_properties(random.random()*math.pi*2, numpy.random.uniform(-3, 3, 3), random.sample([True, False], 1)[0])
            test_transformation.translation_vector = numpy.random.uniform(-3, 3, 3)
            self.test_transformations.append(test_transformation)

    def test_apply_after(self):
        for tt1 in self.test_transformations:
            for tt2 in self.test_transformations:
                temp = copy.deepcopy(tt1)
                temp.apply_after(tt2)
                rotation_matrix = numpy.dot(tt2.rotation_matrix, tt1.rotation_matrix)
                rotation_error = numpy.sum(numpy.ravel((rotation_matrix - temp.rotation_matrix)**2))/9.0
                self.assertAlmostEqual(rotation_error, 0)
                translation_vector = numpy.dot(tt2.rotation_matrix, tt1.translation_vector) + tt2.translation_vector
                translation_error = numpy.sum((translation_vector - temp.translation_vector)**2)/3.0
                self.assertAlmostEqual(translation_error, 0)

    def test_apply_before(self):
        for tt1 in self.test_transformations:
            for tt2 in self.test_transformations:
                temp = copy.deepcopy(tt1)
                temp.apply_before(tt2)
                rotation_matrix = numpy.dot(tt1.rotation_matrix, tt2.rotation_matrix)
                rotation_error = numpy.sum(numpy.ravel((rotation_matrix - temp.rotation_matrix)**2))/9.0
                self.assertAlmostEqual(rotation_error, 0)
                translation_vector = numpy.dot(tt1.rotation_matrix, tt2.translation_vector) + tt1.translation_vector
                translation_error = numpy.sum((translation_vector - temp.translation_vector)**2)/3.0
                self.assertAlmostEqual(translation_error, 0)

    def test_apply_inverse_after(self):
        for tt1 in self.test_transformations:
            for tt2 in self.test_transformations:
                temp = copy.deepcopy(tt1)
                temp.apply_inverse_after(tt2)
                rotation_matrix = numpy.dot(numpy.transpose(tt2.rotation_matrix), tt1.rotation_matrix)
                rotation_error = numpy.sum(numpy.ravel((rotation_matrix - temp.rotation_matrix)**2))/9.0
                self.assertAlmostEqual(rotation_error, 0)
                translation_vector = numpy.dot(numpy.transpose(tt2.rotation_matrix), tt1.translation_vector - tt2.translation_vector)
                translation_error = numpy.sum((translation_vector - temp.translation_vector)**2)/3.0
                self.assertAlmostEqual(translation_error, 0)

    def test_apply_inverse_before(self):
        for tt1 in self.test_transformations:
            for tt2 in self.test_transformations:
                temp = copy.deepcopy(tt1)
                temp.apply_inverse_before(tt2)
                rotation_matrix = numpy.dot(tt1.rotation_matrix, numpy.transpose(tt2.rotation_matrix))
                rotation_error = numpy.sum(numpy.ravel((rotation_matrix - temp.rotation_matrix)**2))/9.0
                self.assertAlmostEqual(rotation_error, 0)
                translation_vector = numpy.dot(tt1.rotation_matrix, -numpy.dot(numpy.transpose(tt2.rotation_matrix), tt2.translation_vector)) + tt1.translation_vector
                translation_error = numpy.sum((translation_vector - temp.translation_vector)**2)/3.0
                self.assertAlmostEqual(translation_error, 0)

