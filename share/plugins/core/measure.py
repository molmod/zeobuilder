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
from zeobuilder.actions.composed import Interactive
from zeobuilder.actions.collections.interactive import InteractiveInfo, InteractiveGroup
from zeobuilder.nodes.glmixin import GLTransformationMixin
from zeobuilder.nodes.vector import Vector
from zeobuilder.transformations import Translation
from zeobuilder.gui.glade_wrapper import GladeWrapper

import math, numpy


class MeasurementsDialog(GladeWrapper):
    def __init__(self):
        GladeWrapper.__init__(self, "zeobuilder.glade", "wi_measurements", "window")
        self.window.hide()
        self.init_callbacks(self.__class__)

        context.application.action_manager.connect("action-started", self.on_action_started)

        self.chain = numpy.zeros((4, 2), float)
        self.chain_len = 0

    def on_window_delete_event(self, window, event):
        self.clear()
        return True

    def on_action_started(self, action_manager):
        if not isinstance(action_manager.current_action, Measure):
            self.clear()

    def clear(self):
        self.window.hide()
        self.chain_len = 0
        self.update_widgets()
        context.application.main.drawing_area.tool_clear()

    def add_point(self, point):
        if self.chain_len > 0:
            delta = point - self.chain[self.chain_len-1]
            distance = math.sqrt(numpy.dot(delta, delta))
            if distance < 1e-6:
                return
        if self.chain_len > 1:
            delta = point - self.chain[self.chain_len-2]
            distance = math.sqrt(numpy.dot(delta, delta))
            if distance < 1e-6:
                return
        if self.chain_len < 4:
            self.chain[self.chain_len] = point
            self.chain_len += 1
        else:
            self.chain[0:3] = self.chain[1:4]
            self.chain[-1] = point
        context.application.main.drawing_area.tool_chain(self.chain[:self.chain_len])
        if self.chain_len > 1:
            self.update_widgets()
            self.window.show()

    def update_widgets(self):
        pass

class Measure(Interactive):
    description = "Measure distances and angles"
    interactive_info = InteractiveInfo("measure.svg", mouse=True)

    measurements = MeasurementsDialog()

    def button_press(self, drawing_area, event):
        if event.button == 1:
            gl_object = drawing_area.get_nearest(event.x, event.y)
            if isinstance(gl_object, GLTransformationMixin) and \
               isinstance(gl_object.transformation, Translation):
                self.measurements.add_point(numpy.array(
                    drawing_area.to_reduced(
                        *drawing_area.position_of_object(gl_object)
                    ))
                )
                return
            elif isinstance(gl_object, Vector):
                b = gl_object.children[0].target
                e = gl_object.children[1].target
                self.measurements.add_point(numpy.array(
                    drawing_area.to_reduced(
                        *drawing_area.position_of_object(b)
                    ))
                )
                self.measurements.add_point(numpy.array(
                    drawing_area.to_reduced(
                        *drawing_area.position_of_object(e)
                    ))
                )
                return

        self.measurements.clear()


actions = {
    "Measure": Measure
}

interactive_groups = {
    "measure": InteractiveGroup(
        image_name="measure.svg",
        description="Measurement tool",
        order=4
    )
}
