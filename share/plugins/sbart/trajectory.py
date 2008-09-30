# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 - 2008 Toon Verstraelen <Toon.Verstraelen@UGent.be>
#
# This file is part of Zeobuilder.
#
# Zeobuilder is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
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
from zeobuilder.actions.composed import ImmediateWithMemory, Parameters
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.nodes.meta import Property
from zeobuilder.nodes.model_object import ModelObjectInfo
from zeobuilder.nodes.elementary import ReferentBase
from zeobuilder.nodes.reference import Reference
from zeobuilder.gui.fields_dialogs import FieldsDialogSimple
import zeobuilder.actions.primitive as primitive
import zeobuilder.gui.fields as fields
import zeobuilder.authors as authors

import numpy, gtk, copy


class TrajectoryError(Exception):
    pass


class Trajectory(ReferentBase):
    info = ModelObjectInfo("plugins/sbart/trajectory.svg", "LoadFrame")
    authors = [authors.toon_verstraelen]

    #
    # State
    #

    def create_references(self):
        return []

    def set_targets(self, targets, init=False):
        for target in self.targets:
            if not isnstance(target, Atom):
                raise TrajectoryError("References of the trajectory object can only point to atoms")
        self.children = [Reference(prefix="Track") for target in targets]
        ReferentBase.set_targets(targets, init)

    #
    # Properties
    #

    def set_frames(self, frames, init=False):
        if frames.shape[1] != len(self.children) or frames.shape[2] != 3:
            raise TrajectoryError("The frames must have the right shape, i.e. (x, %s, 3). You gave %s" % (len(self.children), frames.shape))
        self.frames = frames

    properties = [
        Property("frames", numpy.zeros((0,0,3)), lambda self: self.frames, set_frames),
    ]

    #
    # References
    #

    def check_target(self, reference, target):
        return (
            isinstance(target, context.application.plugins.get_node("Atom")) or
            isinstance(target, context.application.plugins.get_node("Point"))
        )

    #
    # Trajectory
    #

    def load_frame(self, frame_index):
        for atom_index, target in enumerate(self.get_targets()):
            target.transformation.t = self.frames[frame_index, atom_index]


class LoadFrame(ImmediateWithMemory):
    description = "Load a certain frame from the trajectory"
    menu_info = MenuInfo("default/_Object:tools/_Trajectory:conscan", "Load frame", order=(0, 4, 1, 7, 1, 1))
    authors = [authors.toon_verstraelen]

    parameters_dialog = FieldsDialogSimple(
        "Load frame",
        fields.faulty.Int(
            label_text="Frame index",
            attribute_name="frame_index",
            minimum=0,
        ),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK)),
    )

    @staticmethod
    def analyze_selection(parameters=None):
        # A) calling ancestor
        if not ImmediateWithMemory.analyze_selection(parameters): return False
        # B) validating
        if not isinstance(context.application.cache.node, Trajectory): return False
        # C) passed all tests:
        return True

    @classmethod
    def default_parameters(cls):
        result = Parameters()
        result.frame_index = 0
        return result

    def do(self):
        trajectory = context.application.cache.node
        for atom_index, translated in enumerate(trajectory.get_targets()):
            transformation = copy.deepcopy(translated.transformation)
            transformation.t[:] = trajectory.frames[self.parameters.frame_index,atom_index]
            primitive.SetProperty(translated, "transformation", transformation)


nodes = {
    "Trajectory": Trajectory
}


actions = {
    "LoadFrame": LoadFrame,
}





