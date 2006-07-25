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

from zeobuilder import context
from zeobuilder.nodes.parent_mixin import ContainerMixin
from zeobuilder.nodes.glmixin import GLTransformationMixin
from zeobuilder.nodes.reference import Reference

__all__ = ["Base", "PrimitiveError", "Add", "SetAttribute", "Delete", "Move",
           "SetPublishedProperty", "Transform"]


class PrimitiveError(Exception):
    pass


class Base(object):
    def __init__(self, victim, done=False):
        self.victim = victim
        self.done = done
        if context.application.action_manager != None:
            context.application.action_manager.append_primitive_to_current_action(self)
        elif not self.done:
            self.init()
            self.redo()

    def init(self):
        # put here the calls that might imply consequences that must be
        # executed before this primitive.
        pass

    def redo(self):
        assert not self.done, "Primitive action is already done. Can not do it twice"
        self.done = True

    def undo(self):
        assert self.done, "Primitive action is not yet done. Can not undo it."
        self.done = False


class Add(Base):
    def __init__(self, victim, parent, index=-1):
        if not isinstance(parent, ContainerMixin):
            raise PrimitiveError, "ADD: Parent must be a %s." % (ContainerMixin)
        if not parent.check_add(victim.__class__):
            raise PrimitiveError, "ADD: Can not add a %s to a %s." % (victim.__class__, parent.__class__)
        self.parent = parent
        self.index = index
        Base.__init__(self, victim, False)

    def redo(self):
        Base.redo(self)
        self.parent.add(self.victim, self.index)

    def undo(self):
        Base.undo(self)
        self.parent.remove(self.victim)


class SetAttribute(Base):
    def __init__(self, victim, attribute_name, value, done=False):
        self.attribute_name = attribute_name
        if done:
            self.new_value = None
            self.old_value = value
        else:
            self.new_value = value
            self.old_value = None
        Base.__init__(self, victim, done)

    def redo(self):
        Base.redo(self)
        if self.old_value == None:
            self.old_value = eval("self.victim.%s" % self.attribute_name)
        exec("self.victim.%s = self.new_value" % self.attribute_name)

    def undo(self):
        Base.undo(self)
        if self.new_value == None:
            self.new_value = eval("self.victim.%s" % self.attribute_name)
        exec("self.victim.%s = self.old_value" % self.attribute_name)


class Delete(Base):
    def __init__(self, victim):
        if victim.get_fixed():
            raise PrimitiveError, "DELETE: The victim is fixed."
        self.old_parent = None
        self.old_index = None
        Base.__init__(self, victim, False)

    def init(self):
        self.victim.delete_referents()

    def redo(self):
        Base.redo(self)
        if self.old_index == None:
            self.old_parent = self.victim.parent
            self.old_index = self.victim.get_index()
        self.old_parent.remove(self.victim)

    def undo(self):
        Base.undo(self)
        self.old_parent.add(self.victim, self.old_index)


class Move(Base):
    def __init__(self, victim, new_parent, new_index=-1):
        if victim.get_fixed():
            raise PrimitiveError, "MOVE: The victim is fixed."
        if not isinstance(new_parent, ContainerMixin):
            raise PrimitiveError, "MOVE: New parent must be a %s." % (ContainerMixin)
        if not new_parent.check_add(victim.__class__):
            raise PrimitiveError, "MOVE: Can not move a %s to a %s." % (victim.__class__, new_parent.__class__)
        self.new_parent = new_parent
        self.new_index = new_index
        self.old_parent = None
        self.old_index = None
        Base.__init__(self, victim, False)

    def redo(self):
        Base.redo(self)
        if self.old_index == None:
            self.old_parent = self.victim.parent
            self.old_index = self.victim.get_index()
        self.victim.move(self.new_parent, self.new_index)

    def undo(self):
        Base.undo(self)
        self.victim.move(self.old_parent, self.old_index)


class SetPublishedProperty(Base):
    def __init__(self, victim, name, value, done=False):
        # When using done=True, only call this primitive after the changes
        # to the published properties were made and pass a deep copy
        # of the old value
        self.name = name
        self.published_property = victim.published_properties[name]
        if done:
            self.new_value = self.published_property.get(victim)
            self.old_value = value
            # a trick to let the victim know a property has changed
            self.published_property.set(victim, self.new_value)
        else:
            self.new_value = value
            self.old_value = None
        Base.__init__(self, victim, done)

    def redo(self):
        Base.redo(self)
        if self.old_value == None:
            self.old_value = self.published_property.get(self.victim)
        self.published_property.set(self.victim, self.new_value)

    def undo(self):
        Base.undo(self)
        self.published_property.set(self.victim, self.old_value)


class Transform(Base):
    def __init__(self, victim, transformation, done=False, after=True):
        if not isinstance(victim, GLTransformationMixin):
            raise PrimitiveError, "TRANSFORM: Object is not a transformed model object."
        if victim.get_fixed():
            raise PrimitiveError, "TRANSFORM: Object is fixed."
        self.transformation = transformation
        self.after = after
        if done:
            self.victim.invalidate_transformation_list()
        Base.__init__(self, victim, done)

    def redo(self):
        Base.redo(self)
        if self.after:
            self.victim.transformation.apply_after(self.transformation)
        else:
            self.victim.transformation.apply_before(self.transformation)
        self.victim.invalidate_transformation_list()

    def undo(self):
        Base.undo(self)
        if self.after:
            self.victim.transformation.apply_inverse_after(self.transformation)
        else:
            self.victim.transformation.apply_inverse_before(self.transformation)
        self.victim.invalidate_transformation_list()


class SetTarget(Base):
    def __init__(self, victim, target):
        if not isinstance(victim, Reference):
            raise PrimitiveError, "TARGET: Reference must be a %s." % (Reference)
        if not victim.check_target(target):
            raise PrimitiveError, "TARGET: A %s can not refere to to a %s." % (victim, target)
        self.victim = victim
        self.new_target = target
        self.old_target = 0
        Base.__init__(self, victim, False)

    def redo(self):
        Base.redo(self)
        if self.old_target == 0:
            self.old_target = self.victim.target
        self.victim.set_target(self.new_target)

    def undo(self):
        Base.undo(self)
        self.victim.set_target(self.old_target)

