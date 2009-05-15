# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 - 2009 Toon Verstraelen <Toon.Verstraelen@UGent.be>, Center
# for Molecular Modeling (CMM), Ghent University, Ghent, Belgium; all rights
# reserved unless otherwise stated.
#
# This file is part of Zeobuilder.
#
# Zeobuilder is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# In addition to the regulations of the GNU General Public License,
# publications and communications based in parts on this program or on
# parts of this program are required to cite the following article:
#
# "ZEOBUILDER: a GUI toolkit for the construction of complex molecules on the
# nanoscale with building blocks", Toon Verstraelen, Veronique Van Speybroeck
# and Michel Waroquier, Journal of Chemical Information and Modeling, Vol. 48
# (7), 1530-1541, 2008
# DOI:10.1021/ci8000748
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
from zeobuilder.nodes.elementary import GLGeometricBase
from zeobuilder.nodes.model_object import ModelObjectInfo
from zeobuilder.nodes.color_mixin import ColorMixin
from zeobuilder.gui.fields_dialogs import DialogFieldInfo
import zeobuilder.gui.fields as fields
import zeobuilder.authors as authors

from molmod.transformations import Translation

import numpy


class Sphere(GLGeometricBase, ColorMixin):
    info = ModelObjectInfo("plugins/basic/sphere.svg")
    authors = [authors.toon_verstraelen]

    def initnonstate(self):
        GLGeometricBase.initnonstate(self, Translation)

    #
    # Properties
    #

    def set_radius(self, radius, init=False):
        self.radius = radius
        if not init:
            self.invalidate_draw_list()
            self.invalidate_boundingbox_list()

    def set_quality(self, quality, init=False):
        self.quality = quality
        if not init:
            self.invalidate_draw_list()

    properties = [
        Property("radius", 0.5, lambda self: self.radius, set_radius),
        Property("quality", 15, lambda self: self.quality, set_quality),
    ]

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
        ))
    ])

    #
    # Draw
    #

    def draw(self):
        GLGeometricBase.draw(self)
        ColorMixin.draw(self)
        vb = context.application.vis_backend
        vb.draw_sphere(self.radius, self.quality)

    #
    # Revalidation
    #

    def revalidate_bounding_box(self):
        GLGeometricBase.revalidate_bounding_box(self)
        self.bounding_box.extend_with_corners([-self.radius*numpy.ones(3, float), self.radius*numpy.ones(3, float)])


class AddSphere(AddBase):
    description = "Add sphere"
    menu_info = MenuInfo("default/_Object:tools/_Add:3d", "_Sphere", image_name="plugins/basic/sphere.svg", order=(0, 4, 1, 0, 0, 1))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        return AddBase.analyze_selection(Sphere)

    def do(self):
        AddBase.do(self, Sphere)


nodes = {
    "Sphere": Sphere
}

actions = {
    "AddSphere": AddSphere,
}


