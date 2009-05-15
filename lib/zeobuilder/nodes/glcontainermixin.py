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


from parent_mixin import ContainerMixin
from glmixin import GLMixin

from zeobuilder import context


__all__ = ["GLContainerMixin"]


class GLContainerMixin(ContainerMixin):

    #
    # Tree
    #

    def add(self, model_object, index=-1):
        ContainerMixin.add(self, model_object, index)
        self.invalidate_all_lists()

    def add_many(self, model_objects, index=-1):
        ContainerMixin.add_many(self, model_objects, index)
        self.invalidate_all_lists()

    def remove(self, model_object):
        ContainerMixin.remove(self, model_object)
        self.invalidate_all_lists()

    @classmethod
    def check_add(Class, ModelObjectClass):
        if not ContainerMixin.check_add(ModelObjectClass): return False
        if not issubclass(ModelObjectClass, GLMixin): return False
        return True

    #
    # Draw
    #

    def draw_selection(self):
        vb = context.application.vis_backend
        vb.set_bright(True)
        if self.selected:
            vb.call_list(self.boundingbox_list)
        vb.set_bright(False)

    def draw(self):
        for child in self.children:
            child.call_list()


    #
    # Revalidation
    #

    def revalidate_bounding_box(self):
        for child in self.children:
            child_bounding_box = child.get_bounding_box_in_parent_frame()
            if child_bounding_box.corners is not None:
                self.bounding_box.extend_with_corners(child_bounding_box.corners)

    #
    # Geometrix
    #

    def shortest_vector(self, delta):
        return delta


