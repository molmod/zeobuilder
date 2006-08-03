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
from zeobuilder.actions.abstract import ConnectBase
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.nodes.meta import PublishedProperties, Property
from zeobuilder.nodes.model_object import ModelObjectInfo
from zeobuilder.nodes.vector import Vector
from zeobuilder.nodes.color_mixin import ColorMixin
from zeobuilder.gui.fields_dialogs import DialogFieldInfo
import zeobuilder.gui.fields as fields

from OpenGL.GL import *
from OpenGL.GLU import *

import numpy

import math


__all__ = ["Minimiser"]


class Minimiser(Vector, ColorMixin):
    info = ModelObjectInfo("plugins/builder/minimiser.svg")

    #
    # Properties
    #

    def set_radius(self, radius):
        self.radius = radius
        self.invalidate_draw_list()

    def set_quality(self, quality):
        self.quality = quality
        self.invalidate_draw_list()

    published_properties = PublishedProperties({
        "radius": Property(0.5, lambda self: self.radius, set_radius),
        "quality": Property(15, lambda self: self.quality, set_quality),
    })

    #
    # Dialog fields (see action EditProperties)
    #

    dialog_fields = set([
        DialogFieldInfo("Geometry", (2, 2), fields.faulty.Length(
            label_text="Radius",
            attribute_name="radius",
            low=0.0,
            low_inclusive=False,
        )),
        DialogFieldInfo("Markup", (1, 3), fields.faulty.Int(
            label_text="Quality",
            attribute_name="quality",
            minimum=3,
        )),
    ])

    #
    # Draw
    #

    def draw(self):
        Vector.draw(self)
        if self.length <= 0: return
        # halter
        ColorMixin.draw(self)
        gluCylinder(self.quadric, self.radius, 0.0, 0.5*self.length, self.quality, 1)
        glTranslate(0.0, 0.0, 0.5*self.length)
        gluCylinder(self.quadric, 0.0, self.radius, 0.5*self.length, self.quality, 1)

    def write_pov(self, indenter):
        if self.length <= 0: return
        indenter.write_line("union {", 1)
        indenter.write_line("cone {", 1)
        indenter.write_line("<0.0, 0.0, 0.0>, %f, <0.0, 0.0, %f>, 0.0" % (self.radius, 0.5*self.radius))
        indenter.write_line("pigment { rgb <%f, %f, %f> }" % tuple(self.color[0:3]))
        indenter.write_line("finish { my_finish }")
        indenter.write_line("}", -1)
        indenter.write_line("cone {", 1)
        indenter.write_line("<0.0, 0.0, %f>, 0.0, <0.0, 0.0, %f>, %f" % (0.5*self.radius, self.length, self.radius))
        indenter.write_line("pigment { rgb <%f, %f, %f> }" % tuple(self.color[0:3]))
        indenter.write_line("finish { my_finish }")
        indenter.write_line("}", -1)
        Vector.write_pov(self, indenter)
        indenter.write_line("}", -1)

    #
    # Revalidation
    #

    def revalidate_bounding_box(self):
        Vector.revalidate_bounding_box(self)
        if self.length > 0:
            self.bounding_box.extend_with_point(numpy.array([-self.radius, -self.radius, 0]))
            self.bounding_box.extend_with_point(numpy.array([self.radius, self.radius, self.length]))


class ConnectMinimiser(ConnectBase):
    description = "Connect with minimiser"
    menu_info = MenuInfo("default/_Object:tools/_Connect:pair", "_Minimiser", image_name="plugins/builder/minimiser.svg", order=(0, 4, 1, 3, 0, 4))

    def new_connector(self, begin, end):
        return Minimiser(targets=[begin, end])


nodes = {
    "Minimiser": Minimiser
}


actions = {
    "ConnectMinimiser": ConnectMinimiser
}
