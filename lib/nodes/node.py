# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 - 2009 Toon Verstraelen <Toon.Verstraelen@UGent.be>, Center
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


from zeobuilder.nodes.meta import NodeClass, Property
import zeobuilder.gui.fields as fields

import gtk.gdk, gobject

import copy


__all__ = ["Node", "NodeInfo"]


class NodeInfo(object):
    def __init__(self, default_action_name=None):
        if default_action_name is not None:
            self.default_action_name = default_action_name


class Node(gobject.GObject):
    __metaclass__ = NodeClass

    def __init__(self):
        gobject.GObject.__init__(self)
        self.model = None
        self.parent = None
        self.selected = False

    #
    # Tree
    #

    def set_model(self, model, parent, index):
        assert model is not None
        self.model = model
        self.model.add_node(self, parent, index)

    def unset_model(self):
        assert self.model is not None
        self.model.remove_node(self)
        self.set_selected(False)
        self.model = None

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
        if not self.selected and selected:
            self.model.add_to_selection(self)
            self.selected = True
            self.emit("on-selected")
        elif self.selected and not selected:
            self.model.remove_from_selection(self)
            self.selected = False
            self.emit("on-deselected")


gobject.signal_new("on-selected", Node, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
gobject.signal_new("on-deselected", Node, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())


