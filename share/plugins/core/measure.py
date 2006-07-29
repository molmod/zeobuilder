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

from OpenGL.GLUT import *
from OpenGL.GL import *
import numpy

import math


class MeasurementsDialog(GladeWrapper):
    def __init__(self):
        GladeWrapper.__init__(self, "zeobuilder.glade", "wi_measurements", "window")
        self.window.hide()
        self.init_callbacks(self.__class__)

        context.application.action_manager.connect("action-started", self.on_action_started)

        self.model_objects = []
        self.points = []
        self.vectors = []

    def on_window_delete_event(self, window, event):
        self.clear()
        return True

    def on_action_started(self, action_manager):
        if not isinstance(action_manager.current_action, Measure):
            self.clear()

    def clear(self):
        self.window.hide()
        self.model_objects = []
        self.points = []
        self.vectors = []
        self.update_widgets()
        context.application.main.drawing_area.tool_clear()

    def add_object(self, model_object):
        drawing_area = context.application.main.drawing_area

        vector = drawing_area.vector_of_object(model_object)
        point = drawing_area.to_reduced(*drawing_area.position_of_vector(vector))

        chain_len = len(self.model_objects)
        if chain_len > 0:
            delta = vector - self.vectors[chain_len-1]
            distance = math.sqrt(numpy.dot(delta, delta))
            if distance < 1e-6:
                return
        if chain_len > 1:
            delta = vector - self.vectors[chain_len-2]
            distance = math.sqrt(numpy.dot(delta, delta))
            if distance < 1e-6:
                return

        if chain_len == 4:
            self.model_objects.pop(0)
            self.vectors.pop(0)
            self.points.pop(0)
        self.model_objects.append(model_object)
        self.vectors.append(vector)
        self.points.append(point)

        context.application.main.drawing_area.tool_custom(self.draw_tool_chain)
        if chain_len > 0:
            self.update_widgets()
            self.window.show()

    def draw_tool_chain(self):
        font_scale = 0.00015
        glMatrixMode(GL_MODELVIEW)

        glColor(0, 0, 0)
        glLineWidth(5)
        glBegin(GL_LINE_STRIP)
        for point in self.points:
            glVertex3f(point[0], point[1], 0.0)
        glEnd()

        glColor(1, 1, 1)
        glLineWidth(1)
        glVertex3f(point[0], point[1], 0.0)
        glBegin(GL_LINE_STRIP)
        for point in self.points:
            glVertex3f(point[0], point[1], 0.0)
        glEnd()

        if len(self.model_objects) == 4 and \
           self.model_objects[0] == self.model_objects[3]:
            num = 3
        else:
            num = 4

        glColor(0, 0, 0)
        glLineWidth(9)
        for index, point in enumerate(self.points[:num]):
            glPushMatrix()
            glTranslate(point[0], point[1], 0.0)
            glScale(font_scale, font_scale, 1)
            glRectf(-10, -20, 114, 130)
            glPopMatrix()

        glColor(1, 1, 1)
        glLineWidth(1)
        for index, point in enumerate(self.points[:num]):
            glPushMatrix()
            glTranslate(point[0], point[1], 0.0)
            glScale(font_scale, font_scale, 1)
            glutStrokeCharacter(GLUT_STROKE_MONO_ROMAN, ord(str(index+1)))
            glPopMatrix()

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
                self.measurements.add_object(gl_object)
                return
            elif isinstance(gl_object, Vector):
                self.measurements.add_object(gl_object.children[0].target)
                self.measurements.add_object(gl_object.children[1].target)
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
