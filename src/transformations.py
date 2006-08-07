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


from OpenGL.GL import *
import numpy

import math


__all__ = ["Base", "Translation", "Rotation", "Complete"]


class Base(object):
    def clear(self):
        raise NotImplementedError

    def from_matrix(self, matrix):
        raise NotImplementedError

    def get_matrix(self):
        raise NotImplementedError

    def get_inverse_matrix(self):
        raise NotImplementedError

    def gl_apply(self):
        raise NotImplementedError

    def gl_apply_inverse(self):
        raise NotImplementedError

    def gl_from_matrix(self, GL_MATRIX):
        # transpose because opengl=column-major and numpy=row-major
        self.from_matrix(numpy.array(glGetFloatv(GL_MATRIX), float).transpose())

    def invert(self):
        raise NotImplementedError

    def vector_apply(self, v):
        raise NotImplementedError

    def vector_apply_inverse(self, v):
        raise NotImplementedError

    def vector_apply_translation(self, v):
        raise NotImplementedError

    def matrix_apply_before(self, m):
        raise NotImplementedError

    def matrix_apply_inverse_before(self, m):
        raise NotImplementedError

    def matrix_apply_after(self, m):
        raise NotImplementedError

    def matrix_apply_inverse_after(self, m):
        raise NotImplementedError

    def apply_after(self, parent): # self -> parent AFTER self
        raise NotImplementedError

    def apply_inverse_after(self, parent): # self -> !parent AFTER self
        raise NotImplementedError

    def apply_before(self, child): # self -> self AFTER child
        raise NotImplementedError

    def apply_inverse_before(self, child): # self -> self AFTER !child
        raise NotImplementedError

    def compare(self, other, translation_threshold=1e-3, rotation_threshold=1e-3):
        raise NotImplementedError

    def assign_shallow(self, other):
        raise NotImplementedError


class Translation(Base):
    def __init__(self):
        self.translation_vector = numpy.zeros(3, float)

    def __str__(self):
        result = "TRANSLATION\n"
        for i in range(3):
            result += "% 10.7f\n" % self.translation_vector[i]
        return result

    def clear(self):
        self.translation_vector[:] = 0

    def from_matrix(self, m):
        # check wether the translation_vector part is ok
        z = m[3, 0:3]
        numpy.power(z,2,z)
        assert max(z) < 1.0e-6, "The given matrix doesn't have correct translational part"
        assert m[3,3] == 1.0, "The lower right element of the given matrix must be 1.0."
        # get the translational part
        self.translation_vector[:] = m[0:3, 3]

    def get_matrix(self):
        temp = numpy.identity(4, float)
        temp[0:3, 3] = self.translation_vector
        return temp

    def get_inverse_matrix(self):
        temp = numpy.identity(4, float)
        temp[0:3, 3] = -self.translation_vector
        return temp

    def gl_apply(self):
        glTranslate(self.translation_vector[0], self.translation_vector[1], self.translation_vector[2])

    def gl_apply_inverse(self):
        glTranslate(-self.translation_vector[0], -self.translation_vector[1], -self.translation_vector[2])

    def invert(self):
        self.translation_vector *= -1

    def vector_apply(self, v):
        return v + self.translation_vector

    def vector_apply_inverse(self, v):
        return v - self.translation_vector

    def vector_apply_translation(self, v):
        return v + self.translation_vector

    def matrix_apply_before(self, m):
        return m

    def matrix_apply_inverse_before(self, m):
        return m

    def matrix_apply_after(self, m):
        return m

    def matrix_apply_inverse_after(self, m):
        return m

    def apply_after(self, parent): # self -> parent AFTER self
        self.translation_vector[:] = parent.vector_apply(self.translation_vector)

    def apply_inverse_after(self, parent): # self -> !parent AFTER self
        self.translation_vector[:] = parent.vector_apply_inverse(self.translation_vector)

    def apply_before(self, child): # self -> self AFTER child
        self.translation_vector[:] = self.vector_apply(child.vector_apply(numpy.zeros(3, float)))

    def apply_inverse_before(self, child): # self -> self AFTER !child
        self.translation_vector[:] = self.vector_apply(child.vector_apply_inverse(numpy.zeros(3, float)))

    def compare(self, other, translation_threshold=1e-3, rotation_threshold=1e-3):
        return numpy.sum((self.translation_vector - other.translation_vector)**2) < translation_threshold

    def assign_shallow(self, other):
        if isinstance(other, Translation):
            self.translation_vector[:] = other.translation_vector


