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

from elementary import Read
from mixin import ambiguous, insensitive
from zeobuilder.conversion import express_measure, express_data_size

from molmod.transformations import Rotation

import math, gtk, numpy

__all__ = ["Label", "Handedness", "BBox", "Distance", "VectorLength",
           "DataSize"]


class Label(Read):
    def create_widgets(self):
        Read.create_widgets(self)
        self.data_widget = gtk.Label()
        self.data_widget.set_selectable(True)
        self.data_widget.set_alignment(0.0, 0.5)
        self.data_widget.set_use_markup(True)

    def convert_to_representation(self, value):
        if value == ambiguous:
            return ""
        else:
            return str(value)

    def write_to_widget(self, representation, original=False):
        if representation == insensitive:
            self.data_widget.set_sensitive(False)
        else:
            self.data_widget.set_sensitive(True)
            if representation == ambiguous:
                self.data_widget.set_label("<span foreground=\"gray\">%s</span>" % ambiguous)
            else:
                self.data_widget.set_label(representation)


class Handedness(Label):
    def read_from_attribute(self):
        return (numpy.linalg.det(self.attribute.get_absolute_frame().r) > 0)

    def convert_to_representation(self, value):
        if value == ambiguous:
            return ambiguous
        elif value:
            return "The selected frames are right-handed."
        else:
            return "The selected frames are left-handed."

    def applicable_attribute(self):
        from zeobuilder.nodes.glmixin import GLTransformationMixin
        return isinstance(self.attribute, GLTransformationMixin) and \
               isinstance(self.attribute.transformation, Rotation)


class BBox(Label):
    def convert_to_representation(self, value):
        if value.corners is None:
            return "<span foreground=\"red\">NO BBOX INFO FOUND. THIS SHOULD NEVER HAPPEN.</span>"
        else:
            return (
                express_measure(value.corners[1][0] - value.corners[0][0], "Length"),
                express_measure(value.corners[1][1] - value.corners[0][1], "Length"),
                express_measure(value.corners[1][2] - value.corners[0][2], "Length")
            )

    def write_to_widget(self, representation, original=False):
        if isinstance(representation, tuple):
            Label.write_to_widget(self, "<span foreground=\"gray\">(</span> %s <span foreground=\"gray\">,</span> %s <span foreground=\"gray\">,</span> %s <span foreground=\"gray\">)</span>" % representation, original)
        else:
            Label.write_to_widget(self, representation, original)

    def applicable_attribute(self):
        from zeobuilder.nodes.helpers import BoundingBox
        return isinstance(self.attribute, BoundingBox)


class Distance(Label):
    def convert_to_representation(self, value):
        return express_measure(value, "Length")


class VectorLength(Distance):
    def read_from_instance(self, instance):
        attribute = Distance.read_from_instance(self, instance)
        d = attribute.shortest_vector_relative_to(attribute.parent)
        return math.sqrt(numpy.dot(d, d))

    def applicable_attribute(self):
        from zeobuilder.nodes.vector import Vector
        return isinstance(self.attribute, Vector)


class DataSize(Label):
    def convert_to_representation(self, value):
        return express_data_size(value)

