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


from zeobuilder.nodes.meta import NodeClass, Property
from zeobuilder.gui.fields_dialogs import DialogFieldInfo
import zeobuilder.gui.fields as fields

from molmod.units import from_angstrom

from OpenGL.GL import *
import numpy

import copy


__all__ = ["FrameAxes", "BoundingBox"]


def draw_axis_spike(thickness, length):
    glBegin(GL_QUAD_STRIP)
    # (+,+)
    glNormal(0.0,  0.7071067812,  0.7071067812)
    glVertex(thickness,  thickness,  thickness)
    glVertex(length, 0.0, 0.0)
    # (+,-)
    glNormal(0.0,  0.7071067812, -0.7071067812)
    glVertex(thickness,  thickness, -thickness)
    glVertex(length, 0.0, 0.0)
    # (-,-)
    glNormal(0.0, -0.7071067812, -0.7071067812)
    glVertex(-thickness, -thickness, -thickness)
    glVertex(length, 0.0, 0.0)
    # (-,+)
    glNormal(0.0, -0.7071067812,  0.7071067812)
    glVertex(thickness, -thickness,  thickness)
    glVertex(length, 0.0, 0.0)
    # (+,+)
    glNormal(0.0,  0.7071067812,  0.7071067812)
    glVertex(thickness, thickness, thickness)
    glVertex(length, 0.0, 0.0)
    glEnd()


class FrameAxes(object):

    __metaclass__ = NodeClass

    #
    # Properties
    #

    def set_axis_thickness(self, axis_thickness):
        self.axis_thickness = axis_thickness
        self.invalidate_draw_list()
        self.invalidate_boundingbox_list()

    def set_axis_length(self, axis_length):
        self.axis_length = axis_length
        self.invalidate_draw_list()
        self.invalidate_boundingbox_list()

    def set_axes_visible(self, axes_visible):
        self.axes_visible = axes_visible
        self.invalidate_draw_list()
        self.invalidate_boundingbox_list()

    properties = [
        Property("axis_thickness", from_angstrom(0.1), lambda self: self.axis_thickness, set_axis_thickness),
        Property("axis_length", from_angstrom(1.0), lambda self: self.axis_length, set_axis_length),
        Property("axes_visible", True, lambda self: self.axes_visible, set_axes_visible)
    ]

    #
    # Dialog fields (see action EditProperties)
    #

    dialog_fields = set([
        DialogFieldInfo("Geometry", (2, 0), fields.faulty.Length(
            label_text="Axis thickness",
            attribute_name="axis_thickness",
            low=0.0,
            low_inclusive=False,
        )),
        DialogFieldInfo("Geometry", (2, 1), fields.faulty.Length(
            label_text="Axes length",
            attribute_name="axis_length",
            low=0.0,
            low_inclusive=False,
        )),
        DialogFieldInfo("Markup", (1, 4), fields.edit.CheckButton(
            label_text="Show frame axes",
            attribute_name="axes_visible",
        )),
    ])

    #
    # Draw
    #

    def draw(self, light):
        if self.axes_visible:
            col = {True: 2.0, False: 1.2}[light]
            sat = {True: 0.2, False: 0.1}[light]
            glPushMatrix()
            # x-axis
            glMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [col, sat, sat, 1.0])
            draw_axis_spike(self.axis_thickness, self.axis_length)
            # y-axis
            glRotate(120, 1.0, 1.0, 1.0)
            glMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [sat, col, sat, 1.0])
            draw_axis_spike(self.axis_thickness, self.axis_length)
            # z-axis
            glRotate(120, 1.0, 1.0, 1.0)
            glMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [sat, sat, col, 1.0])
            draw_axis_spike(self.axis_thickness, self.axis_length)
            glPopMatrix()

    def write_pov(self, indenter):
        if not self.axes_visible: return
        def write_axis(color, povrot=None):
            indenter.write_line("mesh {", 1)
            indenter.write_line("triangle {", 1)
            indenter.write_line("<%f, %f, %f>," % (self.axis_thickness,  self.axis_thickness,  self.axis_thickness))
            indenter.write_line("<%f, 0.0, 0.0>," % self.axis_length)
            indenter.write_line("<%f, %f, %f>" % (self.axis_thickness,  self.axis_thickness, -self.axis_thickness))
            indenter.write_line("}", -1)
            indenter.write_line("triangle {", 1)
            indenter.write_line("<%f, %f, %f>," % (self.axis_thickness,  self.axis_thickness, -self.axis_thickness))
            indenter.write_line("<%f, 0.0, 0.0>," % self.axis_length)
            indenter.write_line("<%f, %f, %f>" % (-self.axis_thickness, -self.axis_thickness, -self.axis_thickness))
            indenter.write_line("}", -1)
            indenter.write_line("triangle {", 1)
            indenter.write_line("<%f, %f, %f>," % (-self.axis_thickness, -self.axis_thickness, -self.axis_thickness))
            indenter.write_line("<%f, 0.0, 0.0>," % self.axis_length)
            indenter.write_line("<%f, %f, %f>" % (self.axis_thickness, -self.axis_thickness,  self.axis_thickness))
            indenter.write_line("}", -1)
            indenter.write_line("triangle {", 1)
            indenter.write_line("<%f, %f, %f>," % (self.axis_thickness, -self.axis_thickness,  self.axis_thickness))
            indenter.write_line("<%f, 0.0, 0.0>," % self.axis_length)
            indenter.write_line("<%f, %f, %f>" % (self.axis_thickness, self.axis_thickness, self.axis_thickness))
            indenter.write_line("}", -1)
            indenter.write_line("inside_vector <0.0, 0.0, 0.0>")
            indenter.write_line("pigment { color %s }" % color)
            indenter.write_line("finish { my_finish }")
            if povrot is not None: indenter.write_line(povrot)
            indenter.write_line("}", -1)

        write_axis("Red")
        write_axis("Green", "matrix <0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0>")
        write_axis("Blue", "matrix <0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0>")

    #
    # Revalidation
    #

    def extend_bounding_box(self, bounding_box):
        if self.axes_visible:
            bounding_box.extend_with_corners([numpy.array([-self.axis_thickness, -self.axis_thickness, -self.axis_thickness]),
                                              numpy.array([ self.axis_length,     self.axis_length,     self.axis_length   ])])


