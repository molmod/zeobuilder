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

from meta import NodeClass, Property
from reference import Reference

__all__ = ["ParentMixin", "ContainerMixin", "ReferentMixin"]


class ParentMixin(object):

    __metaclass__ = NodeClass

    #
    # Tree
    #

    def set_model(self, model):
        for child in self.children:
            child.set_model(model)

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

    def set_children(self, children):
        self.children = children

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
            model_object.set_model(self.model)

    def add_many(self, model_objects, index=-1):
        if index == -1: index = len(self.children)
        #print "ADD MANY TO " + self.name + ":", [model_object.name for model_object in model_objects], index
        for model_object in model_objects[::-1]:
            self.children.insert(index, model_object)
            model_object.parent = self
        if self.model is not None:
            for model_object in model_objects:
                model_object.set_model(self.model)

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

    #
    # State
    #

    def initnonstate(self):
        self.children = self.create_references()
        for child in self.children:
            child.parent = self
        if self.model is not None:
            for child in self.children:
                child.set_model(self.model)

    def create_references(self):
        raise NotImplementedError

    #
    # Properties
    #

    def default_targets(self):
        return [None for child in self.children]

    def get_targets(self):
        return [child.target for child in self.children]

    def set_targets(self, targets):
        if len(targets) != len(self.children):
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

    def get_targets(self):
        return [child.target for child in self.children]

    #
    # Flags
    #

    def get_fixed(self):
        return False
