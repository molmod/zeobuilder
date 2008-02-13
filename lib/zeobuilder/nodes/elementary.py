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


class ReferentBase(ModelObject, ReferentMixin):

    #
    # state
    #

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

    #
    # Flags
    #

    def get_fixed(self):
        return ReferentMixin.get_fixed(self)


class GLGeometricBase(ModelObject, GLTransformationMixin):

    #
    # State
    #

    def initnonstate(self, Transformation):
        ModelObject.initnonstate(self)
        GLTransformationMixin.initnonstate(self, Transformation)


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

    def draw_selection(self):
        GLContainerMixin.draw_selection(self)

    def draw(self):
        GLContainerMixin.draw(self)
        GLMixin.draw(self)


    def write_pov(self, indenter):
        GLContainerMixin.write_pov(self, indenter)
        GLMixin.write_pov(self, indenter)


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

    def draw_selection(self):
        GLContainerMixin.draw_selection(self)

    def draw(self):
        GLContainerMixin.draw(self)
        GLTransformationMixin.draw(self)


    def write_pov(self, indenter):
        GLContainerMixin.write_pov(self, indenter)
        GLTransformationMixin.write_pov(self, indenter)


class GLReferentBase(ReferentBase, GLMixin):

    #
    # State
    #

    def initnonstate(self):
        ReferentBase.initnonstate(self)
        GLMixin.initnonstate(self)


class GLGeometricReferentBase(ReferentBase, GLTransformationMixin):

    #
    # State
    #

    def initnonstate(self, Transformation):
        ReferentBase.initnonstate(self)
        GLTransformationMixin.initnonstate(self, Transformation)




