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
from zeobuilder.actions.abstract import AddBase
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.nodes.meta import PublishedProperties, Property
from zeobuilder.nodes.elementary import GLGeometricBase
from zeobuilder.nodes.color_mixin import UserColorMixin
from zeobuilder.nodes.model_object import ModelObjectInfo
from zeobuilder.gui.fields_dialogs import DialogFieldInfo
from zeobuilder.transformations import Translation
import zeobuilder.gui.fields as fields

from molmod.data import periodic

from OpenGL.GL import *
from OpenGL.GLUT import *
import numpy


class Atom(GLGeometricBase, UserColorMixin):
    info = ModelObjectInfo("plugins/molecular/atom.svg")

    #
    # State
    #

    def initnonstate(self):
        GLGeometricBase.initnonstate(self, Translation)

    #
    # Properties
    #

    def set_user_radius(self, user_radius):
        self.user_radius = user_radius
        self.invalidate_draw_list()
        self.invalidate_boundingbox_list()

    def set_quality(self, quality):
        self.quality = quality
        self.invalidate_draw_list()

    def set_number(self, number):
        self.number = number
        atom_info = periodic[number]
        self.default_radius = atom_info.radius
        color = [atom_info.red, atom_info.green, atom_info.blue, 1.0]
        if None in color:
            self.default_color = numpy.array([0.7, 0.7, 0.7, 1.0], float)
        else:
            self.default_color = numpy.array(color, float)
        self.invalidate_draw_list()
        self.invalidate_boundingbox_list()

    published_properties = PublishedProperties({
        "user_radius": Property(None, lambda self: self.user_radius, set_user_radius, signal=True),
        "quality": Property(50, lambda self: self.quality, set_quality),
        "number": Property(6, lambda self: self.number, set_number, signal=True),
    })

    #
    # Dialog fields (see action EditProperties)
    #

    dialog_fields = set([
        DialogFieldInfo("Geometry", (2, 9), fields.elementary.Checkable(
            fields.faulty.Length(
                label_text="User defined radius",
                attribute_name="user_radius",
                low=0.0,
                low_inclusive=False,
            )
        )),
        DialogFieldInfo("Markup", (1, 3), fields.faulty.Int(
            label_text="Quality",
            attribute_name="quality",
            minimum=3,
        )),
        DialogFieldInfo("Molecular", (6, 0), fields.edit.Element(
            attribute_name="number",
            show_popup=False,
        )),
    ])

    #
    # Draw
    #

    def get_radius(self):
        if self.user_radius is not None:
            return self.user_radius
        else:
            return self.default_radius

    def draw(self):
        GLGeometricBase.draw(self)
        UserColorMixin.draw(self)
        glutSolidSphere(self.get_radius(), self.quality, self.quality / 2)

    def write_pov(self, indenter):
        indenter.write_line("sphere {", 1)
        indenter.write_line("<0.0, 0.0, 0.0>, %f" % (self.get_radius()))
        indenter.write_line("pigment { rgb <%f, %f, %f> }" % tuple(self.get_color()[0:3]))
        GLGeometricBase.write_pov(self, indenter)
        indenter.write_line("}", -1)

    #
    # Revalidation
    #

    def revalidate_bounding_box(self):
        GLGeometricBase.revalidate_bounding_box(self)
        self.bounding_box.extend_with_corners([-self.get_radius()*numpy.ones(3, float), self.get_radius()*numpy.ones(3, float)])


class AddAtom(AddBase):
    description = "Add atom"
    menu_info = MenuInfo("default/_Object:tools/_Add:3d", "_Atom", image_name="plugins/molecular/atom.svg", order=(0, 4, 1, 0, 0, 4))

    def analyze_selection():
        return AddBase.analyze_selection(Atom)
    analyze_selection = staticmethod(analyze_selection)

    def do(self):
        AddBase.do(self, Atom)


nodes = {
    "Atom": Atom
}

actions = {
    "AddAtom": AddAtom,
}
