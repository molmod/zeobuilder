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
from zeobuilder.nodes.color_mixin import ColorMixin
from zeobuilder.nodes.vector import Vector
from zeobuilder.gui.fields_dialogs import DialogFieldInfo
from zeobuilder.transformations import Complete
import zeobuilder.gui.fields as fields

from OpenGL.GL import *
from OpenGL.GLU import *
import math, numpy


class Arrow(Vector, ColorMixin):
    info = ModelObjectInfo("plugins/core/arrow.svg")

    #
    # Properties
    #

    def set_radius(self, radius):
        self.radius = radius
        self.invalidate_draw_list()
        self.invalidate_boundingbox_list()

    def set_quality(self, quality):
        self.quality = quality
        self.invalidate_draw_list()

    def set_arrow_length(self, arrow_length):
        self.arrow_length = arrow_length
        self.invalidate_draw_list()
        self.invalidate_boundingbox_list()

    def set_arrow_radius(self, arrow_radius):
        self.arrow_radius = arrow_radius
        self.invalidate_draw_list()
        self.invalidate_boundingbox_list()

    def set_arrow_position(self, arrow_position):
        self.arrow_position = arrow_position
        self.invalidate_draw_list()
        self.invalidate_boundingbox_list()

    published_properties = PublishedProperties({
        "radius": Property(0.15, lambda self: self.radius, set_radius),
        "quality": Property(15, lambda self: self.quality, set_quality),
        "arrow_length": Property(0.6, lambda self: self.arrow_length, set_arrow_length),
        "arrow_radius": Property(0.3, lambda self: self.arrow_radius, set_arrow_radius),
        "arrow_position": Property(0.5, lambda self: self.arrow_position, set_arrow_position)
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
        DialogFieldInfo("Geometry", (2, 3), fields.faulty.Length(
            label_text="Arrow length",
            attribute_name="arrow_length",
            low=0.0,
        )),
        DialogFieldInfo("Geometry", (2, 4), fields.faulty.Length(
            label_text="Arrow radius",
            attribute_name="arrow_radius",
            low=0.0,
            low_inclusive=False,
        )),
        DialogFieldInfo("Geometry", (2, 5), fields.faulty.Float(
            label_text="Arrow position",
            attribute_name="arrow_position",
            low=0.0,
            high=1.0,
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
        ColorMixin.draw(self)
        if self.length == 0.0: return
        # usefull variable
        if self.arrow_radius <= 0:
            arrowtop_length = self.arrow_length
        else:
            arrowtop_length = self.arrow_length/self.arrow_radius*self.radius
        # stick and bottom
        if (self.length - arrowtop_length > 0) and (self.radius > 0):
            gluCylinder(self.quadric, self.radius, self.radius, self.length - arrowtop_length, self.quality, 1)
            gluQuadricOrientation(self.quadric, GLU_INSIDE)
            gluDisk(self.quadric, 0, self.radius, self.quality, 1)
        # arrowtop
        if (self.radius > 0):
            if (arrowtop_length > 0):
                glPushMatrix()
                glTranslate(0.0, 0.0, self.length - arrowtop_length)
                gluQuadricOrientation(self.quadric, GLU_OUTSIDE)
                gluCylinder(self.quadric, self.radius, 0, arrowtop_length, self.quality, self.quality)
                glPopMatrix()
            else:
                glPushMatrix()
                glTranslate(0.0, 0.0, self.length)
                gluQuadricOrientation(self.quadric, GLU_OUTSIDE)
                gluDisk(self.quadric, 0, self.radius, self.quality, 1)
                glPopMatrix()
        # arrow
        if (self.arrow_radius - self.radius > 0) and (self.arrow_length - arrowtop_length) > 0:
            glPushMatrix()
            glTranslate(0.0, 0.0, (self.length - self.arrow_length)*(self.arrow_position))
            gluQuadricOrientation(self.quadric, GLU_OUTSIDE)
            gluCylinder(self.quadric, self.arrow_radius, self.radius, self.arrow_length - arrowtop_length, self.quality, self.quality)
            gluQuadricOrientation(self.quadric, GLU_INSIDE)
            gluDisk(self.quadric, 0, self.arrow_radius, self.quality, 1)
            glPopMatrix()
        gluQuadricOrientation(self.quadric, GLU_OUTSIDE)

    def write_pov(self, indenter):
        self.calc_vector_dimensions()
        if self.length == 0.0: return
        # usefull variable
        if self.arrow_radius <= 0:
            arrowtop_length = self.arrow_length
        else:
            arrowtop_length = self.arrow_length/self.arrow_radius*self.radius
        # group all
        indenter.write_line("union {", 1)
        # stick and bottom
        if (self.length - arrowtop_length > 0) and (self.radius > 0):
            indenter.write_line("cylinder {", 1)
            indenter.write_line("<0.0, 0.0, 0.0>, <0.0, 0.0, %f>, %f" % (self.length - arrowtop_length, self.radius))
            indenter.write_line("pigment { rgb <%f, %f, %f> }" % tuple(self.color[0:3]))
            indenter.write_line("finish { my_finish }")
            indenter.write_line("}", -1)
        # arrowtop
        if (self.radius > 0) and (arrowtop_length > 0):
            indenter.write_line("cone {", 1)
            indenter.write_line("<0.0, 0.0, %f>, %f, <0.0, 0.0, %f>, 0.0" % (self.length - arrowtop_length, self.radius, self.length))
            indenter.write_line("pigment { rgb <%f, %f, %f> }" % tuple(self.color[0:3]))
            indenter.write_line("finish { my_finish }")
            indenter.write_line("}", -1)
        # arrow
        if (self.arrow_radius - self.radius > 0) and (self.arrow_length - arrowtop_length) > 0:
            indenter.write_line("cone {", 1)
            indenter.write_line("<0.0, 0.0, %f>, %f, <0.0, 0.0, %f>, %f" % ((self.length - self.arrow_length)*self.arrow_position, self.arrow_radius, (self.length - self.arrow_length)*self.arrow_position + self.arrow_length - arrowtop_length, self.radius))
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
        if self.length > 0.0:
            self.bounding_box.extend_with_corners([numpy.array([0.0, 0.0, 0.0]), numpy.array([0.0, 0.0, self.length])])
            temp = {True: self.radius, False: self.arrow_radius}[self.radius > self.arrow_radius]
            self.bounding_box.extend_with_corners([numpy.array([-temp, -temp, 0.0]), numpy.array([ temp,  temp, 0.0])])


class ConnectArrow(ConnectBase):
    description = "Connect with arrow"
    menu_info = MenuInfo("default/_Object:tools/_Connect:pair", "_Arrow", image_name="plugins/core/arrow.svg", order=(0, 4, 1, 3, 0, 0))

    def new_connector(self, begin, end):
        return Arrow(targets=[begin, end])


nodes = {
    "Arrow": Arrow
}

actions = {
    "ConnectArrow": ConnectArrow,
}
