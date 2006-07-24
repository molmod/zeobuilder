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


from zeobuilder import context
from zeobuilder.nodes.meta import DialogFieldInfo
from zeobuilder.nodes.reference import SpatialReference
from zeobuilder.nodes.elementary import GLReferentBase
from zeobuilder.nodes.color_mixin import ColorMixin
from zeobuilder.transformations import Complete
import zeobuilder.gui.fields as fields

from OpenGL.GL import *
from OpenGL.GLU import *
import numpy

import math


__all__ = ["Vector"]


class Vector(GLReferentBase):

    #
    # State
    #

    def initnonstate(self):
        GLReferentBase.initnonstate(self)
        self.orientation = Complete()

    def create_references(self):
        return [
            SpatialReference(prefix="Begin"),
            SpatialReference(prefix="End")
        ]

    #
    # Tree
    #

    def initialize_gl(self):
        GLReferentBase.initialize_gl(self)
        self.quadric = context.application.main.drawing_area.scene.quadric

    def release_gl(self):
        GLReferentBase.release_gl(self)
        self.quadric = None


    #
    # Dialog fields (see action EditProperties)
    #

    dialog_fields = set([
        DialogFieldInfo("Basic", (0, 2), fields.read.VectorLength("Vector length")),
    ])

    #
    # Draw
    #

    def draw(self):
        self.calc_vector_dimensions()
        self.orientation.gl_apply()

    def write_pov(self, indenter):
        GLReferentBase.write_pov(self, indenter)
        indenter.write_line("matrix <%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f>" % (tuple(numpy.ravel(numpy.transpose(self.orientation.rotation_matrix))) + tuple(self.orientation.translation_vector)))

    #
    # Revalidation
    #

    def revalidate_total_list(self):
        if self.total_list > 0:
            glNewList(self.total_list, GL_COMPILE)
            if self.visible:
                glPushName(self.draw_list)
                glPushMatrix()
                if self.selected: glCallList(self.boundingbox_list)
                glCallList(self.draw_list)
                glPopMatrix()
                glPopName()
            glEndList()
            self.total_list_valid = True

    def revalidate_draw_list(self):
        if self.draw_list > 0:
            GLReferentBase.revalidate_draw_list(self)

    def revalidate_boundingbox_list(self):
        if self.boundingbox_list > 0:
            #print "Compiling selection list (" + str(self.boundingbox_list) + "): " + str(self.name)
            glNewList(self.boundingbox_list, GL_COMPILE)
            glPushMatrix()
            self.orientation.gl_apply()
            self.revalidate_bounding_box()
            self.bounding_box.draw()
            glPopMatrix()
            glEndList()
            self.boundingbox_list_valid = True

    #
    # Frame
    #

    def get_bounding_box_in_parent_frame(self):
        return self.bounding_box.transformed(self.orientation)

    #
    # Vector
    #

    def translation_relative_to(self, target, other):
        if target != None:
            return target.get_frame_relative_to(other).translation_vector
        else:
            return None

    def translations_relative_to(self, other):
        return tuple([self.translation_relative_to(self.children[i].target, other) for i in (0, 1)])

    def shortest_vector_relative_to(self, other):
        b, e = self.translations_relative_to(other)
        if (b == None) or (e == None):
            return None
        else:
            return self.parent.shortest_vector(e - b)

    def calc_vector_dimensions(self):
        relative_translation = self.shortest_vector_relative_to(self.parent)
        if relative_translation == None:
            self.length = 0
        else:
            self.length = math.sqrt(numpy.dot(relative_translation, relative_translation))
            if self.length > 0:
                self.orientation.translation_vector = self.translation_relative_to(self.children[0].target, self.parent)
                c = relative_translation[2] / self.length
                if c == 1.0:
                    self.orientation.set_rotation_properties(0, numpy.array([1.0, 0.0, 0.0]), False)
                elif c == -1.0:
                    self.orientation.set_rotation_properties(180, numpy.array([1.0, 0.0, 0.0]), False)
                else:
                    x, y = relative_translation[0], relative_translation[1]
                    if abs(x) < abs(y):
                        signy = {True: 1, False: -1}[y >= 0]
                        a = -signy
                        b = signy * x / y
                    else:
                        signx = {True: 1, False: -1}[x >= 0]
                        a = -signx * y / x
                        b = signx
                    self.orientation.set_rotation_properties(math.acos(c) * 180 / math.pi, numpy.array([a, b, 0.0]), False)

    def set_target(self, reference, target):
        GLReferentBase.set_target(self, reference, target)
        self.invalidate_boundingbox_list()
        self.invalidate_draw_list()

    def target_moved(self, reference, target):
        GLReferentBase.target_moved(self, reference, target)
        self.invalidate_boundingbox_list()
        self.invalidate_draw_list()

