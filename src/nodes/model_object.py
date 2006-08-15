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

from zeobuilder.nodes.node import Node, NodeInfo
from zeobuilder.nodes.meta import Property
from zeobuilder.gui.fields_dialogs import DialogFieldInfo
import zeobuilder.gui.fields as fields
import zeobuilder.actions.primitive as primitive

import gobject

import copy


__all__ = ["ModelObject", "ModelObjectInfo"]


class ModelObjectInfo(NodeInfo):
    def __init__(self, icon_name=None, default_action_name=None):
        NodeInfo.__init__(self, default_action_name)
        if icon_name is not None:
            self.icon_name = icon_name


class ModelObject(Node):
    info = ModelObjectInfo(default_action_name="EditProperties")

    #
    # State
    #

    def __init__(self, **initstate):
        # some debugging code
        #Node.count += 1
        #print " PLUS => Initializing " + str(self.__class__) + " (" + str(Node.count) + ") " + hex(id(self))
        Node.__init__(self)
        # initialisation of non state variables
        self.initnonstate()
        # further initialize the state (the properties)
        self.initstate(**initstate)

    def __del__(self):
        pass
        # some debugging code
        #Node.count -= 1
        #print " MIN  => Deleting     " + str(self.__class__) + " (" + str(Node.count) + ") " + hex(id(self))

    def __getstate__(self):
        return dict((p.name, p.get(self)) for p in self.properties)

    def initstate(self, **initstate):
        for p in self.properties:
            if p.name not in self.__dict__:
                self.__dict__[p.name] = p.default(self)
        for p in self.properties:
            value = initstate.get(p.name)
            if value is None:
                value = p.default(self)
            p.set(self, value)

    def initnonstate(self):
        self.references = []

    #
    # Properties
    #

    @classmethod
    def class_name(cls):
        temp = str(cls)
        return temp[temp.rfind(".")+1:-2]

    def default_name(self):
        return self.class_name()

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    properties = [
        Property("name", default_name, get_name, set_name)
    ]

    #
    # Dialog fields (see action EditProperties)
    #

    dialog_fields = set([
        DialogFieldInfo("Basic", (0, 0), fields.faulty.Name(
            label_text="Name",
            attribute_name="name",
        )),
    ])

    #
    # Tree
    #

    def delete_referents(self):
        for reference in copy.copy(self.references):
            if reference.model is not None:
                #print "Deleting Referent %s(%i)" % (reference.parent.get_name(), id(reference.parent))
                primitive.Delete(reference.parent)

    def move(self, new_parent, index=-1):
        if (index > 0) and (self.parent == new_parent) and index > self.get_index():
            index -= 1
        self.parent.remove(self)
        new_parent.add(self, index)
        self.emit("on-move")
        #print "EMIT: on-move"

    #
    # Flags
    #

    def get_fixed(self):
        return (self.model is not None) and (self.parent is None)


gobject.signal_new("on-move", ModelObject, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())

