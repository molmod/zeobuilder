# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 - 2010 Toon Verstraelen <Toon.Verstraelen@UGent.be>, Center
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

from OpenGL.GL import glBegin, glCallList, glColor, glDisable, glEnable, \
    glEnd, glEndList, glGenLists, glGetInteger, glGetIntegerv, glLineWidth, \
    glLoadIdentity, glMatrixMode, glNewList, glScale, glScalef, glVertex, \
    glVertex3f, GL_COMPILE, GL_DEPTH, GL_DEPTH_TEST, GL_LIGHTING, GL_LINE, \
    GL_LINES, GL_LINE_LOOP, GL_MODELVIEW, GL_PROJECTION, GL_VIEWPORT


class Tool(object):
    # This is an OpenGL-only implementation
    def __init__(self):
        self.draw_list = None
        self.total_list = None
        self.tools = {
            "clear": self._clear,
            "rectangle": self._rectangle,
            "line": self._line,
            "custom": self._custom,
        }


    def __call__(self, name, *args, **kwargs):
        da = context.application.main.drawing_area
        if not da.get_gl_drawable().gl_begin(da.get_gl_context()): return
        glNewList(self.draw_list, GL_COMPILE)
        self.tools[name](*args, **kwargs)
        glEndList()
        da.get_gl_drawable().gl_end()
        da.queue_draw()

    def initialize_gl(self):
        self.draw_list = glGenLists(1)
        self.total_list = glGenLists(1)
        self.compile_total_list()
        self._clear()

    def compile_total_list(self):
        if self.total_list is not None:
            glNewList(self.total_list, GL_COMPILE)
            # reset a few things
            glDisable(GL_DEPTH_TEST)
            glDisable(GL_LIGHTING)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            # change the modelview to camera coordinates
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
            glCallList(self.draw_list)
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_LIGHTING)
            glEndList()

    def _clear(self):
        pass

    def _rectangle(self, r1, r2):
        glColor(1, 1, 1)
        glLineWidth(1)
        glBegin(GL_LINE_LOOP)
        glVertex3f(r1[0], r1[1], 0.0)
        glVertex3f(r2[0], r1[1], 0.0)
        glVertex3f(r2[0], r2[1], 0.0)
        glVertex3f(r1[0], r2[1], 0.0)
        glEnd()

    def _line(self, r1, r2):
        glColor(1, 1, 1)
        glLineWidth(1)
        glBegin(GL_LINES)
        glVertex3f(r1[0], r1[1], 0.0)
        glVertex3f(r2[0], r2[1], 0.0)
        glEnd()

    def _custom(self, draw_function):
        draw_function()


