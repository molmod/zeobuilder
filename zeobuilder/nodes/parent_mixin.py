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
# --

from meta import NodeClass, Property
from reference import Reference

__all__ = ["ParentMixin", "ContainerMixin", "ReferentMixin"]


class ParentMixin(object):

    __metaclass__ = NodeClass

    #
    # Tree
    #

    def set_model(self, model, parent, index):
        for i, child in enumerate(self.children):
            child.set_model(model, self, i)

    def unset_model(self):
        for child in self.children:
            child.unset_model()

    def unparent(self):
        for child in self.children:
            child.parent = None
            if isinstance(child, ParentMixin):
                child.unparent()

    def reparent(self):
        for child in self.children:
            child.parent = self
            if isinstance(child, ParentMixin):
                child.reparent()


class ContainerMixin(ParentMixin):

    #
    # Properties
    #

    def set_children(self, children, init=False):
        self.children = children
        if not init:
            for child in self.children:
                child.parent = self
            if self.model is not None:
                for i, child in enumerate(self.children):
                    child.set_model(self.model, self, i)

    properties = [
        Property("children", [], lambda self: self.children, set_children),
    ]

    #
    # Tree
    #

    def add(self, model_object, index=-1):
        if index == -1: index = len(self.children)
        #print "ADD TO " + self.name + ":", model_object.name, index
        self.children.insert(index, model_object)
        model_object.parent = self
        if self.model is not None:
            model_object.set_model(self.model, self, index)

    def add_many(self, model_objects, index=-1):
        if index == -1: index = len(self.children)
        #print "ADD MANY TO " + self.name + ":", [model_object.name for model_object in model_objects], index
        for model_object in model_objects[::-1]:
            self.children.insert(index, model_object)
            model_object.parent = self
            if self.model is not None:
                model_object.set_model(self.model, self, index)

    def remove(self, model_object):
        #print "REMOVE FROM " + self.name + ":", model_object.name
        if self.model is not None:
            model_object.unset_model()
        model_object.parent = None
        self.children.remove(model_object)

    def delete_referents(self):
        for child in self.children:
            child.delete_referents()

    @classmethod
    def check_add(Class, ModelObjectClass):
        if issubclass(ModelObjectClass, Reference):
            return False
        else:
            return True


class ReferentMixinError(Exception):
    pass


class ReferentMixin(ParentMixin):

    def set_children(self, children):
        self.children = children
        for child in self.children:
            child.parent = self
        if self.model is not None:
            for i, child in enumerate(self.children):
                child.set_model(self.model, self, i)

    #
    # Properties
    #

    def default_targets(self):
        return []

    def get_targets(self):
        return [child.target for child in self.children]

    def set_targets(self, targets, init=False):
        #print self
        #print targets
        #print self.children
        if len(targets) != len(self.children):
            if init and len(targets) == 0:
                for child in self.children:
                    child.set_target(None)
            else:
                raise ReferentMixinError("The number of targets should match the number of references.")
        for child, target in zip(self.children, targets):
            child.set_target(target)

    properties = [
        Property("targets", default_targets, get_targets, set_targets),
    ]

    #
    # References
    #

    def define_target(self, reference, new_target):
        pass

    def undefine_target(self, reference, old_target):
        pass

    def check_target(self, reference, target):
        return True

    def target_moved(self, reference, target):
        pass

    #
    # Flags
    #

    def get_fixed(self):
        return False


