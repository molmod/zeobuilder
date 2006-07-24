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


from zeobuilder.nodes.model_object import ModelObject
from zeobuilder.nodes.parent_mixin import ContainerMixin, ReferentMixin
from zeobuilder.nodes.glmixin import GLMixin, GLTransformationMixin
from zeobuilder.nodes.glcontainermixin import GLContainerMixin


__all__ = ["ContainerBase", "ReferentBase", "GLGeometricBase",
           "GLContainerBase", "GLFrameBase", "GLReferentBase",
           "GLGeometricReferentBase"]


class ContainerBase(ModelObject, ContainerMixin):

    #
    # Tree
    #

    def set_model(self, model):
        ModelObject.set_model(self, model)
        ContainerMixin.set_model(self, model)

    def unset_model(self):
        ContainerMixin.unset_model(self)
        ModelObject.unset_model(self)

    def delete_referents(self):
        ContainerMixin.delete_referents(self)
        ModelObject.delete_referents(self)

    def set_expanded(self, expanded):
        ContainerMixin.set_expanded(self, expanded)


class ReferentBase(ModelObject, ReferentMixin):

    #
    # state
    #

    def initstate(self, **initstate):
        ModelObject.initstate(self, **initstate)
        ReferentMixin.initstate(self, **initstate)

    def initnonstate(self):
        ReferentMixin.initnonstate(self)
        ModelObject.initnonstate(self)

    #
    # Tree
    #

    def set_model(self, model):
        ModelObject.set_model(self, model)
        ReferentMixin.set_model(self, model)

    def unset_model(self):
        ReferentMixin.unset_model(self)
        ModelObject.unset_model(self)

    def set_expanded(self, expanded):
        ReferentMixin.set_expanded(self, expanded)

    #
    # Flags
    #

    def get_fixed(self):
        return ReferentMixin.get_fixed(self)

    def set_expanded(self, expanded):
        ReferentMixin.set_expanded(self, expanded)


class GLGeometricBase(ModelObject, GLTransformationMixin):

    #
    # State
    #

    def initnonstate(self, Transformation):
        ModelObject.initnonstate(self)
        GLTransformationMixin.initnonstate(self, Transformation)

    #
    # Flags
    #

    def set_selected(self, selected):
        GLTransformationMixin.set_selected(self, selected)


class GLContainerBase(ModelObject, GLMixin, GLContainerMixin):

    #
    # State
    #

    def initnonstate(self):
        ModelObject.initnonstate(self)
        GLMixin.initnonstate(self)

    #
    # Tree
    #

    def set_model(self, model):
        ModelObject.set_model(self, model)
        GLContainerMixin.set_model(self, model)

    def unset_model(self):
        GLContainerMixin.unset_model(self)
        ModelObject.unset_model(self)

    def request_gl(self):
        GLMixin.request_gl(self)
        GLContainerMixin.request_gl(self)

    def drop_gl(self):
        GLContainerMixin.drop_gl(self)
        GLMixin.drop_gl(self)

    def delete_referents(self):
        GLContainerMixin.delete_referents(self)
        ModelObject.delete_referents(self)


    #
    # Revalidation
    #

    def revalidate_bounding_box(self):
        GLMixin.revalidate_bounding_box(self)
        GLContainerMixin.revalidate_bounding_box(self)

    #
    # Draw
    #

    def draw(self):
        GLContainerMixin.draw(self)
        GLMixin.draw(self)


    def write_pov(self, indenter):
        GLContainerMixin.write_pov(self, indenter)
        GLMixin.write_pov(self, indenter)

    #
    # Flags
    #

    def set_selected(self, selected):
        GLMixin.set_selected(self, selected)

    def set_expanded(self, expanded):
        GLContainerMixin.set_expanded(self, expanded)


class GLFrameBase(ModelObject, GLTransformationMixin, GLContainerMixin):

    #
    # State
    #

    def initnonstate(self, Transformation):
        ModelObject.initnonstate(self)
        GLTransformationMixin.initnonstate(self, Transformation)

    #
    # Tree
    #

    def set_model(self, model):
        ModelObject.set_model(self, model)
        GLContainerMixin.set_model(self, model)

    def unset_model(self):
        GLContainerMixin.unset_model(self)
        ModelObject.unset_model(self)

    def request_gl(self):
        GLTransformationMixin.request_gl(self)
        GLContainerMixin.request_gl(self)

    def drop_gl(self):
        GLTransformationMixin.drop_gl(self)
        GLContainerMixin.drop_gl(self)

    def delete_referents(self):
        GLContainerMixin.delete_referents(self)
        ModelObject.delete_referents(self)

    #
    # Revalidation
    #

    def revalidate_bounding_box(self):
        GLTransformationMixin.revalidate_bounding_box(self)
        GLContainerMixin.revalidate_bounding_box(self)

    #
    # Draw
    #

    def draw(self):
        GLContainerMixin.draw(self)
        GLTransformationMixin.draw(self)


    def write_pov(self, indenter):
        GLContainerMixin.write_pov(self, indenter)
        GLTransformationMixin.write_pov(self, indenter)

    #
    # Flags
    #

    def set_selected(self, selected):
        GLTransformationMixin.set_selected(self, selected)

    def set_expanded(self, expanded):
        GLContainerMixin.set_expanded(self, expanded)


class GLReferentBase(ReferentBase, GLMixin):

    #
    # State
    #

    def initnonstate(self):
        ReferentBase.initnonstate(self)
        GLMixin.initnonstate(self)

    #
    # Flags
    #

    def set_selected(self, selected):
        GLMixin.set_selected(self, selected)


class GLGeometricReferentBase(ReferentBase, GLTransformationMixin):

    #
    # State
    #

    def initnonstate(self, Transformation):
        ReferentBase.initnonstate(self)
        GLTransformationMixin.initnonstate(self, Transformation)

    #
    # Flags
    #

    def set_selected(self, selected):
        GLTransformationMixin.set_selected(self, selected)

