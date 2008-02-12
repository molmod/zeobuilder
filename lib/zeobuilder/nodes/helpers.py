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
# Contact information:
#
# Supervisors
#
# Prof. Dr. Michel Waroquier and Prof. Dr. Ir. Veronique Van Speybroeck
#
# Center for Molecular Modeling
# Ghent University
# Proeftuinstraat 86, B-9000 GENT - BELGIUM
# Tel: +32 9 264 65 59
# Fax: +32 9 264 65 60
# Email: Michel.Waroquier@UGent.be
# Email: Veronique.VanSpeybroeck@UGent.be
#
# Author
#
# Ir. Toon Verstraelen
# Center for Molecular Modeling
# Ghent University
# Proeftuinstraat 86, B-9000 GENT - BELGIUM
# Tel: +32 9 264 65 56
# Email: Toon.Verstraelen@UGent.be
#
# --


from zeobuilder import context
from zeobuilder.nodes.meta import NodeClass, Property
from zeobuilder.gui.fields_dialogs import DialogFieldInfo
import zeobuilder.gui.fields as fields

from molmod.units import angstrom

import numpy

import copy


__all__ = ["FrameAxes", "BoundingBox"]


def draw_axis_spike(thickness, length):
    vb = context.application.vis_backend
    vb.draw_quad_strip(*[
        (
            [0.0,  0.7071067812,  0.7071067812],
            [
                [thickness,  thickness,  thickness],
                [length, 0.0, 0.0],
            ],
        ),
        (
            [0.0,  0.7071067812, -0.7071067812],
            [
                [thickness,  thickness, -thickness],
                [length, 0.0, 0.0],
            ],
        ),
        (
            [0.0, -0.7071067812, -0.7071067812],
            [
                [-thickness, -thickness, -thickness],
                [length, 0.0, 0.0],
            ],
        ),
        (
            [0.0, -0.7071067812,  0.7071067812],
            [
                [thickness, -thickness,  thickness],
                [length, 0.0, 0.0],
            ],
        ),
        (
            [0.0,  0.7071067812,  0.7071067812],
            [
                [thickness, thickness, thickness],
                [length, 0.0, 0.0],
            ],
        ),
    ])


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
        Property("axis_thickness", 0.1*angstrom, lambda self: self.axis_thickness, set_axis_thickness),
        Property("axis_length", 1.0*angstrom, lambda self: self.axis_length, set_axis_length),
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
            vb = context.application.vis_backend
            vb.push_matrix()
            # x-axis
            vb.set_color(col, sat, sat)
            draw_axis_spike(self.axis_thickness, self.axis_length)
            # y-axis
            vb.rotate(120, 1.0, 1.0, 1.0)
            vb.set_color(sat, col, sat)
            draw_axis_spike(self.axis_thickness, self.axis_length)
            # z-axis
            vb.rotate(120, 1.0, 1.0, 1.0)
            vb.set_color(sat, sat, col)
            draw_axis_spike(self.axis_thickness, self.axis_length)
            vb.pop_matrix()

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

        vb = context.application.vis_backend
        vb.set_specular(False)
        vb.set_color(gray, gray, gray)
        vb.set_line_width(1)

        corners = []
        for x in [0, 1]:
            for y in [0, 1]:
                for z in [0, 1]:
                    corners.append([
                        self.corners[x][0] - sel_margin*(2*x-1),
                        self.corners[y][1] - sel_margin*(2*x-1),
                        self.corners[z][2] - sel_margin*(2*x-1),
                    ])
        corners = numpy.array(corners)

        vb.draw_line(corners[0], corners[4])
        vb.draw_line(corners[1], corners[5])
        vb.draw_line(corners[2], corners[6])
        vb.draw_line(corners[3], corners[7])

        vb.draw_line(corners[0], corners[2])
        vb.draw_line(corners[1], corners[3])
        vb.draw_line(corners[4], corners[6])
        vb.draw_line(corners[5], corners[7])

        vb.draw_line(corners[0], corners[1])
        vb.draw_line(corners[2], corners[3])
        vb.draw_line(corners[4], corners[5])
        vb.draw_line(corners[6], corners[7])

        vb.set_specular(True)


