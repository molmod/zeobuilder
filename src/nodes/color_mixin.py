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
from zeobuilder.undefined import Undefined
import zeobuilder.gui.fields as fields

from OpenGL.GL import *
import numpy, gobject


__all__ = ["ColorMixin", "UserColorMixin"]


class ColorMixin(gobject.GObject):

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
        glMaterial(GL_BACK, GL_AMBIENT_AND_DIFFUSE, self.color)


class UserColorMixin(gobject.GObject):

    __metaclass__ = NodeClass

    #
    # Properties
    #

    def set_user_color(self, user_color):
        self.user_color = user_color
        self.invalidate_draw_list()

    published_properties = PublishedProperties({
        "user_color": Property(Undefined(numpy.array([0.7, 0.7, 0.7, 1.0])), lambda self: self.user_color, set_user_color, signal=True)
    })

    #
    # Dialog fields (see action EditProperties)
    #

    dialog_fields = set([
        DialogFieldInfo("Markup", (1, 7), fields.optional.CheckOptional(
            fields.edit.Color(
                label_text="User define color",
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

    def default_color(self):
        raise NotImplementedError

    def draw(self):
        glMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, self.get_color())
        glMaterial(GL_BACK, GL_AMBIENT_AND_DIFFUSE, self.get_color())
