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

from elementary import Read
from mixin import ambiguous
from zeobuilder.conversion import express_measure, express_data_size

from molmod import Rotation

import gtk, numpy

__all__ = [
    "Label", "Handedness", "BBox", "Distance", "VectorLength", "DataSize",
    "Mapping",
]


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
        return (
            isinstance(self.attribute, GLTransformationMixin) and
            isinstance(self.attribute.transformation, Rotation)
        )


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
        return numpy.sqrt(numpy.dot(d, d))

    def applicable_attribute(self):
        from zeobuilder.nodes.vector import Vector
        return isinstance(self.attribute, Vector)


class DataSize(Label):
    def convert_to_representation(self, value):
        return express_data_size(value)


class Mapping(Read):
    def create_widgets(self):
        Read.create_widgets(self)
        self.list_store = gtk.ListStore(str, str)
        self.tree_view = gtk.TreeView(self.list_store)

        renderer_text = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Key", renderer_text, text=0)
        #column.pack_start(renderer_text, expand=False)
        self.tree_view.append_column(column)

        renderer_text = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Value", renderer_text, text=1)
        #column.pack_start(renderer_text, expand=True)
        self.tree_view.append_column(column)

        self.data_widget = gtk.ScrolledWindow()
        self.data_widget.add(self.tree_view)
        self.data_widget.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.data_widget.set_size_request(-1, 100)
        self.data_widget.set_shadow_type(gtk.SHADOW_IN)

    def convert_to_representation(self, value):
        if value == ambiguous:
            return {}
        else:
            return value

    def write_to_widget(self, representation, original=False):
        for key, value in sorted(representation.iteritems()):
            value = str(value)[:100].replace("\n", " ")
            self.list_store.append((key,str(value)))


