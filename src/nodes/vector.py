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
from zeobuilder.nodes.reference import SpatialReference
from zeobuilder.nodes.elementary import GLReferentBase
from zeobuilder.nodes.color_mixin import ColorMixin
from zeobuilder.gui.fields_dialogs import DialogFieldInfo
import zeobuilder.gui.fields as fields

from molmod.transformations import Complete

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
    # Dialog fields (see action EditProperties)
    #

    dialog_fields = set([
        DialogFieldInfo("Basic", (0, 2), fields.read.VectorLength(
            label_text="Vector length"
        )),
    ])

    #
    # Draw
    #

    def draw(self):
        self.calc_vector_dimensions()
        context.application.vis_backend.transform(self.orientation)

    def write_pov(self, indenter):
        GLReferentBase.write_pov(self, indenter)
        indenter.write_line("matrix <%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f>" % (tuple(numpy.ravel(numpy.transpose(self.orientation.r))) + tuple(self.orientation.t)))

    #
    # Revalidation
    #

    def revalidate_total_list(self):
        if self.gl_active:
            vb = context.application.vis_backend
            vb.begin_list(self.total_list)
            if self.visible:
                vb.push_name(self.draw_list)
                vb.push_matrix()
                self.draw_selection()
                vb.call_list(self.draw_list)
                vb.pop_matrix()
                vb.pop_name()
            vb.end_list()
            self.total_list_valid = True

    def revalidate_draw_list(self):
        if self.gl_active:
            GLReferentBase.revalidate_draw_list(self)

    def revalidate_boundingbox_list(self):
        if self.gl_active:
            vb = context.application.vis_backend
            #print "Compiling selection list (" + str(self.boundingbox_list) + "): " + str(self.name)
            vb.begin_list(self.boundingbox_list)
            vb.push_matrix()
            vb.transform(self.orientation)
            self.revalidate_bounding_box()
            self.bounding_box.draw()
            vb.pop_matrix()
            vb.end_list()
            self.boundingbox_list_valid = True

    #
    # Frame
    #

    def get_bounding_box_in_parent_frame(self):
        return self.bounding_box.transformed(self.orientation)

    #
    # Vector
    #

    def shortest_vector_relative_to(self, other):
        b = self.children[0].translation_relative_to(other)
        e = self.children[1].translation_relative_to(other)
        if (b is None) or (e is None):
            return None
        else:
            return self.parent.shortest_vector(e - b)

    def calc_vector_dimensions(self):
        relative_translation = self.shortest_vector_relative_to(self.parent)
        if relative_translation is None:
            self.length = 0
        else:
            self.length = math.sqrt(numpy.dot(relative_translation, relative_translation))
            if self.length > 0:
                self.orientation.t = self.children[0].translation_relative_to(self.parent)
                #axis = numpy.cross(relative_translation, numpy.array([1.0, 0.0, 0.0]))
                c = relative_translation[2] / self.length
                if c >= 1.0:
                    self.orientation.set_rotation_properties(0, numpy.array([1.0, 0.0, 0.0]), False)
                elif c <= -1.0:
                    self.orientation.set_rotation_properties(math.pi, numpy.array([1.0, 0.0, 0.0]), False)
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
                    self.orientation.set_rotation_properties(math.acos(c), numpy.array([a, b, 0.0]), False)

    def define_target(self, reference, new_target):
        GLReferentBase.define_target(self, reference, new_target)
        self.invalidate_boundingbox_list()
        self.invalidate_draw_list()

    def target_moved(self, reference, target):
        GLReferentBase.target_moved(self, reference, target)
        self.invalidate_boundingbox_list()
        self.invalidate_draw_list()