class Rotation(Base):
    def __init__(self):
        self.rotation_matrix = numpy.identity(3, float)

    def __str__(self):
        result = "ROTATION\n"
        for i in range(3):
            result += "[ % 10.7f \t % 10.7f \t % 10.7f ]\n" % tuple(self.rotation_matrix[i])
        return result

    def clear(self):
        self.rotation_matrix[:] = 0
        self.rotation_matrix.ravel()[::4] = 1

    def from_matrix(self, m):
        self.rotation_matrix[:] = m[0:3, 0:3]

    def get_matrix(self):
        temp = numpy.identity(4, float)
        temp[0:3, 0:3] = self.rotation_matrix
        return temp

    def get_inverse_matrix(self):
        temp = numpy.identity(4, float)
        temp[0:3, 0:3] = self.rotation_matrix.transpose()
        return temp

    def gl_apply(self):
        temp = numpy.identity(4, float)
        temp[0:3, 0:3] = self.rotation_matrix.transpose()
        glMultMatrixf(temp)

    def gl_apply_inverse(self):
        temp = numpy.identity(4, float)
        temp[0:3, 0:3] = self.rotation_matrix
        glMultMatrixf(temp)

    def invert(self):
        self.rotation_matrix[:] = self.rotation_matrix.transpose()

    def inversion_rotation(self):
        self.rotation_matrix *= -1

    def vector_apply(self, v):
        return numpy.dot(self.rotation_matrix, v)

    def vector_apply_inverse(self, v):
        return numpy.dot(self.rotation_matrix.transpose(), v)

    def vector_apply_translation(self, v):
        return v

    def matrix_apply_before(self, m):
        return numpy.dot(self.rotation_matrix, m)

    def matrix_apply_inverse_before(self, m):
        return numpy.dot(self.rotation_matrix.transpose(), m)

    def matrix_apply_after(self, m):
        return numpy.dot(m, self.rotation_matrix)

    def matrix_apply_inverse_after(self, m):
        return numpy.dot(m, self.rotation_matrix.transpose())

    def apply_after(self, parent): # self -> parent AFTER self
        self.rotation_matrix[:] = parent.matrix_apply_before(self.rotation_matrix)

    def apply_inverse_after(self, parent): # self -> !parent AFTER self
        self.rotation_matrix[:] = parent.matrix_apply_inverse_before(self.rotation_matrix)

    def apply_before(self, child): # self -> self AFTER child
        self.rotation_matrix[:] = child.matrix_apply_after(self.rotation_matrix)

    def apply_inverse_before(self, child): # self -> self AFTER !child
        self.rotation_matrix[:] = child.matrix_apply_inverse_after(self.rotation_matrix)

    def compare(self, other, translation_threshold=1e-3, rotation_threshold=1e-3):
        return numpy.sum(numpy.ravel((self.rotation_matrix - other.rotation_matrix)**2)) < rotation_threshold

    def assign_shallow(self, other):
        if isinstance(other, Rotation):
            self.rotation_matrix[:] = other.rotation_matrix

    def get_rotation_properties(self):
        r = self.rotation_matrix
        # determine wether an inversion rotation has been applied
        invert = (numpy.linalg.det(r) < 0)
        factor = {True: -1, False: 1}[invert]
        # get the rotation data
        # trace(r) = 1+2*cos(angle)
        cos_angle = 0.5*(factor*numpy.trace(r) - 1)
        if cos_angle > 1: cos_angle = 1.0
        if cos_angle < -1: cos_angle = -1.0
        # the antisymmetric part of the non-diagonal vector tell us something
        # about sin(angle) and n.
        rotation_axis = 0.5*factor*numpy.array([-r[1, 2] + r[2, 1], r[0, 2] - r[2, 0], -r[0, 1] + r[1, 0]])
        sin_angle = math.sqrt(numpy.dot(rotation_axis, rotation_axis))
        # look for the best way to normalize the
        if (sin_angle == 0.0) and (cos_angle > 0):
            rotation_axis[2] = 1.0
        elif abs(sin_angle) < (1-cos_angle):
            for index in range(3):
                rotation_axis[index] = {True: -1, False: 1}[rotation_axis[index] < 0] * math.sqrt(abs((factor*r[index, index] - cos_angle) / (1 - cos_angle)))
        else:
            rotation_axis = rotation_axis / sin_angle

        # Finally calculate the rotation_angle:
        rotation_angle = math.atan2(sin_angle, cos_angle)
        return rotation_angle, rotation_axis, invert

    def set_rotation_properties(self, rotation_angle, rotation_axis, invert):
        norm = math.sqrt(numpy.dot(rotation_axis, rotation_axis))
        if norm > 0:
            x = rotation_axis[0] / norm
            y = rotation_axis[1] / norm
            z = rotation_axis[2] / norm
            c = math.cos(rotation_angle)
            s = math.sin(rotation_angle)
            self.rotation_matrix[:] = (2*invert-1) * numpy.array([
                [x*x*(1-c)+c  , x*y*(1-c)-z*s, x*z*(1-c)+y*s],
                [x*y*(1-c)+z*s, y*y*(1-c)+c  , y*z*(1-c)-x*s],
                [x*z*(1-c)-y*s, y*z*(1-c)+x*s, z*z*(1-c)+c  ]
            ])
        else:
            self.rotation_matrix[:] = numpy.identity(3) * (2*invert-1)


