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


from zeobuilder.nodes.meta import NodeClass, PublishedProperties, Property
from zeobuilder.gui.fields_dialogs import DialogFieldInfo
import zeobuilder.gui.fields as fields

from OpenGL.GL import *
import numpy


__all__ = ["ColorMixin", "DoubleSidedColorMixin"]


class ColorMixin(object):

    __metaclass__ = NodeClass

    #
    # Properties
    #

    def set_color(self, color):
        self.color = color
        self.invalidate_draw_list()

    published_properties = PublishedProperties({
        "color": Property(numpy.array([0.7, 0.7, 0.7, 1.0]), lambda self: self.color, set_color)
    })

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
        glMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, self.color)
        #if self.double_sided:
        #    glMaterial(GL_BACK, GL_AMBIENT_AND_DIFFUSE, self.color)


class DoubleSidedColorMixin(object):

    __metaclass__ = NodeClass

    #
    # Properties
    #

    def set_front_color(self, front_color):
        self.front_color = front_color
        self.invalidate_draw_list()

    def set_back_color(self, back_color):
        self.back_color = back_color
        self.invalidate_draw_list()

    published_properties = PublishedProperties({
        "front_color": Property(numpy.array([0.7, 0.7, 0.7, 1.0]), lambda self: self.front_color, set_front_color),
        "back_color": Property(numpy.array([0.7, 0.7, 0.7, 1.0]), lambda self: self.back_color, set_back_color),
    })

    #
    # Dialog fields (see action EditProperties)
    #

    dialog_fields = set([
        DialogFieldInfo("Markup", (1, 0), fields.edit.Color(
            label_text="Front color",
            attribute_name="front_color",
        )),
        DialogFieldInfo("Markup", (1, 1), fields.edit.Color(
            label_text="Back color",
            attribute_name="back_color",
        ))
    ])

    #
    # Draw
    #

    def draw(self):
        glMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, self.front_color)
        glMaterial(GL_BACK, GL_AMBIENT_AND_DIFFUSE, self.back_color)


