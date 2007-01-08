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
from zeobuilder.undefined import Undefined

from molmod.transformations import Rotation, Translation, Complete
from molmod.units import angstrom

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import numpy

import math


__all__ = ["Scene"]


glutInit([])


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
            DialogFieldInfo("Default Viewer", (1, 1), fields.faulty.MeasureEntry(
                measure="Angle",
                label_text="Eye opening angle",
                attribute_name="opening_angle",
                low=0.0,
                low_inclusive=True,
                high=0.5*math.pi,
                high_inclusive=False,
                show_popup=False,
            )),
        )
        config.register_setting(
            "window_size",
            5*angstrom,
            DialogFieldInfo("Default Viewer", (1, 2), fields.faulty.Length(
                label_text="Window size",
                attribute_name="window_size",
                low=0.0,
                low_inclusive=False,
            )),
        )
        config.register_setting(
            "window_depth",
            200.0*angstrom,
            DialogFieldInfo("Default Viewer", (1, 3), fields.faulty.Length(
                label_text="Window depth",
                attribute_name="window_depth",
                low=0.0,
                low_inclusive=False,
            )),
        )

        config.register_setting(
            "background_color",
            numpy.array([1, 1, 1, 0], float),
            None,
        )
        config.register_setting(
            "fog_color",
            numpy.array([0, 0, 0, 0], float),
            None,
        )
        config.register_setting(
            "fog_depth",
            10.0*angstrom,
            None,
        )

        self.reset_view()
        self.gl_names = {}
        self.revalidations = []
        self.clip_planes = {}

    def initialize(self): # gl_context sensitive method
        glMaterial(GL_FRONT, GL_SPECULAR, [0.9, 0.9, 0.9, 1.0])
        glMaterial(GL_FRONT, GL_SHININESS, 70.0)
        glLight(GL_LIGHT0, GL_SPECULAR, [0.7, 0.7, 0.7, 1.0])
        glLight(GL_LIGHT0, GL_AMBIENT, [0.1, 0.1, 0.1, 1.0])
        glLight(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 3.0, 0.0])
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)

        # Some default gl settings
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)

        self.initialize_interactive_tool()
        self.initialize_rotation_center()
        self.apply_renderer_settings()

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
        # change the modelview to reduced coordinates
        viewport = glGetIntegerv(GL_VIEWPORT)
        width = viewport[2] - viewport[0]
        height = viewport[3] - viewport[1]
        if width > height:
            w = float(width) / float(height)
            h = 1.0
        else:
            w = 1.0
            h = float(height) / float(width)
        glScalef(2/w, 2/h, 1.0)
        #glTranslatef(-0.5*w, -0.5*h, 0.0)
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

    def apply_renderer_settings(self): # gl_context sensitive method
        configuration = context.application.configuration
        glClearColor(*configuration.background_color)
        glFogfv(GL_FOG_COLOR, configuration.fog_color)
        if isinstance(configuration.fog_depth, Undefined):
            glDisable(GL_FOG)
        else:
            glEnable(GL_FOG)
            glFogfv(GL_FOG_MODE, GL_LINEAR)
            glFogfv(GL_FOG_START, self.znear + self.window_depth - configuration.fog_depth)
            glFogfv(GL_FOG_END, self.znear + self.window_depth)

    def add_revalidation(self, revalidation):
        self.revalidations.append(revalidation)

    def set_window_size(self, window_size):
        self.window_size = window_size
        self.update_znear()
        self.apply_renderer_settings()

    def update_znear(self):
        if self.opening_angle > 0.0:
            self.znear = 0.5*self.window_size/math.tan(0.5*self.opening_angle)
        else:
            self.znear = 0.0

    def draw(self, selection_box=None): # gl_context sensitive method
        # This function is called when the color and depth buffers have to be
        # refreshed, or when the user points to an object and you want to
        # identify it.
        viewport = glGetIntegerv(GL_VIEWPORT)
        width = viewport[2]
        height = viewport[3]
        universe = context.application.model.universe

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
        znear = self.znear
        zfar = znear + self.window_depth
        if width > height:
            w = 0.5*float(width) / float(height)
            h = 0.5
        else:
            w = 0.5
            h = 0.5*float(height) / float(width)
        if self.opening_angle > 0.0:
            glFrustum(-w*self.window_size, w*self.window_size, -h*self.window_size, h*self.window_size, znear, zfar)
        else:
            glOrtho(-w*self.window_size, w*self.window_size, -h*self.window_size, h*self.window_size, znear, zfar)
        if selection_box is None:
            self.projection_matrix = numpy.transpose(numpy.array(glGetFloatv(GL_PROJECTION_MATRIX), float))

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # Move to viewer position (reverse)
        self.viewer.gl_apply_inverse()
        glTranslatef(0.0, 0.0, -znear)
        # Draw the rotation center, only when realy drawing objects:
        if selection_box is None:
            glMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
            glShadeModel(GL_SMOOTH)
            glCallList(self.rotation_center_list)
        # Now rotate to the model frame and move back to the model center (reverse)
        self.rotation.gl_apply_inverse()
        # Then bring the rotation center at the right place (reverse)
        self.rotation_center.gl_apply_inverse()
        if universe is not None:
            universe.model_center.gl_apply_inverse()

        if selection_box is None:
            self.modelview_matrix = numpy.transpose(numpy.array(glGetFloatv(GL_MODELVIEW_MATRIX), float))

        # define the clipping planes:
        for GL_CLIP_PLANEi, coefficients in self.clip_planes.iteritems():
            glEnable(GL_CLIP_PLANEi)
            temp = coefficients.copy()
            glClipPlane(GL_CLIP_PLANEi, coefficients)

        if universe is not None:
            if selection_box is None: # When just picking objects, don't change the call lists, not needed.
                self.revalidations.reverse()
                for revalidation in self.revalidations:
                    revalidation()
                self.revalidations = []
            universe.call_list()

        for GL_CLIP_PLANEi in self.clip_planes:
            glDisable(GL_CLIP_PLANEi)

        if selection_box is not None:
            # now let the caller analyze the hits by returning the selection
            # buffer. Note: The selection buffer can be used as an iterator
            # over 3-tupples (near, far, names) where names is tuple that
            # contains the gl_names associated with the encountered vertices.
            return glRenderMode(GL_RENDER)
        else:
            # draw the interactive tool (e.g. selection rectangle):
            glCallList(self.tool_list)

    def reset_view(self):
        config = context.application.configuration
        self.rotation_center = Translation()
        self.rotation = Rotation()
        self.viewer = Translation()
        self.viewer.t[2] = config.viewer_distance
        self.opening_angle = config.opening_angle
        self.window_size = config.window_size
        self.window_depth = config.window_depth
        self.update_znear()
        self.apply_renderer_settings()

    def yield_hits(self, selection_box): # gl_context sensitive method
        for selection in self.draw(selection_box):
            yield self.gl_names.get(selection[2][-1])

    def get_nearest(self, x, y): # gl_context sensitive method
        nearest = None
        for selection in self.draw((x, y, x, y)):
            if nearest is None:
                nearest = selection
            elif selection[0] < nearest[0]:
                nearest = selection
        if nearest is None:
            return None
        else:
            return self.gl_names.get(nearest[2][-1])

    def compile_tool_rectangle(self, left, top, right, bottom): # gl_context sensitive method
        glNewList(self.tool_draw_list, GL_COMPILE)
        glColor(1, 1, 1)
        glLineWidth(1)
        glBegin(GL_LINE_LOOP)
        glVertex3f(left,  top,    0.0)
        glVertex3f(left,  bottom, 0.0)
        glVertex3f(right, bottom, 0.0)
        glVertex3f(right, top,    0.0)
        glEnd()
        glEndList()

    def compile_tool_line(self, x1, y1, x2, y2):
        glNewList(self.tool_draw_list, GL_COMPILE)
        glColor(1, 1, 1)
        glLineWidth(1)
        glBegin(GL_LINES)
        glVertex3f(x1, y1, 0.0)
        glVertex3f(x2, y2, 0.0)
        glEnd()
        glEndList()

    def compile_tool_custom(self, draw_function):
        glNewList(self.tool_draw_list, GL_COMPILE)
        draw_function()
        glEndList()

    def get_camera_properties(self):
        #ALL THIS STUFF IS IN MODEL COORDINATES!!!
        viewport = glGetIntegerv(GL_VIEWPORT)
        width = viewport[2]
        height = viewport[3]
        if width > height:
            w = float(width) / float(height)
            h = 1.0
        else:
            w = 1.0
            h = float(height) / float(width)
        viewing_direction = -self.modelview_matrix[2,:3]
        distance_eye_viewer =  self.znear
        eye_position = numpy.dot(
            self.modelview_matrix[:3,:3].transpose(),
            -self.modelview_matrix[:3,3]
        )
        viewer_position = numpy.dot(
            self.modelview_matrix[:3,:3].transpose(),
            -self.modelview_matrix[:3,3] - numpy.array([0.0, 0.0, distance_eye_viewer])
        )
        top_left = numpy.dot(
            self.modelview_matrix[:3,:3].transpose(),
            -self.modelview_matrix[:3,3] - numpy.array([0.5*w*self.window_size, -0.5*h*self.window_size, distance_eye_viewer])
        )
        left_to_right = numpy.dot(
            self.modelview_matrix[:3,:3].transpose(),
            numpy.array([w*self.window_size, 0.0, 0.0])
        )
        top_to_bottom = numpy.dot(
            self.modelview_matrix[:3,:3].transpose(),
            numpy.array([0.0, -h*self.window_size, 0.0])
        )
        #print
        #print "viewing_direction  ", viewing_direction
        #print "distance_eye_viewer", distance_eye_viewer
        #print "eye_position       ", eye_position
        #print "viewer_position    ", viewer_position
        #print "top_left           ", top_left
        #print "left_to_right      ", left_to_right
        #print "top_to_bottom      ", top_to_bottom
        #print
        return viewing_direction, distance_eye_viewer, eye_position, viewer_position, top_left, left_to_right, top_to_bottom
