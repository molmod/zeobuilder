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
# ----------
# The scene class executes the necessary gl Commands: mouse response, letting
# the geometric objects do their stuff, define light and material, ... This glScene
# can be passed to a glArea object so this can be used for visualising all the
# geometric objects.


from zeobuilder import context
from zeobuilder.transformations import Rotation, Translation, Complete
from molmod.units import angstrom

from OpenGL.GLU import *
from OpenGL.GL import *
import numpy

import math


__all__ = ["Scene"]


class Scene(object):
    select_buffer_size = 4096

    def __init__(self):
        self.quadric = gluNewQuadric()
        gluQuadricNormals(self.quadric, GLU_SMOOTH)

        # register configuration settings: default viewer
        from zeobuilder.gui import fields
        from zeobuilder.gui.fields_dialogs import DialogFieldInfo
        config = context.application.configuration
        config.register_setting(
            "viewer_distance",
            100.0*angstrom,
            DialogFieldInfo("Default Viewer", (1, 0), fields.faulty.Length(
                label_text="Distance from origin",
                attribute_name="viewer_distance",
                low=0.0,
                low_inclusive=True,
            )),
        )
        config.register_setting(
            "opening_angle",
            0.0,
            DialogFieldInfo("Default Viewer", (1, 1), fields.faulty.Float(
                label_text="Eye opening angle",
                attribute_name="opening_angle",
                low=0.0,
                low_inclusive=True,
                high=90.0,
                high_inclusive=False,
                show_popup=False,
            )),
        )
        config.register_setting(
            "window_size",
            5*angstrom,
            DialogFieldInfo("Default Viewer", (1, 1), fields.faulty.Length(
                label_text="Window size",
                attribute_name="window_size",
                low=0.0,
                low_inclusive=False,
            )),
        )
        config.register_setting(
            "window_depth",
            200.0*angstrom,
            DialogFieldInfo("Default Viewer", (1, 1), fields.faulty.Length(
                label_text="Window depth",
                attribute_name="window_depth",
                low=0.0,
                low_inclusive=False,
            )),
        )

        self.reset_view()
        self.gl_names = {}
        self.revalidations = []
        self.clip_planes = {}

    def initialize(self): # gl_context sensitive method
        # And then there was light (and material)!
        glLightModelf(GL_LIGHT_MODEL_TWO_SIDE, 1)
        glMaterial(GL_FRONT, GL_SPECULAR, [0.7, 0.7, 0.7, 1.0])
        glMaterial(GL_FRONT, GL_SHININESS, 70.0)
        #glMaterial(GL_BACK, GL_SPECULAR, [0.7, 0.7, 0.7, 1.0])
        #glMaterial(GL_BACK, GL_SHININESS, 70.0)
        glLight(GL_LIGHT0, GL_SPECULAR, [0.7, 0.7, 0.7, 1.0])
        glLight(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 3.0, 0.0])
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)
        glEnable(GL_CULL_FACE)

        # Some default gl settings
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        #glEnable(GL_LINE_STIPPLE)

        self.initialize_interactive_tool()
        self.initialize_rotation_center()

    def initialize_interactive_tool(self): # gl_context sensitive method
        self.tool_draw_list = glGenLists(1)
        self.clear_tool_draw_list()

        self.tool_list = glGenLists(1)
        self.compile_tool_list()

    def compile_tool_list(self): # gl_context sensitive method
        glNewList(self.tool_list, GL_COMPILE)
        # reset a few things
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # change the modelview to screen coordinates
        viewport = glGetIntegerv(GL_VIEWPORT)
        w = viewport[2] - viewport[0]
        h = viewport[3] - viewport[1]
        glScalef(2.0 / w, -2.0 / h, 1.0);
        glTranslatef(-w / 2.0, -h / 2.0, 0.0);
        glLineWidth(1)
        #glLineStipple(1, -21846)
        glCallList(self.tool_draw_list)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEndList()

    def clear_tool_draw_list(self): # gl_context sensitive method
        glNewList(self.tool_draw_list, GL_COMPILE)
        glEndList()

    def initialize_rotation_center(self): # gl_context sensitive method
        self.rotation_center_list = glGenLists(1)
        glNewList(self.rotation_center_list, GL_COMPILE)
        small = 0.1
        big = 0.3
        glBegin(GL_POLYGON)
        glNormal3f(1.0, 0.0, 0.0)
        glVertex3f(small, 0.0, 0.0)
        glVertex3f(big, big, 0.0)
        glVertex3f(0.0, small, 0.0)
        glVertex3f(-big, big, 0.0)
        glVertex3f(-small, 0.0, 0.0)
        glVertex3f(-big, -big, 0.0)
        glVertex3f(0.0, -small, 0.0)
        glVertex3f(big, -big, 0.0)
        glEnd()
        glEndList()

    def add_revalidation(self, revalidation):
        self.revalidations.append(revalidation)

    def znear(self):
        if self.opening_angle > 0.0:
            return 0.5*self.window_size/math.tan(0.5*self.opening_angle*math.pi/180)
        else:
            return 0.0

    def draw(self, selection_box=None): # gl_context sensitive method
        # This function is called when the color and depth buffers have to be refilled,
        # or when the user points to an object and you want to identify it.
        viewport = glGetIntegerv(GL_VIEWPORT)
        width = viewport[2]
        height = viewport[3]

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
                          viewport)

        # Apply the frustum matrix
        znear = self.znear()
        zfar = znear + self.window_depth
        if self.opening_angle > 0.0:
            if width > height:
                w = float(width) / float(height)
                glFrustum(-w*self.window_size, w*self.window_size, -self.window_size, self.window_size, znear, zfar)
            else:
                h = float(height) / float(width)
                glFrustum(-self.window_size, self.window_size, -h*self.window_size, h*self.window_size, znear, zfar)
        else:
            if width > height:
                w = float(width) / float(height)
                glOrtho(-w*self.window_size, w*self.window_size, -self.window_size, self.window_size, znear, zfar)
            else:
                h = float(height) / float(width)
                glOrtho(-self.window_size, self.window_size, -h*self.window_size, h*self.window_size, znear, zfar)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # Move to viewer position (reverse)
        self.viewer.gl_apply()
        glTranslatef(0.0, 0.0, -znear)
        # Draw the rotation center, only when realy drawing objects:
        if selection_box is None:
            glMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
            glShadeModel(GL_SMOOTH)
            glCallList(self.rotation_center_list)
        # Then bring the rotation center at the right place
        # Now rotate to the model frame and move back to the model center
        self.rotation.gl_apply_inverse()
        # Move to rotation center (reverse)
        #glTranslatef(-self.center[0], -self.center[1], -self.center[2])
        self.center.gl_apply_inverse()
        #print self.transformation

        # define the clipping planes:
        for GL_CLIP_PLANEi, coefficients in self.clip_planes.iteritems():
            temp = coefficients.copy()
            glClipPlane(GL_CLIP_PLANEi, coefficients)

        if context.application.model.universe is not None:
            if selection_box is None: # When just picking objects, don't change the call lists, not needed.
                self.revalidations.reverse()
                for revalidation in self.revalidations:
                    revalidation()
                self.revalidations = []
            context.application.model.universe.call_list()

        if selection_box is not None:
            # now let the caller analyze the hits.
            temp = glRenderMode(GL_RENDER)
            if temp is None:
                return []
            else:
                return list(temp)
        else:
            # draw the selection rectangle (if visible):
            glCallList(self.tool_list)

    def reset_view(self):
        config = context.application.configuration
        self.center = Translation()
        self.rotation = Rotation()
        self.viewer = Translation()
        self.viewer.translation_vector[2] = -config.viewer_distance
        self.opening_angle = config.opening_angle
        self.window_size = config.window_size
        self.window_depth = config.window_depth

    def get_parent_model_view(self, gl_object):
        # determine the model view
        model_view = Complete()
        model_view.apply_before(self.viewer)
        model_view.apply_inverse_before(self.rotation)
        model_view.apply_inverse_before(self.center)
        if gl_object is not None:
            model_view.apply_before(gl_object.get_absolute_parentframe())
        return model_view

    def compile_tool_rectangle(self, left, top, right, bottom): # gl_context sensitive method
        glNewList(self.tool_draw_list, GL_COMPILE)
        glBegin(GL_LINE_LOOP)
        glVertex3f(left,  top,    0.0)
        glVertex3f(left,  bottom, 0.0)
        glVertex3f(right, bottom, 0.0)
        glVertex3f(right, top,    0.0)
        glEnd()
        glEndList()

    def compile_tool_chain(self, points): # gl_context sensitive method
        glNewList(self.tool_draw_list, GL_COMPILE)
        glBegin(GL_LINE_LOOP)
        for point in points:
            glVertex3f(point[0], point[1], 0.0)
        glEnd()
        glEndList()
