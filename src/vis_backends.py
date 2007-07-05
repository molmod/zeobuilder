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


from OpenGL.GLU import *
from OpenGL.GL import *


__all__ = ["VisBackend", "VisBackendOpenGL"]


class VisBackend(object):
    def __init__(self):
        self.names = {}

    #
    # List related functuions
    #

    def _gen_list(self):
        raise NotImplementedError

    def _del_list(self, l):
        raise NotImplementedError

    def create_list(self, owner=None):
        l = self._gen_list()
        if owner is not None:
            self.names[l] = owner
        return l

    def delete_list(self, l):
        self._del_list(l)
        if l in self.names:
            del self.names[l]

    def begin_list(self, l):
        raise NotImplementedError

    def end_list(self, l):
        raise NotImplementedError

    def call_list(self, l):
        raise NotImplementedError

    #
    # Names
    #

    def push_name(self, name):
        raise NotImplementedError

    def pop_name(self):
        raise NotImplementedError

    #
    # Transform functions
    #

    def push_matrix(self):
        raise NotImplementedError

    def translate(self, x, y, z):
        raise NotImplementedError

    def rotate(self, angle, x, y, z):
        raise NotImplementedError

    def transform(self, transformation):
        raise NotImplementedError

    def pop_matrix(self):
        raise NotImplementedError

    #
    # Layout related functions
    #

    def set_color(self, color):
        raise NotImplementedError

    def set_bright(self, bright):
        raise NotImplementedError

    def set_specular(self, specular):
        raise NotImplementedError

    def set_line_width(self, width):
        raise NotImplementedError

    #
    # Draw functions
    #

    def draw_line(self, points):
        raise NotImplementedError

    def draw_quads(self, coordinates):
        raise NotImplementedError

    def draw_quad_strip(self, coordinates, normals):
        raise NotImplementedError

    def draw_sphere(self, radius, quality):
        raise NotImplementedError

    def draw_cylinder(self, start, length, radius, quality):
        raise NotImplementedError

    def draw_cone(self, start, length, radius1, radius2, quality):
        raise NotImplementedError

    def draw_disk(self, radius, quality):
        raise NotImplementedError

    def set_quadric_outside(self):
        raise NotImplementedError

    def set_quadric_inside(self):
        raise NotImplementedError


class VisBackendOpenGL(VisBackend):
    def __init__(self):
        VisBackend.__init__(self)
        self.quadric = gluNewQuadric()
        gluQuadricNormals(self.quadric, GLU_SMOOTH)
        #self.name_counter = 0
        #self.matrix_counter = 0

    #
    # List related functuions
    #

    def _gen_list(self):
        return glGenLists(1)

    def _del_list(self, l):
        glDeleteLists(l, 1)

    def begin_list(self, l):
        glNewList(l, GL_COMPILE)

    def end_list(self):
        glEndList()

    def call_list(self, l):
        glCallList(l)

    #
    # Names
    #

    def push_name(self, name):
        glPushName(name)
        #self.name_counter += 1
        #print "NAME UP  ", self.name_counter

    def pop_name(self):
        glPopName
        #self.name_counter -= 1
        #print "NAME DOWN", self.name_counter
        #assert self.name_counter >= 0

    #
    # Transform functions
    #

    def push_matrix(self):
        glPushMatrix()
        #self.matrix_counter += 1
        #print "MATRIX UP  ", self.matrix_counter

    def translate(self, x, y, z):
        glTranslate(x, y, z)

    def rotate(self, angle, x, y, z):
        glRotate(angle, x, y, z)

    def transform(self, transformation):
        transformation.gl_apply()

    def pop_matrix(self):
        glPopMatrix()
        #self.matrix_counter -= 1
        #print "MATRIX DOWN", self.matrix_counter
        #assert self.matrix_counter >= 0


    #
    # Layout related functions
    #

    def set_color(self, r, g, b, a=1.0):
        glMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [r, g, b, a])

    def set_bright(self, bright):
        if bright:
            glMaterial(GL_FRONT, GL_SHININESS, 0.0)
        else:
            glMaterial(GL_FRONT, GL_SHININESS, 70.0)

    def set_specular(self, specular):
        if specular:
            glMaterial(GL_FRONT, GL_SPECULAR, [0.7, 0.7, 0.7, 1.0])
        else:
            glMaterial(GL_FRONT, GL_SPECULAR, [0.0, 0.0, 0.0, 0.0])

    def set_line_width(self, width):
        glLineWidth(width)

    #
    # Draw functions
    #

    def draw_line(self, *points):
        glBegin(GL_LINES)
        for point in points:
            glVertex(point)
        glEnd()

    def draw_quads(self, coordinates, normals):
        glBegin(GL_QUADS)
        for quadc, normal in zip(coordinates, normals):
            glNormal3f(normal)
            for c in quadc:
                glVertex(c)
        glEnd()

    def draw_quad_strip(self, coordinates, normals):
        glBegin(GL_QUAD_STRIP)
        for coordinate, normal in zip(coordinates, normals):
            glNormal(normal)
            glVertex(coordinate)
        glEnd()

    def draw_sphere(self, radius, quality):
        gluSphere(self.quadric, radius, quality, quality/2)

    def draw_cylinder(self, radius, length, quality):
        gluCylinder(self.quadric, radius, radius, length, quality, 1)

    def draw_cone(self, radius1, radius2, length, quality):
        gluCylinder(self.quadric, radius1, radius2, length, quality, 1)

    def draw_disk(self, radius, quality):
        gluDisk(self.quadric, 0, radius, quality, 1)

    def set_quadric_outside(self):
        gluQuadricOrientation(self.quadric, GLU_OUTSIDE)

    def set_quadric_inside(self):
        gluQuadricOrientation(self.quadric, GLU_INSIDE)


