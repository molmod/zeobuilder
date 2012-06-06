# -*- coding: utf-8 -*-
# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 - 2012 Toon Verstraelen <Toon.Verstraelen@UGent.be>, Center
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
#--


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

    def set_model(self, model, parent, index):
        ModelObject.set_model(self, model, parent, index)
        ContainerMixin.set_model(self, model, parent, index)

    def unset_model(self):
        ContainerMixin.unset_model(self)
        ModelObject.unset_model(self)

    def delete_referents(self):
        ContainerMixin.delete_referents(self)
        ModelObject.delete_referents(self)


class ReferentBase(ModelObject, ReferentMixin):

    #
    # Tree
    #

    def set_model(self, model, parent, index):
        ModelObject.set_model(self, model, parent, index)
        ReferentMixin.set_model(self, model, parent, index)

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

    def set_model(self, model, parent, index):
        ModelObject.set_model(self, model, parent, index)
        GLContainerMixin.set_model(self, model, parent, index)

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

    def set_model(self, model, parent, index):
        ModelObject.set_model(self, model, parent, index)
        GLContainerMixin.set_model(self, model, parent, index)

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


