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
from zeobuilder.nodes.meta import PublishedProperties, Property, DialogFieldInfo
from zeobuilder.nodes.elementary import GLGeometricBase
from zeobuilder.nodes.color_mixin import ColorMixin
from zeobuilder.actions.abstract import AddBase
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.gui import load_image
from zeobuilder.transformations import Translation
import zeobuilder.gui.fields as fields

from OpenGL.GL import *
from OpenGL.GLUT import *
import numpy


class Sphere(GLGeometricBase, ColorMixin):
    icon = load_image("sphere.svg", (20, 20))

    def initnonstate(self):
        GLGeometricBase.initnonstate(self, Translation)

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

    published_properties = PublishedProperties({
        "radius": Property(0.5, lambda self: self.radius, set_radius),
        "quality": Property(50, lambda self: self.quality, set_quality),
    })

    #
    # Dialog fields (see action EditProperties)
    #

    dialog_fields = set([
        DialogFieldInfo("Geometry", (2, 2), fields.faulty.Length(
            label_text="Radius",
            attribute_name="radius",
            invalid_message="Invalid sphere radius.",
            low=0.0,
            low_inclusive=False,
        )),
        DialogFieldInfo("Markup", (1, 3), fields.faulty.Int(
            label_text="Quality",
            attribute_name="quality",
            invalid_message="Invalid quality",
            minimum=3,
        ))
    ])

    #
    # Draw
    #

    def draw(self):
        GLGeometricBase.draw(self)
        ColorMixin.draw(self)
        glutSolidSphere(self.radius, self.quality, self.quality / 2)

    def write_pov(self, indenter):
        indenter.write_line("sphere {", 1)
        indenter.write_line("<0.0, 0.0, 0.0>, %f" % (self.radius))
        indenter.write_line("pigment { rgb <%f, %f, %f> }" % tuple(self.color[0:3]))
        GLGeometricBase.write_pov(self, indenter)
        indenter.write_line("}", -1)

    #
    # Revalidation
    #

    def revalidate_bounding_box(self):
        GLGeometricBase.revalidate_bounding_box(self)
        self.bounding_box.extend_with_corners([-self.radius*numpy.ones(3, float), self.radius*numpy.ones(3, float)])


class AddSphere(AddBase):
    description = "Add sphere"
    menu_info = MenuInfo("default/_Object:tools/_Add:3d", "_Sphere", image_name="sphere.svg", order=(0, 4, 1, 0, 0, 1))

    def analyze_selection():
        return AddBase.analyze_selection(Sphere)
    analyze_selection = staticmethod(analyze_selection)

    def do(self):
        AddBase.do(self, Sphere)


nodes = {
    "Sphere": Sphere
}

actions = {
    "AddSphere": AddSphere,
}
