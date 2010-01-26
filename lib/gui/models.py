# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 - 2010 Toon Verstraelen <Toon.Verstraelen@UGent.be>, Center
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


from zeobuilder import context
from zeobuilder.nodes.node import Node
from zeobuilder.nodes.parent_mixin import ParentMixin
from zeobuilder.nodes.glmixin import GLMixin
from zeobuilder.gui.simple import ok_error
from zeobuilder.models import Model as ModelBase

import gtk, gobject

import array


__all__ = ["Model"]


class Model(ModelBase, gtk.TreeStore):
    def __init__(self):
        ModelBase.__init__(self)
        gtk.TreeStore.__init__(self, Node)

    def add_node(self, node, parent, index):
        #print "Adding node %s (%i)" % (node.get_name(), id(node))
        if parent is None:
            parent_iter = None
        else:
            parent_iter = node.parent.iter
        node.iter = self.insert(parent_iter, index, [node])
        if isinstance(node, GLMixin): # only the gui model requires gl
            node.initialize_gl()

    def remove_node(self, node):
        #print "Removing node %s (%i)" % (node.get_name(), id(node))
        self.remove(node.iter)
        if isinstance(node, GLMixin): # only the gui model requires gl
            node.cleanup_gl()
        del node.iter


