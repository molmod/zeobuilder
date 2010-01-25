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
from zeobuilder.nodes.reference import SpatialReference
from zeobuilder.nodes.elementary import GLReferentBase
from zeobuilder.nodes.color_mixin import ColorMixin
from zeobuilder.gui.fields_dialogs import DialogFieldInfo
import zeobuilder.gui.fields as fields

from molmod import Complete, Translation

import numpy


__all__ = ["Vector"]


class Vector(GLReferentBase):

    #
    # State
    #

    def initnonstate(self):
        GLReferentBase.initnonstate(self)
        self.orientation = Complete.identity()
        self.set_children([
            SpatialReference(prefix="Begin"),
            SpatialReference(prefix="End")
        ])

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
            self.length = numpy.sqrt(numpy.dot(relative_translation, relative_translation))
            if self.length > 0:
                t = self.children[0].translation_relative_to(self.parent)
                c = relative_translation[2] / self.length
                if c >= 1.0:
                    self.orientation = Translation(t)
                elif c <= -1.0:
                    alpha = numpy.pi
                    axis = numpy.array([1.0, 0.0, 0.0])
                    self.orientation = Complete.from_properties(alpha, axis, False, t)
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
                    alpha = numpy.arccos(c)
                    axis = numpy.array([a, b, 0.0])
                    self.orientation = Complete.from_properties(alpha, axis, False, t)

    def define_target(self, reference, new_target):
        GLReferentBase.define_target(self, reference, new_target)
        self.invalidate_boundingbox_list()
        self.invalidate_draw_list()

    def target_moved(self, reference, target):
        GLReferentBase.target_moved(self, reference, target)
        self.invalidate_boundingbox_list()
        self.invalidate_draw_list()

    def get_neighbor(self, one_target):
        if self.children[0].target == one_target:
            return self.children[1].target
        else:
            return self.children[0].target


