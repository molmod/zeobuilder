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
from zeobuilder.nodes.base import Base as NodeBase
from zeobuilder.nodes.parent_mixin import ParentMixin
from zeobuilder.gui.simple import ok_error
from zeobuilder.models import Model as ModelBase

import gtk, gobject

import array


__all__ = ["Model"]


class Model(ModelBase, gtk.TreeStore):
    def __init__(self):
        ModelBase.__init__(self)
        gtk.TreeStore.__init__(self, ModelBase)

    def add_node(self, node):
        #print "Adding node %s (%i)" % (node.get_name(), id(node))
        if node.parent is None:
            parent_iter = None
            index = self.root.index(node)
        else:
            parent_iter = node.parent.iter
            index = node.parent.children.index(node)
        node.iter = self.insert(parent_iter, index, [node])

    def remove_node(self, node):
        #print "Removing node %s (%i)" % (node.get_name(), id(node))
        self.remove(node.iter)
        del node.iter
        self.model = None

    def set_universe(self, universe):
        ModelBase.set_universe(self, universe)
        self.universe.request_gl()

    def unset_universe(self):
        self.universe.drop_gl()
        ModelBase.unset_universe(self)

