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

    def set_radius(self, radius):
        self.radius = radius
        self.invalidate_draw_list()
        self.invalidate_boundingbox_list()

    def set_quality(self, quality):
        self.quality = quality
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


