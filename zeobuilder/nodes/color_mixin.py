# -*- coding: utf-8 -*-
# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 - 2012 Toon Verstraelen <Toon.Verstraelen@UGent.be>, Center
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
#--


from zeobuilder import context
from zeobuilder.nodes.meta import NodeClass, Property
from zeobuilder.gui.fields_dialogs import DialogFieldInfo
from zeobuilder.undefined import Undefined
import zeobuilder.gui.fields as fields

import numpy, gobject


__all__ = ["ColorMixin", "UserColorMixin"]


class ColorMixin(gobject.GObject):

    __metaclass__ = NodeClass

    #
    # Properties
    #

    def set_color(self, color, init=False):
        self.color = color
        if not init:
            self.invalidate_draw_list()

    properties = [
        Property("color", numpy.array([0.7, 0.7, 0.7, 1.0]), lambda self: self.color, set_color)
    ]

    #
    # Dialog fields (see action EditProperties)
    #

    dialog_fields = set([
        DialogFieldInfo("Markup", (1, 0), fields.edit.Color(
            label_text="Color",
            attribute_name="color",
        ))
    ])

    #
    # Draw
    #

    def draw(self):
        context.application.vis_backend.set_color(*self.color)


class UserColorMixin(gobject.GObject):

    __metaclass__ = NodeClass

    #
    # Properties
    #

    def set_user_color(self, user_color, init=False):
        self.user_color = user_color
        if not init:
            self.invalidate_draw_list()

    properties = [
        Property("user_color", Undefined(numpy.array([0.7, 0.7, 0.7, 1.0])), lambda self: self.user_color, set_user_color, signal=True)
    ]

    #
    # Dialog fields (see action EditProperties)
    #

    dialog_fields = set([
        DialogFieldInfo("Markup", (1, 7), fields.optional.CheckOptional(
            fields.edit.Color(
                label_text="User defined color",
                attribute_name="user_color",
            )
        )),
    ])

    #
    # Draw
    #

    def get_color(self):
        if isinstance(self.user_color, Undefined):
            return self.default_color
        else:
            return self.user_color

    def draw(self):
        context.application.vis_backend.set_color(*self.get_color())


