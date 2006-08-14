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


__all__ = ["PrimitiveError", "Add", "SetAttribute", "Delete", "Move",
           "SetProperty", "Transform", "SetTarget"]


class PrimitiveError(Exception):
    pass


class Primitive(object):
    changes_selection = False # see actions.composed.Action.__init__

    def __init__(self, victim, done=False):
        #print "INIT", self
        self.victim = victim
        self.done = done
        if context.application.action_manager is not None:
            context.application.action_manager.append_primitive_to_current_action(self)
        elif not self.done:
            self.init()
            self.redo()

    def init(self):
        # put here the calls that might imply consequences that must be
        # executed before this primitive.
        pass

    def redo(self):
        #print "REDO", self
        assert not self.done, "Primitive action is already done. Can not do it twice"
        self.done = True

    def undo(self):
        #print "UNDO", self
        assert self.done, "Primitive action is not yet done. Can not undo it."
        self.done = False


class Add(Primitive):
    def __init__(self, victim, parent, index=-1, select=True):
        if not isinstance(parent, ContainerMixin):
            raise PrimitiveError, "ADD: Parent must be a %s. You gave %s." % (ContainerMixin, parent)
        if not parent.check_add(victim.__class__):
            raise PrimitiveError, "ADD: Can not add %s to %s." % (victim, parent)
        self.parent = parent
        self.index = index
        self.changes_selection = select
        Primitive.__init__(self, victim, False)

    def redo(self):
        Primitive.redo(self)
        self.parent.add(self.victim, self.index)
        if self.changes_selection:
            context.application.main.toggle_selection(self.victim, on=True)

    def undo(self):
        Primitive.undo(self)
        self.parent.remove(self.victim)


class SetAttribute(Primitive):
    def __init__(self, victim, attribute_name, value, done=False):
        self.attribute_name = attribute_name
        if done:
            self.new_value = None
            self.old_value = value
        else:
            self.new_value = value
            self.old_value = None
        Primitive.__init__(self, victim, done)

    def redo(self):
        Primitive.redo(self)
        if self.old_value is None:
            self.old_value = eval("self.victim.%s" % self.attribute_name)
        exec("self.victim.%s = self.new_value" % self.attribute_name)

    def undo(self):
        Primitive.undo(self)
        if self.new_value is None:
            self.new_value = eval("self.victim.%s" % self.attribute_name)
        exec("self.victim.%s = self.old_value" % self.attribute_name)


class Delete(Primitive):
    def __init__(self, victim):
        if victim.get_fixed():
            raise PrimitiveError, "DELETE: The victim is fixed."
        self.old_parent = None
        self.old_index = None
        Primitive.__init__(self, victim, False)

    def init(self):
        self.victim.delete_referents()

    def redo(self):
        Primitive.redo(self)
        if self.old_index is None:
            self.old_parent = self.victim.parent
            self.old_index = self.victim.get_index()
        self.old_parent.remove(self.victim)

    def undo(self):
        Primitive.undo(self)
        self.old_parent.add(self.victim, self.old_index)


class Move(Primitive):
    def __init__(self, victim, new_parent, new_index=-1, select=True):
        if victim.get_fixed():
            raise PrimitiveError, "MOVE: The victim is fixed."
        if not isinstance(new_parent, ContainerMixin):
            raise PrimitiveError, "MOVE: New parent must be a %s. You gave %s." % (ContainerMixin, new_parent)
        if not new_parent.check_add(victim.__class__):
            raise PrimitiveError, "MOVE: Can not move %s to %s." % (victim, new_parent)
        self.new_parent = new_parent
        self.new_index = new_index
        self.old_parent = None
        self.old_index = None
        self.changes_selection = select
        Primitive.__init__(self, victim, False)

    def redo(self):
        Primitive.redo(self)
        if self.old_index is None:
            self.old_parent = self.victim.parent
            self.old_index = self.victim.get_index()
        self.victim.move(self.new_parent, self.new_index)
        if self.changes_selection:
            context.application.main.toggle_selection(self.victim, on=True)

    def undo(self):
        Primitive.undo(self)
        self.victim.move(self.old_parent, self.old_index)
        if self.changes_selection:
            context.application.main.toggle_selection(self.victim, on=True)


class SetProperty(Primitive):
    def __init__(self, victim, name, value, done=False):
        # When using done=True, only call this primitive after the changes
        # to the properties were made and pass a deep copy of the old value
        self.name = name
        self.property = victim.properties_by_name[name]
        if done:
            self.new_value = self.property.get(victim)
            self.old_value = value
            # a trick to let the victim know a property has changed
            #self.property.set(victim, self.new_value)
        else:
            self.new_value = value
            self.old_value = None
        Primitive.__init__(self, victim, done)

    def redo(self):
        Primitive.redo(self)
        if self.old_value is None:
            self.old_value = self.property.get(self.victim)
        self.property.set(self.victim, self.new_value)

    def undo(self):
        Primitive.undo(self)
        self.property.set(self.victim, self.old_value)


class Transform(Primitive):
    def __init__(self, victim, transformation, done=False, after=True):
        if not isinstance(victim, GLTransformationMixin):
            raise PrimitiveError, "TRANSFORM: Object must be a %s. You gave %s." % (GLTransformationMixin, victim)
        if victim.get_fixed():
            raise PrimitiveError, "TRANSFORM: Object %s is fixed." % victim
        self.transformation = transformation
        self.after = after
        if done:
            self.victim.invalidate_transformation_list()
        Primitive.__init__(self, victim, done)

    def redo(self):
        Primitive.redo(self)
        if self.after:
            self.victim.transformation.apply_after(self.transformation)
        else:
            self.victim.transformation.apply_before(self.transformation)
        self.victim.invalidate_transformation_list()

    def undo(self):
        Primitive.undo(self)
        if self.after:
            self.victim.transformation.apply_inverse_after(self.transformation)
        else:
            self.victim.transformation.apply_inverse_before(self.transformation)
        self.victim.invalidate_transformation_list()


class SetTarget(Primitive):
    def __init__(self, victim, target):
        if not isinstance(victim, Reference):
            raise PrimitiveError, "TARGET: Reference must be a %s. You gave %s." % (Reference, victim)
        if not victim.check_target(target):
            raise PrimitiveError, "TARGET: A %s can not refere to to a %s." % (victim, target)
        self.victim = victim
        self.new_target = target
        self.old_target = 0
        Primitive.__init__(self, victim, False)

    def redo(self):
        Primitive.redo(self)
        if self.old_target == 0:
            self.old_target = self.victim.target
        self.victim.set_target(self.new_target)

    def undo(self):
        Primitive.undo(self)
        self.victim.set_target(self.old_target)

