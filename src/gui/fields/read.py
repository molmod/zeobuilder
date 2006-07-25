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
from mixin import ambiguous
from zeobuilder.conversion import express_measure, express_data_size
from molmod.units import LENGTH

import math, gtk, numpy

__all__ = ["Label", "Handedness", "BBox", "Distance", "VectorLength",
           "DataSize"]


class Label(Read):
    self_containing = False

    def create_widgets(self):
        Read.create_widgets(self)
        self.container = gtk.Label()
        self.container.set_alignment(0.0, 0.5)
        self.container.set_use_markup(True)

    def convert_to_representation(self, value):
        if value == ambiguous:
            return ""
        else:
            return str(value)

    def write_to_widget(self, representation, original=False):
        if representation == ambiguous:
            self.container.set_label("<span foreground=\"gray\">%s</span>" % ambiguous)
        else:
            self.container.set_label(representation)


class Handedness(Label):
    mutable_attribute = True

    def read_from_attribute(self, attribute):
        return (numpy.linalg.det(attribute.get_absolute_frame().rotation_matrix) > 0)

    def convert_to_representation(self, value):
        if value == ambiguous:
            return ambiguous
        elif value:
            return "The selected frames are right-handed."
        else:
            return "The selected frames are left-handed."

    def applicable_attribute(self, attribute):
        from zeobuilder.transformations import Rotation
        from zeobuilder.nodes.glmixin import GLTransformationMixin
        return isinstance(attribute, GLTransformationMixin) and \
               isinstance(attribute.transformation, Rotation)


class BBox(Label):
    mutable_attribute = True

    def convert_to_representation(self, value):
        return (express_measure(value.corners[1][0] - value.corners[0][0], LENGTH),
                express_measure(value.corners[1][1] - value.corners[0][1], LENGTH),
                express_measure(value.corners[1][2] - value.corners[0][2], LENGTH))

    def write_to_widget(self, representation, original=False):
        if representation == ambiguous:
            Label.write_to_widget(self, ambiguous, original)
        else:
            Label.write_to_widget(self, "<span foreground=\"gray\">(</span> %s <span foreground=\"gray\">,</span> %s <span foreground=\"gray\">,</span> %s <span foreground=\"gray\">)</span>" % representation, original)

    def applicable_attribute(self, attribute):
        from zeobuilder.nodes.helpers import BoundingBox
        return isinstance(attribute, BoundingBox)


class Distance(Label):
    def convert_to_representation(self, value):
        return express_measure(value, LENGTH)


class VectorLength(Distance):
    mutable_attribute = True

    def read_from_instance(self, instance):
        attribute = Distance.read_from_instance(self, instance)
        d = attribute.shortest_vector_relative_to(attribute.parent)
        return math.sqrt(numpy.dot(d, d))

    def applicable_attribute(self, attribute):
        from zeobuilder.nodes.vector import Vector
        return isinstance(attribute, Vector)


class DataSize(Label):
    def convert_to_representation(self, value):
        return express_data_size(value)

