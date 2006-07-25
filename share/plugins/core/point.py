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
import numpy


class Point(GLGeometricBase, ColorMixin):
    icon = load_image("point.svg", (20, 20))

    def initnonstate(self):
        GLGeometricBase.initnonstate(self, Translation)

    #
    # Properties
    #

    def set_spike_length(self, spike_length):
        self.spike_length = spike_length
        self.invalidate_draw_list()
        self.invalidate_boundingbox_list()

    def set_spike_thickness(self, spike_thickness):
        self.spike_thickness = spike_thickness
        self.invalidate_draw_list()
        self.invalidate_boundingbox_list()

    published_properties = PublishedProperties({
        "spike_length": Property(0.3, lambda self: self.spike_length, set_spike_length),
        "spike_thickness": Property(0.1, lambda self: self.spike_thickness, set_spike_thickness),
    })

    #
    # Dialog fields (see action EditProperties)
    #

    dialog_fields = set([
        DialogFieldInfo("Geometry", (2, 7), fields.faulty.Length(
            label_text="Spike length", 
            attribute_name="spike_length", 
            invalid_message="Invalid spike length.", 
            low=0.0, 
            low_inclusive=False
        )),
        DialogFieldInfo("Geometry", (2, 8), fields.faulty.Length(
            label_text="Spike thickness", 
            attribute_name="spike_thickness", 
            invalid_message="Invalid spike thickness.", 
            low=0.0, 
            low_inclusive=False
        ))
    ])

    #
    # Draw
    #

    def draw_spike(self):
        ColorMixin.draw(self)
        glBegin(GL_QUAD_STRIP)
        # (100)
        glNormal3f(0.5773502692, -0.5773502692, -0.5773502692)
        glVertex3f(self.spike_length, self.spike_length, self.spike_length)
        glNormal3f(1, 0, 0)
        glVertex3f(self.spike_thickness, 0, 0)
        # (010)
        glNormal3f(-0.5773502692, 0.5773502692, -0.5773502692)
        glVertex3f(self.spike_length, self.spike_length, self.spike_length)
        glNormal3f(0, 1, 0)
        glVertex3f(0, self.spike_thickness, 0)
        # (010)
        glNormal3f(-0.5773502692, -0.5773502692, 0.5773502692)
        glVertex3f(self.spike_length, self.spike_length, self.spike_length)
        glNormal3f(0, 0, 1)
        glVertex3f(0, 0, self.spike_thickness)
        # (100)
        glNormal3f(0.5773502692, -0.5773502692, -0.5773502692)
        glVertex3f(self.spike_length, self.spike_length, self.spike_length)
        glNormal3f(1, 0, 0)
        glVertex3f(self.spike_thickness, 0, 0)
        glEnd()

    def draw(self):
        GLGeometricBase.draw(self)
        glPushMatrix()
        for i in range(2):
            for i in range(4):
                self.draw_spike()
                glRotate(90, 1.0, 0.0, 0.0)
            glRotate(180, 0.0, 1.0, 0.0)
        glPopMatrix()

    def write_pov(self, indenter):
        def write_spike(signs):
            indenter.write_line("triangle {", 1)
            indenter.write_line("< %f,  %f,  %f>," % (signs[0]*self.spike_length, signs[1]*self.spike_length, signs[2]*self.spike_length))
            indenter.write_line("< %f, 0.0, 0.0>," % (signs[0]*self.spike_thickness))
            indenter.write_line("<0.0,  %f, 0.0>" % (signs[1]*self.spike_thickness))
            indenter.write_line("}", -1)
            indenter.write_line("triangle {", 1)
            indenter.write_line("< %f,  %f,  %f>," % (signs[0]*self.spike_length, signs[1]*self.spike_length, signs[2]*self.spike_length))
            indenter.write_line("<0.0,  %f, 0.0>," % (signs[1]*self.spike_thickness))
            indenter.write_line("<0.0, 0.0,  %f>" % (signs[2]*self.spike_thickness))
            indenter.write_line("}", -1)
            indenter.write_line("triangle {", 1)
            indenter.write_line("< %f,  %f,  %f>," % (signs[0]*self.spike_length, signs[1]*self.spike_length, signs[2]*self.spike_length))
            indenter.write_line("<0.0, 0.0,  %f>," % (signs[2]*self.spike_thickness))
            indenter.write_line("< %f, 0.0, 0.0>" % (signs[0]*self.spike_thickness))
            indenter.write_line("}", -1)

        signslist = [((i/4 % 2) * 2 - 1, (i/2 % 2) * 2 - 1, (i % 2) * 2 - 1) for i in range(8)]
        indenter.write_line("mesh {", 1)
        for signs in signslist:
            write_spike(signs)
        indenter.write_line("inside_vector <0.0, 0.0, 0.0>")
        indenter.write_line("pigment { rgb <%f, %f, %f> }" % tuple(self.color[0:3]))
        GLGeometricBase.write_pov(self, indenter)
        indenter.write_line("}", -1)

    #
    # Revalidation
    #

    def revalidate_bounding_box(self):
        GLGeometricBase.revalidate_bounding_box(self)
        self.bounding_box.extend_with_corners([-self.spike_length*numpy.ones(3, float), self.spike_length*numpy.ones(3, float)])


class AddPoint(AddBase):
    description = "Add point"
    menu_info = MenuInfo("default/_Object:tools/_Add:3d", "_Point", image_name="point.svg", order=(0, 4, 1, 0, 0, 2))

    def analyze_selection():
        return AddBase.analyze_selection(Point)
    analyze_selection = staticmethod(analyze_selection)

    def do(self):
        AddBase.do(self, Point)


nodes = {
    "Point": Point
}

actions = {
    "AddPoint": AddPoint,
}
