# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 - 2008 Toon Verstraelen <Toon.Verstraelen@UGent.be>
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
# --


from zeobuilder import context
from zeobuilder.actions.composed import Immediate
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.nodes.model_object import ModelObjectInfo
from zeobuilder.nodes.reference import SpatialReference
from zeobuilder.nodes.elementary import GLReferentBase
from zeobuilder.nodes.color_mixin import ColorMixin
import zeobuilder.authors as authors
import zeobuilder.actions.primitive as primitive

import numpy

import math


class Tetraeder(GLReferentBase, ColorMixin):
    info = ModelObjectInfo("plugins/basic/tetra.svg")
    authors = [authors.toon_verstraelen]

    #
    # State
    #

    def initnonstate(self):
        GLReferentBase.initnonstate(self)
        self.set_children([
            SpatialReference(prefix="Corner1"),
            SpatialReference(prefix="Corner2"),
            SpatialReference(prefix="Corner3"),
            SpatialReference(prefix="Corner4"),
        ])

    #
    # Draw
    #

    def draw(self):
        GLReferentBase.draw(self)
        ColorMixin.draw(self)
        vb = context.application.vis_backend
        p0,p1,p2,p3 = [target.get_frame_relative_to(self.parent).t for target in self.get_targets()]

        def get_normal(a,b,c,d):
            result = numpy.cross(a-b,c-b)
            norm = numpy.linalg.norm(result)
            if norm < 1e-8:
                return numpy.zeros(3,float)
            else:
                result /= norm
            if numpy.dot(result,d-b) > 0:
                result *= -1
            return result

        vb.draw_triangles((
            get_normal(p0,p1,p2,p3),
            [p0,p1,p2],
        ), (
            get_normal(p1,p2,p3,p0),
            [p1,p2,p3],
        ), (
            get_normal(p2,p3,p0,p1),
            [p2,p3,p0],
        ), (
            get_normal(p3,p0,p1,p2),
            [p3,p0,p1],
        ))

    #
    # Revalidation
    #

    def revalidate_bounding_box(self):
        GLReferentBase.revalidate_bounding_box(self)
        for target in self.get_targets():
            self.bounding_box.extend_with_point(target.get_frame_relative_to(self.parent).t)

    #
    # Vector
    #


    def define_target(self, reference, new_target):
        GLReferentBase.define_target(self, reference, new_target)
        self.invalidate_boundingbox_list()
        self.invalidate_draw_list()

    def target_moved(self, reference, target):
        GLReferentBase.target_moved(self, reference, target)
        self.invalidate_boundingbox_list()
        self.invalidate_draw_list()



class AddTetraeder(Immediate):
    description = "Add tetraeder"
    menu_info = MenuInfo("default/_Object:tools/_Add:3d", "_Tetraeder", image_name="plugins/basic/tetra.svg", order=(0, 4, 1, 0, 0, 6))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        if len(cache.nodes) != 4: return False
        if len(cache.translations) != 4: return False
        if cache.common_parent is None: return False
        # C) passed all tests:
        return True

    def do(self):
        cache = context.application.cache
        nodes = cache.nodes
        primitive.Add(
            Tetraeder(targets=nodes),
            cache.common_parent,
            index=cache.highest_index + 1
        )


nodes = {
    "Tetraeder": Tetraeder
}

actions = {
    "AddTetraeder": AddTetraeder,
}




