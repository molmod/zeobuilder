# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 Toon Verstraelen <Toon.Verstraelen@UGent.be>
#
# This file is part of Zeobuilder.
#
# Zeobuilder is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
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
from zeobuilder.actions.abstract import AddBase
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.nodes.meta import Property
from zeobuilder.nodes.model_object import ModelObjectInfo
from zeobuilder.nodes.elementary import GLGeometricBase
from zeobuilder.nodes.color_mixin import ColorMixin
from zeobuilder.gui.fields_dialogs import DialogFieldInfo
import zeobuilder.gui.fields as fields
import zeobuilder.authors as authors

from molmod.transformations import Complete

import copy, numpy


class Box(GLGeometricBase, ColorMixin):
    info = ModelObjectInfo("plugins/basic/box.svg")
    authors = [authors.toon_verstraelen]

    def initnonstate(self):
        GLGeometricBase.initnonstate(self, Complete)

    #
    # Properties
    #

    def set_size(self, size):
        self.size = size
        self.invalidate_draw_list()
        self.invalidate_boundingbox_list()

    properties = [
        Property("size", numpy.array([1.0, 1.0, 1.0]), lambda self: self.size, set_size),
    ]

    #
    # Dialog fields (see action EditProperties)
    #

    dialog_fields = set([
        DialogFieldInfo("Geometry", (2, 6), fields.composed.ComposedArray(
            FieldClass=fields.faulty.Length,
            array_name="%s",
            suffices=["Width", "Height", "Depth"],
            label_text="Box size",
            attribute_name="size",
        ))
    ])

    #
    # Draw
    #

    def draw(self):
        GLGeometricBase.draw(self)
        ColorMixin.draw(self)
        vb = context.application.vis_backend

        x,y,z = numpy.identity(3)
        sides = numpy.array([(x,y,z,z), (x,y,-z,-z), (y,z,x,x), (y,z,-x,-x), (z,x,y,y), (z,x,-y,-y)], float)
        sides[:,:3] *= 0.5*self.size

        vb.draw_quads(*[
            (
                normal,
                [
                     a+b+c,
                     a-b+c,
                    -a-b+c,
                    -a+b+c,
                ]
            ) for a,b,c,normal in sides
        ])

    def write_pov(self, indenter):
        indenter.write_line("box {", 1)
        indenter.write_line("<%f, %f, %f>, <%f, %f, %f>" % (tuple(-self.size*0.5) + tuple(self.size*0.5)))
        indenter.write_line("pigment { rgb <%f, %f, %f> }" % tuple(self.color[0:3]))
        GLGeometricBase.write_pov(self, indenter)
        indenter.write_line("}", -1)

    #
    # Revalidation
    #

    def revalidate_bounding_box(self):
        GLGeometricBase.revalidate_bounding_box(self)
        self.bounding_box.extend_with_corners([-0.5*self.size, 0.5*self.size])


class AddBox(AddBase):
    description = "Add box"
    menu_info = MenuInfo("default/_Object:tools/_Add:3d", "_Box", image_name="plugins/basic/box.svg", order=(0, 4, 1, 0, 0, 0))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        return AddBase.analyze_selection(Box)

    def do(self):
        AddBase.do(self, Box)


nodes = {
    "Box": Box
}

actions = {
    "AddBox": AddBox,
}




