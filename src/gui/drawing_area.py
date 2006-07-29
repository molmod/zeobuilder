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

import scene

from zeobuilder.nodes.glmixin import GLTransformationMixin
from zeobuilder.transformations import Complete

import gtk.gtkgl, gtk.gdkgl, numpy
from OpenGL.GL import *

__all__ = ["DrawingArea"]


class DrawingArea(gtk.gtkgl.DrawingArea):
    def __init__(self):
        self.scene = scene.Scene()

        gl_config = gtk.gdkgl.Config(mode=(gtk.gdkgl.MODE_RGB | gtk.gdkgl.MODE_DEPTH | gtk.gdkgl.MODE_DOUBLE))
        gtk.gtkgl.DrawingArea.__init__(self, gl_config)
        self.connect("realize", self.on_realize)
        self.connect("configure_event", self.on_configure_event)
        self.connect("expose_event", self.on_expose_event)

        self.set_flags(gtk.CAN_FOCUS)
        self.set_size_request(300, 300)

    def on_realize(self, widget):
        if not self.get_gl_drawable().gl_begin(self.get_gl_context()): return
        self.scene.initialize()
        self.get_gl_drawable().gl_end()

    def on_configure_event(self, widget, event):
        if not self.get_gl_drawable().gl_begin(self.get_gl_context()): return
        glViewport(0, 0, event.width, event.height)
        self.scene.revalidations.append(self.scene.compile_tool_list)
        self.get_gl_drawable().gl_end()

    def on_expose_event(self, widget, event):
        if not self.get_gl_drawable().gl_begin(self.get_gl_context()): return
        self.scene.draw()
        if self.get_gl_drawable().is_double_buffered():
            self.get_gl_drawable().swap_buffers()
        else:
            glFlush()
        self.get_gl_drawable().gl_end()

    def position_of_vector(self, vector):
        temp = numpy.ones(4, float)
        temp[0:len(vector)] = vector
        temp = numpy.dot(self.scene.projection_matrix, temp)
        temp = temp[0:2]/temp[3] # from homogeneous to Cartesian coordinates
        temp = numpy.array([
            int(0.5*(1+temp[0])*self.allocation.width),
            int(0.5*(1-temp[1])*self.allocation.height)
        ])
        return temp

    def vector_of_object(self, gl_object):
        frame = gl_object.get_absolute_frame()
        tmp = numpy.ones(4, float)
        tmp[:3] = frame.translation_vector
        tmp = numpy.dot(self.scene.modelview_matrix, tmp)
        return tmp[:3]/tmp[3]

    def depth_of_object(self, gl_object):
        return -self.vector_of_object(gl_object)[-1]

    def position_of_object(self, gl_object):
        frame = gl_object.get_absolute_frame()
        tmp = numpy.ones(4, float)
        tmp[:3] = frame.translation_vector
        return self.position_of_vector(numpy.dot(self.scene.modelview_matrix, tmp))

    def user_to_parent(self, gl_object):
        if hasattr(gl_object, "parent") and \
           isinstance(gl_object.parent, GLTransformationMixin):
            parent_matrix = gl_object.parent.get_absolute_frame().rotation_matrix
        else:
            parent_matrix = numpy.identity(3, float)
        return numpy.dot(self.scene.modelview_matrix[0:3,0:3], parent_matrix).transpose()

    def depth_to_scale(self, depth):
        """ transforms a depth into a scale au/pixel"""
        if self.scene.opening_angle > 0.0:
            return 2/float(self.allocation.width)/self.scene.projection_matrix[0, 0]*depth
        else:
            return 2/float(self.allocation.width)/self.scene.projection_matrix[0, 0]

    def yield_hits(self, selection_box):
        if not self.get_gl_drawable().gl_begin(self.get_gl_context()): return
        for hit in self.scene.yield_hits(selection_box):
            yield hit
        self.get_gl_drawable().gl_end()

    def get_nearest(self, x, y):
        if not self.get_gl_drawable().gl_begin(self.get_gl_context()): return
        hit = self.scene.get_nearest(x, y)
        self.get_gl_drawable().gl_end()
        return hit

    def tool_clear(self):
        if not self.get_gl_drawable().gl_begin(self.get_gl_context()): return
        self.scene.clear_tool_draw_list()
        self.queue_draw()
        self.get_gl_drawable().gl_end()

    def to_reduced(self, x, y):
        w = self.allocation.width
        h = self.allocation.height
        if w < h:
            return (x - 0.5*w)/w, -(y - 0.5*h)/w
        else:
            return (x - 0.5*w)/h, -(y - 0.5*h)/h

    def tool_rectangle(self, left, top, right, bottom):
        if not self.get_gl_drawable().gl_begin(self.get_gl_context()): return
        self.scene.compile_tool_rectangle(left, top, right, bottom)
        self.queue_draw()
        self.get_gl_drawable().gl_end()

    def tool_chain(self, points):
        if not self.get_gl_drawable().gl_begin(self.get_gl_context()): return
        self.scene.compile_tool_chain(points)
        self.queue_draw()
        self.get_gl_drawable().gl_end()

    def tool_custom(self, compile_function):
        if not self.get_gl_drawable().gl_begin(self.get_gl_context()): return
        compile_function(self.scene.tool_draw_list)
        self.queue_draw()
        self.get_gl_drawable().gl_end()