class BoundingBox(object):
    def __init__(self):
        self.clear()

    def clear(self):
        self.corners = None

    def extend_with_point(self, point):
        if self.corners is None:
            self.corners = [copy.deepcopy(point), copy.deepcopy(point)]
        else:
            for i in range(3):
                if point[i] < self.corners[0][i]: self.corners[0][i] = point[i]
                if point[i] > self.corners[1][i]: self.corners[1][i] = point[i]

    def extend_with_corners(self, corners):
        if self.corners is None:
            self.corners = copy.deepcopy(corners)
        else:
            for i in range(3):
                if corners[0][i] < self.corners[0][i]: self.corners[0][i] = corners[0][i]
                if corners[1][i] > self.corners[1][i]: self.corners[1][i] = corners[1][i]

    def transformed(self, transformation):
        result = BoundingBox()
        if self.corners is None: return result
        combinations = ((0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0), (0, 0, 1), (1, 0, 1), (0, 1, 1), (1, 1, 1))
        for c in combinations:
            result.extend_with_point(transformation.vector_apply(numpy.array([self.corners[c[0]][0], self.corners[c[1]][1], self.corners[c[2]][2]])))
        return result

    #
    # Draw
    #

    def draw(self):
        if self.corners is None: return
        # we can asume that self.bounding_box is defined. self.bounding_box defines a box
        # that surrounds the content of the current geometric object and
        # has it's ridges parallel to the frame axes. It has the following
        # structure: [[lowest_x, lowest_y, lowest_z], [highest_x, highest_y, highest_z]]

        # a margin of sel_margin is left between the bounding_box edges and the frame
        # that visualises the selection
        sel_margin = 0.06
        gray = 4.5
        glMaterial(GL_FRONT, GL_DIFFUSE, [0.0, 0.0, 0.0, 0.0])
        glMaterial(GL_FRONT, GL_AMBIENT, [gray, gray, gray, 1.0])
        glMaterial(GL_FRONT, GL_SPECULAR, [0.0, 0.0, 0.0, 0.0])

        # the ridges parallell to the z-axis
        glLineWidth(1)
        #glLineStipple(1, -1)
        #glLineStipple(1, -21846)
        glBegin(GL_LINES)
        # 1 -> 5
        glNormalf(-1.0, -1.0,  0.0)
        glVertexf(self.corners[0][0] - sel_margin, self.corners[0][1] - sel_margin, self.corners[1][2] + sel_margin)
        glVertexf(self.corners[0][0] - sel_margin, self.corners[0][1] - sel_margin, self.corners[0][2] - sel_margin)
        # 2 -> 6
        glNormalf( 1.0, -1.0,  0.0)
        glVertexf(self.corners[1][0] + sel_margin, self.corners[0][1] - sel_margin, self.corners[1][2] + sel_margin)
        glVertexf(self.corners[1][0] + sel_margin, self.corners[0][1] - sel_margin, self.corners[0][2] - sel_margin)
        # 3 -> 7
        glNormalf( 1.0,  1.0,  0.0)
        glVertexf(self.corners[1][0] + sel_margin, self.corners[1][1] + sel_margin, self.corners[1][2] + sel_margin)
        glVertexf(self.corners[1][0] + sel_margin, self.corners[1][1] + sel_margin, self.corners[0][2] - sel_margin)
        # 4 -> 8
        glNormalf(-1.0,  1.0,  0.0)
        glVertexf(self.corners[0][0] - sel_margin, self.corners[1][1] + sel_margin, self.corners[1][2] + sel_margin)
        glVertexf(self.corners[0][0] - sel_margin, self.corners[1][1] + sel_margin, self.corners[0][2] - sel_margin)
        glEnd()

        # the ridges parallell to the y-axis
        glBegin(GL_LINES)
        # 1 -> 4
        glNormalf(-1.0,  0.0,  1.0)
        glVertexf(self.corners[0][0] - sel_margin, self.corners[0][1] - sel_margin, self.corners[1][2] + sel_margin)
        glVertexf(self.corners[0][0] - sel_margin, self.corners[1][1] + sel_margin, self.corners[1][2] + sel_margin)
        # 2 -> 3
        glNormalf( 1.0,  0.0,  1.0)
        glVertexf(self.corners[1][0] + sel_margin, self.corners[0][1] - sel_margin, self.corners[1][2] + sel_margin)
        glVertexf(self.corners[1][0] + sel_margin, self.corners[1][1] + sel_margin, self.corners[1][2] + sel_margin)
        # 6 -> 7
        glNormalf( 1.0,  0.0, -1.0)
        glVertexf(self.corners[1][0] + sel_margin, self.corners[0][1] - sel_margin, self.corners[0][2] - sel_margin)
        glVertexf(self.corners[1][0] + sel_margin, self.corners[1][1] + sel_margin, self.corners[0][2] - sel_margin)
        # 5 -> 8
        glNormalf(-1.0,  0.0, -1.0)
        glVertexf(self.corners[0][0] - sel_margin, self.corners[0][1] - sel_margin, self.corners[0][2] - sel_margin)
        glVertexf(self.corners[0][0] - sel_margin, self.corners[1][1] + sel_margin, self.corners[0][2] - sel_margin)
        glEnd()

        # the ridges parallell to the x-axis
        glBegin(GL_LINES)
        # 1 -> 2
        glNormalf( 0.0, -1.0,  1.0)
        glVertexf(self.corners[0][0] - sel_margin, self.corners[0][1] - sel_margin, self.corners[1][2] + sel_margin)
        glVertexf(self.corners[1][0] + sel_margin, self.corners[0][1] - sel_margin, self.corners[1][2] + sel_margin)
        # 4 -> 3
        glNormalf( 0.0,  1.0,  1.0)
        glVertexf(self.corners[0][0] - sel_margin, self.corners[1][1] + sel_margin, self.corners[1][2] + sel_margin)
        glVertexf(self.corners[1][0] + sel_margin, self.corners[1][1] + sel_margin, self.corners[1][2] + sel_margin)
        # 6 -> 5
        glNormalf( 0.0, -1.0, -1.0)
        glVertexf(self.corners[1][0] + sel_margin, self.corners[0][1] - sel_margin, self.corners[0][2] - sel_margin)
        glVertexf(self.corners[0][0] - sel_margin, self.corners[0][1] - sel_margin, self.corners[0][2] - sel_margin)
        # 7 -> 8
        glNormalf( 0.0,  1.0, -1.0)
        glVertexf(self.corners[1][0] + sel_margin, self.corners[1][1] + sel_margin, self.corners[0][2] - sel_margin)
        glVertexf(self.corners[0][0] - sel_margin, self.corners[1][1] + sel_margin, self.corners[0][2] - sel_margin)
        glEnd()

        glMaterial(GL_FRONT, GL_SPECULAR, [0.7, 0.7, 0.7, 1.0])
