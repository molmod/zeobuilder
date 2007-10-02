# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 Toon Verstraelen <Toon.Verstraelen@UGent.be>
#
# This file is part of Zeobuilder.
#
# Zeobuilder is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
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


from tools import Tool

from zeobuilder import context

from OpenGL.GLUT import glutInit
from OpenGL.GLU import *
from OpenGL.GL import *
import numpy

__all__ = ["VisBackend", "VisBackendOpenGL"]


class VisBackend(object):
    def initialize_draw(self):
        context.application.scene.initialize_draw()

    def draw(self):
        raise NotImplementedError

    #
    # List related functuions
    #

    def create_list(self, owner=None):
        raise NotImplementedError

    def delete_list(self, l):
        raise NotImplementedError

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

    def draw_polygon(self, *data):
        raise NotImplementedError

    def draw_quads(self, *data):
        raise NotImplementedError

    def draw_quad_strip(self, *data):
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

    #
    # Clip functions
    #

    def set_clip_plane(self, index, coefficients):
        raise NotImplementedError

    def unset_clip_plane(self, index):
        raise NotImplementedError

    #
    # Fog and background functions
    #

    def unset_fog(self):
        raise NotImplementedError

    def set_fog(self, color, start, end):
        raise NotImplementedError

    def set_background_color(self, color):
        raise NotImplementedError


glutInit([]) # FIXME, due to unittests


class VisBackendOpenGL(VisBackend):
    select_buffer_size = 4096

    def __init__(self, scene, camera):
        VisBackend.__init__(self, scene, camera)
        VisBackend.__init__(self)
        self.quadric = gluNewQuadric()
        gluQuadricNormals(self.quadric, GLU_SMOOTH)
        #self.name_counter = 0
        #self.matrix_counter = 0
        self.names = {}
        self.clip_constants = [GL_CLIP_PLANE0, GL_CLIP_PLANE1, GL_CLIP_PLANE2, GL_CLIP_PLANE3, GL_CLIP_PLANE4, GL_CLIP_PLANE5]
        self.tool = Tool()

    #
    # Generic stuff
    #

    def initialize_draw(self):
        self.set_specular(True)
        self.set_bright(False)
        glLight(GL_LIGHT0, GL_SPECULAR, [0.7, 0.7, 0.7, 1.0])
        glLight(GL_LIGHT0, GL_AMBIENT, [0.1, 0.1, 0.1, 1.0])
        glLight(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 3.0, 0.0])
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glCullFace(GL_BACK)
        VisBackend.initialize_draw(self)
        self.tool.initialize_gl()

    def draw(self, width, height, selection_box=None):
        scene = context.application.scene
        camera = context.application.camera

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        if selection_box is not None:
            # set up a select buffer
            glSelectBuffer(self.select_buffer_size)
            glRenderMode(GL_SELECT)
            glInitNames()

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # Apply the pick matrix if selecting
        if selection_box is not None:
            gluPickMatrix(0.5 * (selection_box[0] + selection_box[2]),
                          height - 0.5 * (selection_box[1] + selection_box[3]),
                          selection_box[2] - selection_box[0] + 1,
                          selection_box[3] - selection_box[1] + 1,
                          (0, 0, width, height))

        # Apply the frustum matrix
        znear = camera.znear
        zfar = camera.znear + camera.window_depth
        if width > height:
            w = 0.5*float(width) / float(height)
            h = 0.5
        else:
            w = 0.5
            h = 0.5*float(height) / float(width)
        if znear > 0.0:
            glFrustum(-w*camera.window_size, w*camera.window_size, -h*camera.window_size, h*camera.window_size, znear, zfar)
        else:
            glOrtho(-w*camera.window_size, w*camera.window_size, -h*camera.window_size, h*camera.window_size, znear, zfar)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # Move to eye position (reverse)
        camera.eye.gl_apply_inverse()
        glTranslatef(0.0, 0.0, -znear)
        # Draw the rotation center, only when realy drawing objects:
        if selection_box is None:
            glMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
            glShadeModel(GL_SMOOTH)
            self.call_list(scene.rotation_center_list)
        # Now rotate to the model frame and move back to the model center (reverse)
        camera.rotation.gl_apply_inverse()
        # Then bring the rotation center at the right place (reverse)
        camera.rotation_center.gl_apply_inverse()
        scene.model_center.gl_apply_inverse()

        scene.draw()

        if selection_box is not None:
            # now let the caller analyze the hits by returning the selection
            # buffer. Note: The selection buffer can be used as an iterator
            # over 3-tupples (near, far, names) where names is tuple that
            # contains the gl_names associated with the encountered vertices.
            return glRenderMode(GL_RENDER)
        else:
            # draw the interactive tool (e.g. selection rectangle):
            glCallList(self.tool.total_list)

    #
    # List related functuions
    #

    def create_list(self, owner=None):
        l = glGenLists(1)
        if owner is not None:
            self.names[l] = owner
        return l

    def delete_list(self, l):
        glDeleteLists(l, 1)
        if l in self.names:
            del self.names[l]

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
        glPopName()
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

    def draw_polygon(self, *data):
        glBegin(GL_POLYGON)
        for normal, vectors in data:
            glNormal3fv(normal)
            for vector in vectors:
                glVertex(vector)
        glEnd()

    def draw_quads(self, *data):
        glBegin(GL_QUADS)
        for normal, vectors in data:
            glNormal3fv(normal)
            for vector in vectors:
                glVertex(vector)
        glEnd()

    def draw_quad_strip(self, *data):
        glBegin(GL_QUAD_STRIP)
        for normal, vectors in data:
            glNormal3fv(normal)
            for vector in vectors:
                glVertex(vector)
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

    #
    # Clip functions
    #

    def set_clip_plane(self, index, coefficients):
        glEnable(self.clip_constants[index])
        glClipPlane(self.clip_constants[index], coefficients)

    def unset_clip_plane(self, index):
        glDisable(self.clip_constants[index])

    #
    # Fog and background functions
    #

    def unset_fog(self):
        glDisable(GL_FOG)

    def set_fog(self, color, start, end):
        glFogfv(GL_FOG_COLOR, color)
        glEnable(GL_FOG)
        glFogfv(GL_FOG_MODE, GL_LINEAR)
        glFogfv(GL_FOG_START, start)
        glFogfv(GL_FOG_END, end)

    def set_background_color(self, color):
        glClearColor(*color)

