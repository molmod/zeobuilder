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
from zeobuilder.nodes.meta import PublishedProperties, Property
from zeobuilder.nodes.elementary import GLGeometricBase
from zeobuilder.nodes.color_mixin import ColorMixin
from zeobuilder.actions.abstract import AddBase
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.gui import load_image
from zeobuilder.gui.fields_dialogs import DialogFieldInfo
from zeobuilder.transformations import Complete
import zeobuilder.gui.fields as fields

from OpenGL.GL import *
import copy, numpy


class Box(GLGeometricBase, ColorMixin):
    icon = load_image("box.svg", (20, 20))

    def initnonstate(self):
        GLGeometricBase.initnonstate(self, Complete)

    #
    # Properties
    #

    def set_size(self, size):
        self.size = size
        self.invalidate_draw_list()
        self.invalidate_boundingbox_list()

    published_properties = PublishedProperties({
        "size": Property(numpy.array([1.0, 1.0, 1.0]), lambda self: self.size, set_size),
    })

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
        glBegin(GL_QUADS)
        #
        glNormal3f(0, 0, -1.0)
        glVertex3f(-0.5*self.size[0],  0.5*self.size[1], -0.5*self.size[2])
        glVertex3f( 0.5*self.size[0],  0.5*self.size[1], -0.5*self.size[2])
        glVertex3f( 0.5*self.size[0], -0.5*self.size[1], -0.5*self.size[2])
        glVertex3f(-0.5*self.size[0], -0.5*self.size[1], -0.5*self.size[2])
        #
        glNormal3f(0, 0, 1.0)
        glVertex3f(-0.5*self.size[0], -0.5*self.size[1],  0.5*self.size[2])
        glVertex3f( 0.5*self.size[0], -0.5*self.size[1],  0.5*self.size[2])
        glVertex3f( 0.5*self.size[0],  0.5*self.size[1],  0.5*self.size[2])
        glVertex3f(-0.5*self.size[0],  0.5*self.size[1],  0.5*self.size[2])
        #
        glNormal3f(0, -1.0, 0)
        glVertex3f(-0.5*self.size[0], -0.5*self.size[1], -0.5*self.size[2])
        glVertex3f( 0.5*self.size[0], -0.5*self.size[1], -0.5*self.size[2])
        glVertex3f( 0.5*self.size[0], -0.5*self.size[1],  0.5*self.size[2])
        glVertex3f(-0.5*self.size[0], -0.5*self.size[1],  0.5*self.size[2])
        #
        glNormal3f(0,  1.0, 0)
        glVertex3f(-0.5*self.size[0],  0.5*self.size[1],  0.5*self.size[2])
        glVertex3f( 0.5*self.size[0],  0.5*self.size[1],  0.5*self.size[2])
        glVertex3f( 0.5*self.size[0],  0.5*self.size[1], -0.5*self.size[2])
        glVertex3f(-0.5*self.size[0],  0.5*self.size[1], -0.5*self.size[2])
        #
        glNormal3f(-1.0, 0, 0)
        glVertex3f(-0.5*self.size[0], -0.5*self.size[1],  0.5*self.size[2])
        glVertex3f(-0.5*self.size[0],  0.5*self.size[1],  0.5*self.size[2])
        glVertex3f(-0.5*self.size[0],  0.5*self.size[1], -0.5*self.size[2])
        glVertex3f(-0.5*self.size[0], -0.5*self.size[1], -0.5*self.size[2])
        #
        glNormal3f( 1.0, 0, 0)
        glVertex3f( 0.5*self.size[0], -0.5*self.size[1], -0.5*self.size[2])
        glVertex3f( 0.5*self.size[0],  0.5*self.size[1], -0.5*self.size[2])
        glVertex3f( 0.5*self.size[0],  0.5*self.size[1],  0.5*self.size[2])
        glVertex3f( 0.5*self.size[0], -0.5*self.size[1],  0.5*self.size[2])
        glEnd()

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
    menu_info = MenuInfo("default/_Object:tools/_Add:3d", "_Box", image_name="box.svg", order=(0, 4, 1, 0, 0, 0))

    def analyze_selection():
        return AddBase.analyze_selection(Box)
    analyze_selection = staticmethod(analyze_selection)

    def do(self):
        AddBase.do(self, Box)


nodes = {
    "Box": Box
}

actions = {
    "AddBox": AddBox,
}

