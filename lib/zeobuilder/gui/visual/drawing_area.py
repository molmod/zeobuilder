# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 - 2009 Toon Verstraelen <Toon.Verstraelen@UGent.be>, Center
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


from zeobuilder import context
from zeobuilder.actions.composed import UserError

import gtk.gtkgl, gtk.gdkgl, numpy
from OpenGL.GL import *



__all__ = ["DrawingArea"]


class DrawingArea(gtk.gtkgl.DrawingArea):
    def __init__(self):
        gl_config = gtk.gdkgl.Config(mode=(gtk.gdkgl.MODE_RGB | gtk.gdkgl.MODE_DEPTH | gtk.gdkgl.MODE_DOUBLE))
        gtk.gtkgl.DrawingArea.__init__(self, gl_config)
        self.connect("realize", self.on_realize)
        self.connect("configure_event", self.on_configure_event)
        self.connect("expose_event", self.on_expose_event)

        self.set_flags(gtk.CAN_FOCUS)
        self.set_size_request(300, 300)

    def on_realize(self, widget):
        if not self.get_gl_drawable().gl_begin(self.get_gl_context()): return
        vb = context.application.vis_backend
        vb.initialize_draw()
        self.get_gl_drawable().gl_end()

    def on_configure_event(self, widget, event):
        if not self.get_gl_drawable().gl_begin(self.get_gl_context()): return
        glViewport(0, 0, event.width, event.height)
        vb = context.application.vis_backend
        vb.tool.compile_total_list()
        self.get_gl_drawable().gl_end()

    def on_expose_event(self, widget, event):
        if not self.get_gl_drawable().gl_begin(self.get_gl_context()): return
        vb = context.application.vis_backend
        vb.draw(self.allocation.width, self.allocation.height)
        if self.get_gl_drawable().is_double_buffered():
            self.get_gl_drawable().swap_buffers()
        else:
            glFlush()
        self.get_gl_drawable().gl_end()

    def yield_hits(self, selection_box):
        if not self.get_gl_drawable().gl_begin(self.get_gl_context()): return
        vb = context.application.vis_backend
        try:
            for selection in vb.draw(self.allocation.width, self.allocation.height, selection_box):
                yield vb.names.get(selection[2][-1])
        except GLerror, e:
            self.get_gl_drawable().gl_end()
            if e.errno[0] == 1283:
                raise UserError("Too many objects in selection. Increase selection buffer size.")
            else:
                raise
        self.get_gl_drawable().gl_end()

    def get_nearest(self, x, y):
        if not self.get_gl_drawable().gl_begin(self.get_gl_context()): return
        vb = context.application.vis_backend
        nearest = None
        for selection in vb.draw(self.allocation.width, self.allocation.height, (x, y, x, y)):
            if nearest is None:
                nearest = selection
            elif selection[0] < nearest[0]:
                nearest = selection
        self.get_gl_drawable().gl_end()
        if nearest is None:
            return None
        else:
            return vb.names.get(nearest[2][-1])

    def screen_to_camera(self, p, translate=True):
        w = self.allocation.width
        h = self.allocation.height
        result = p.copy()
        if translate:
            result[0] -= 0.5*w
            result[1] -= 0.5*h
        if w < h:
            result /= w
        else:
            result /= h
        result[1] *= -1
        return result

    def camera_to_screen(self, p, translate=True):
        w = self.allocation.width
        h = self.allocation.height
        result = p.copy()
        result[1] *= -1
        if w < h:
            result *= w
        else:
            result *= h
        if translate:
            result[0] += 0.5*w
            result[1] += 0.5*h
        return result.astype(int)