class Complete(Translation, Rotation):
    def __init__(self):
        self.translation_vector = numpy.zeros(3, float)
        self.rotation_matrix = numpy.identity(3, float)

    def __str__(self):
        result = "COMPLETE\n"
        for i in range(3):
            result += "[ % 10.7f \t % 10.7f \t % 10.7f ] \t % 10.7f \n" % (tuple(self.rotation_matrix[i]) + (self.translation_vector[i],))
        return result

    def clear(self):
        Translation.clear(self)
        Rotation.clear(self)

    def from_matrix(self, m):
        Rotation.from_matrix(self, m)
        Translation.from_matrix(self, m)

    def get_matrix(self):
        temp = Translation.get_matrix(self)
        temp[0:3, 0:3] = self.rotation_matrix
        return temp

    def get_inverse_matrix(self):
        invtrans = numpy.dot(-self.translation_vector, self.rotation_matrix)
        temp = Rotation.get_inverse_matrix(self)
        temp[0:3, 3] = invtrans
        return temp

    def gl_apply(self):
        glMultMatrixf(self.get_matrix().transpose())

    def gl_apply_inverse(self):
        glMultMatrixf(self.get_inverse_matrix().transpose())

    def invert(self):
        self.rotation_matrix[:] = self.rotation_matrix.transpose()
        self.translation_vector[:] = numpy.dot(self.rotation_matrix, -self.translation_vector)

    def vector_apply(self, v):
        return numpy.dot(self.rotation_matrix, v) + self.translation_vector

    def vector_apply_inverse(self, v):
        return numpy.dot(self.rotation_matrix.transpose(), v - self.translation_vector)

    def vector_apply_translation(self, v):
        return v + self.translation_vector

    def matrix_apply_before(self, m):
        return numpy.dot(self.rotation_matrix, m)

    def matrix_apply_inverse_before(self, m):
        return numpy.dot(self.rotation_matrix.transpose(), m)

    def matrix_apply_after(self, m):
        return numpy.dot(m, self.rotation_matrix)

    def matrix_apply_inverse_after(self, m):
        return numpy.dot(m, self.rotation_matrix.transpose())

    def apply_after(self, parent): # self -> parent AFTER self
        Translation.apply_after(self, parent)
        Rotation.apply_after(self, parent)

    def apply_inverse_after(self, parent): # self -> !parent AFTER self
        Translation.apply_inverse_after(self, parent)
        Rotation.apply_inverse_after(self, parent)

    def apply_before(self, child): # self -> self AFTER child
        Translation.apply_before(self, child)
        Rotation.apply_before(self, child)

    def apply_inverse_before(self, child): # self -> self AFTER !child
        Translation.apply_inverse_before(self, child)
        Rotation.apply_inverse_before(self, child)

    def compare(self, other, translation_threshold=1e-3, rotation_threshold=1e-3):
        return (
            numpy.sum((self.translation_vector - other.translation_vector)**2) < translation_threshold and
            numpy.sum(numpy.ravel((self.rotation_matrix - other.rotation_matrix)**2)) < rotation_threshold
        )

    def assign_shallow(self, other):
        Translation.assign_shallow(self, other)
        Rotation.assign_shallow(self, other)
