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


from zeobuilder import context

from zeobuilder.nodes.node import Node, NodeInfo
from zeobuilder.nodes.glmixin import GLTransformationMixin
from zeobuilder.nodes.analysis import bridge as tree_bridge
from zeobuilder.gui import load_image

from molmod.transformations import Translation

import gtk.gdk, gobject

import os


__all__ = ["Reference", "SpatialReference", "GLTransformedReference"]


class Reference(Node):
    info = NodeInfo("SelectTargets")
    overlay_icon = load_image("reference.svg", (20, 20))

    def __init__(self, prefix):
        Node.__init__(self)
        self.target = None
        self.prefix = prefix
        self.icon = self.overlay_icon

    def set_target(self, target):
        if self.target is None and target is not None:
            self.define_target(target)
        elif self.target is not None and target is not None:
            self.undefine_target()
            self.define_target(target)
        elif self.target is not None and target is None:
            self.undefine_target()
        else:
            return

    #
    # Tree
    #

    def get_name(self):
        if self.target is None:
            return "Empty reference. This should never happen. Contact the authors."
        else:
            return self.prefix + ": " + self.target.name

    def set_model(self, model, parent, index):
        Node.set_model(self, model, parent, index)
        if self.target is not None:
            self.target.references.append(self)

    def unset_model(self):
        Node.unset_model(self)
        if self.target is not None:
            self.target.references.remove(self)

    #
    # Targets
    #

    def define_target(self, new_target):
        assert self.target is None, "Reference already has a target"
        assert new_target is not None, "Must assign a target"
        assert self.check_target(new_target), "Target %s not accepted" % new_target
        self.target = new_target
        if self.model is not None:
            self.target.references.append(self)
        self.icon = self.target.reference_icon
        self.parent.define_target(self, new_target)

    def undefine_target(self):
        assert self.target is not None, "Reference has no target to undefine"
        old_target = self.target
        if self.model is not None:
            old_target.references.remove(self)
        self.target = None
        self.icon = self.overlay_icon
        self.parent.undefine_target(self, old_target)

    def check_target(self, new_target):
        if isinstance(new_target, Reference): return False
        if self.parent is not None:
            return self.parent.check_target(self, new_target)
        else:
            return True


class SpatialReference(Reference):
    #
    # State
    #

    def __init__(self, prefix):
        Reference.__init__(self, prefix)
        self.bridge_handlers = []

    #
    # Tree
    #

    def set_model(self, model, parent, index):
        Reference.set_model(self, model, parent, index)
        if self.target is not None: self.connect_bridge()

    def unset_model(self):
        Reference.unset_model(self)
        if self.target is not None: self.disconnect_bridge()

    #
    # Targets
    #

    def define_target(self, new_target):
        Reference.define_target(self, new_target)
        if self.model is not None: self.connect_bridge()

    def undefine_target(self):
        if self.model is not None: self.disconnect_bridge()
        Reference.undefine_target(self)

    def check_target(self, new_target):
        if not isinstance(new_target, GLTransformationMixin) or not isinstance(new_target.transformation, Translation): return False
        return Reference.check_target(self, new_target)

    def on_target_move(self, model_object):
        self.disconnect_bridge()
        self.connect_bridge()
        self.parent.target_moved(self, model_object)

    def on_target_transformed(self, model_object):
        self.parent.target_moved(self, model_object)

    def connect_bridge(self):
        bridge = tree_bridge(self, self.target)
        for model_object in bridge:
            self.bridge_handlers.append((model_object, model_object.connect("on-move", self.on_target_move)))
            if isinstance(model_object, GLTransformationMixin):
                self.bridge_handlers.append((model_object, model_object.connect("on-transformation-list-invalidated", self.on_target_transformed)))

    def disconnect_bridge(self):
        for model_object, connection_identifier in self.bridge_handlers:
            model_object.disconnect(connection_identifier)
        self.bridge_handlers = []

    #
    # About translation
    #

    def translation_relative_to(self, other):
        if self.target is not None:
            return self.target.get_frame_relative_to(other).t
        else:
            return None


