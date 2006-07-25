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


from zeobuilder.nodes.meta import NodeClass, PublishedProperties, Property
import zeobuilder.gui.fields as fields

import gtk.gdk, gobject

import copy


__all__ = ["Base"]


class Base(gobject.GObject):

    __metaclass__ = NodeClass
    icon = None

    def __init__(self):
        gobject.GObject.__init__(self)
        self.model = None
        self.parent = None
        self.selected = False

    #
    # Tree
    #

    def set_model(self, model):
        assert model is not None
        self.model = model
        self.model.add_node(self)

    def unset_model(self):
        assert self.model is not None
        self.model.remove_node(self)

    def get_name(self):
        raise NotImplementedError

    def get_index(self):
        if self.parent is None:
            if self.model is None:
                return None
            else:
                self.model.root.index(self)
        else:
            return self.parent.children.index(self)

    def trace(self):
        parent = self
        trace = [self]
        while parent is not None:
            parent = parent.parent
            trace.insert(0, parent)
        return trace

    def is_indirect_child_of(self, parent):
        if parent == self.parent: return True
        elif self.parent is None: return False
        else: return self.parent.is_indirect_child_of(parent)

    #
    # Flags
    #

    def get_fixed(self):
        return True

    def set_selected(self, selected):
        assert self.model is not None, "Can only select an node if it is part of a model."
        self.selected = selected
