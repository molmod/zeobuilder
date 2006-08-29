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


from parent_mixin import ContainerMixin
from glmixin import GLMixin


from OpenGL.GL import *


__all__ = ["GLContainerMixin"]


class GLContainerMixin(ContainerMixin):

    #
    # Tree
    #

    def request_gl(self):
        for child in self.children:
            child.request_gl()

    def drop_gl(self):
        for child in self.children:
            child.drop_gl()

    def add(self, model_object, index=-1):
        model_object.request_gl()
        ContainerMixin.add(self, model_object, index)
        self.invalidate_all_lists()

    def remove(self, model_object):
        ContainerMixin.remove(self, model_object)
        model_object.drop_gl()
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
        if self.selected:
            glCallList(self.boundingbox_list)

    def draw(self):
        for child in self.children:
            child.call_list()

    def write_pov(self, indenter):
        for child in self.children:
            if child.visible: child.write_pov(indenter)

    #
    # Revalidation
    #

    def revalidate_bounding_box(self):
        for child in self.children:
            if child.visible:
                child_bounding_box = child.get_bounding_box_in_parent_frame()
                if child_bounding_box.corners is not None:
                    self.bounding_box.extend_with_corners(child_bounding_box.corners)

    #
    # Geometrix
    #

    def shortest_vector(self, delta):
        return delta
