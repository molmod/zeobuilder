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
from zeobuilder.gui.glade_wrapper import GladeWrapper
from zeobuilder.conversion import express_measure

from molmod.vectors import angle
from molmod.transformations import Translation

from OpenGL.GLUT import *
from OpenGL.GL import *
import numpy

import math


class MeasurementsWindow(GladeWrapper):
    def __init__(self):
        GladeWrapper.__init__(self, "plugins/core/gui.glade", "wi_measurements", "window")
        self.window.hide()
        self.init_callbacks(self.__class__)

        labels_chain2 = ["distances",
            "label_12", "distance_12"
        ]
        labels_chain3 = ["angles", "distances_to_line",
            "label_23", "distance_23",
            "label_123", "angle_123",
            "label_1_23", "distance_1_23",
        ]
        labels_chain_only3 = [
            "label_12_3", "distance_12_3",
        ]
        labels_chain4 = [
            "dihedral_angles", "out_of_plane_angles",
            "distances_to_plane", "distances_between_lines",
            "label_34", "distance_34",
            "label_234", "angle_234",
            "label_123_234", "angle_123_234",
            "label_12_234", "angle_12_234",
            "label_123_34", "angle_123_34",
            "label_1_234", "distance_1_234",
            "label_123_4", "distance_123_4",
            "label_23_4", "distance_23_4",
            "label_12_34", "distance_12_34",
        ]
        labels_chain_closed = [
            "label_31", "distance_31",
            "label_231", "angle_231",
            "label_312", "angle_312",
            "label_31_2", "distance_31_2",
        ]

        self.init_proxies(
            labels_chain2 + labels_chain3 + labels_chain_only3 + labels_chain4 +
            labels_chain_closed
        )
        self.labels_chain2 = [self.__dict__[label] for label in labels_chain2]
        self.labels_chain3 = [self.__dict__[label] for label in labels_chain3]
        self.labels_chain_only3 = [self.__dict__[label] for label in labels_chain_only3]
        self.labels_chain4 = [self.__dict__[label] for label in labels_chain4]
        self.labels_chain_closed = [self.__dict__[label] for label in labels_chain_closed]

        context.application.action_manager.connect("action-started", self.on_action_started)
        context.application.action_manager.connect("action-ends", self.on_action_ended)
        context.application.action_manager.connect("action-cancels", self.on_action_ended)

        self.model_objects = []
        self.points = []
        self.vectors = []

    def on_window_delete_event(self, window, event):
        self.clear()
        return True

    def on_action_started(self, action_manager):
        if not isinstance(action_manager.current_action, Measure):
            if len(self.model_objects) == 1:
                self.clear()
            else:
                context.application.main.drawing_area.tool_clear(queue=False)

    def on_action_ended(self, action_manager):
        if not isinstance(action_manager.current_action, Measure):
            self.reveal()

    def reveal(self):
        drawing_area = context.application.main.drawing_area

        # first check wether some modelobjects have disapeared:
        self.model_objects = [
            model_object
            for model_object
            in self.model_objects
            if model_object.model == context.application.model
        ]
        # update the vectors and the points
        self.vectors = [
            drawing_area.vector_of_object(model_object)
            for model_object
            in self.model_objects
        ]
        self.points = [
            drawing_area.to_reduced(*drawing_area.position_of_vector(vector))
            for vector
            in self.vectors
        ]

        self.update_widgets()

    def clear(self):
        self.model_objects = []
        self.points = []
        self.vectors = []
        self.update_widgets()

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

        self.update_widgets()

    def reverse(self):
        if len(self.model_objects) > 0:
            self.model_objects.reverse()
            self.vectors.reverse()
            self.points.reverse()
            self.update_widgets()

    def remove_last_object(self):
        if len(self.model_objects) > 0:
            self.model_objects.pop()
            self.vectors.pop()
            self.points.pop()
            self.update_widgets()

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
        def show_labels(labels):
            for label in labels:
                label.show()

        def hide_labels(labels):
            for label in labels:
                label.hide()

        def express_distance(index1, index2):
            delta = self.vectors[index1] - self.vectors[index2]
            return express_measure(math.sqrt(numpy.dot(delta, delta)), measure="Length")

        def express_angle(index1, index2, index3):
            delta1 = self.vectors[index1] - self.vectors[index2]
            delta2 = self.vectors[index3] - self.vectors[index2]
            return express_measure(angle(delta1, delta2), measure="Angle")

        def express_distance_to_line(index1, index2, index3):
            delta1 = self.vectors[index1] - self.vectors[index2]
            delta2 = self.vectors[index2] - self.vectors[index3]
            delta2 /= math.sqrt(numpy.dot(delta2, delta2))
            normal = delta1 - delta2*numpy.dot(delta1, delta2)
            return express_measure(math.sqrt(numpy.dot(normal, normal)), measure="Length")

        def express_dihedral_angle(index1, index2, index3, index4):
            normal1 = numpy.cross(
                self.vectors[index1] - self.vectors[index2],
                self.vectors[index3] - self.vectors[index2]
            )
            normal2 = numpy.cross(
                self.vectors[index2] - self.vectors[index3],
                self.vectors[index4] - self.vectors[index3]
            )
            return express_measure(angle(normal1, normal2), measure="Angle")

        def express_out_of_plane_angle(index1, index2, index3, index4):
            delta = self.vectors[index1] - self.vectors[index2]
            normal = numpy.cross(
                self.vectors[index4] - self.vectors[index3],
                self.vectors[index2] - self.vectors[index3]
            )
            return express_measure(0.5*math.pi - angle(normal, delta), measure="Angle")

        def express_distance_to_plane(index1, index2, index3, index4):
            delta = self.vectors[index1] - self.vectors[index2]
            normal = numpy.cross(
                self.vectors[index2] - self.vectors[index3],
                self.vectors[index4] - self.vectors[index3]
            )
            normal /= math.sqrt(numpy.dot(normal, normal))
            return express_measure(abs(numpy.dot(delta, normal)), measure="Length")

        def express_distance_between_lines(index1, index2, index3, index4):
            delta1 = self.vectors[index1] - self.vectors[index2]
            delta2 = self.vectors[index3] - self.vectors[index4]
            normal = numpy.cross(delta1, delta2)
            normal /= math.sqrt(numpy.dot(normal, normal))
            delta3 = self.vectors[index1] - self.vectors[index3]
            return express_measure(abs(numpy.dot(delta3, normal)), measure="Length")

        chain_len = len(self.model_objects)
        if chain_len > 0:
            context.application.main.drawing_area.tool_custom(self.draw_tool_chain)
        else:
            context.application.main.drawing_area.tool_clear()

        if chain_len > 1:
            self.window.show()

            if chain_len > 1:
                show_labels(self.labels_chain2)
                self.distance_12.set_label(express_distance(0, 1))
            else:
                hide_labels(self.labels_chain2)

            if chain_len > 2:
                show_labels(self.labels_chain3)
                self.distance_23.set_label(express_distance(1, 2))
                self.angle_123.set_label(express_angle(0, 1, 2))
                self.distance_1_23.set_label(express_distance_to_line(0, 1, 2))
            else:
                hide_labels(self.labels_chain3)

            if chain_len == 3 or self.model_objects[0] == self.model_objects[-1]:
                show_labels(self.labels_chain_only3)
                self.distance_12_3.set_label(express_distance_to_line(2, 1, 0))
            else:
                hide_labels(self.labels_chain_only3)

            if chain_len > 3:
                if self.model_objects[0] == self.model_objects[-1]:
                    self.distance_31.set_label(express_distance(2, 0))
                    self.angle_231.set_label(express_angle(1, 2, 0))
                    self.angle_312.set_label(express_angle(2, 0, 1))
                    self.distance_31_2.set_label(express_distance_to_line(1, 0, 2))
                    show_labels(self.labels_chain_closed)
                    hide_labels(self.labels_chain4)
                else:
                    self.distance_34.set_label(express_distance(2, 3))
                    self.angle_234.set_label(express_angle(1, 2, 3))
                    self.angle_123_234.set_label(express_dihedral_angle(0, 1, 2, 3))
                    self.angle_12_234.set_label(express_out_of_plane_angle(0, 1, 2, 3))
                    self.angle_123_34.set_label(express_out_of_plane_angle(3, 2, 1, 0))
                    self.distance_1_234.set_label(express_distance_to_plane(0, 1, 2, 3))
                    self.distance_123_4.set_label(express_distance_to_plane(3, 2, 1, 0))
                    self.distance_23_4.set_label(express_distance_to_line(3, 1, 2))
                    self.distance_12_34.set_label(express_distance_between_lines(0, 1, 2, 3))
                    show_labels(self.labels_chain4)
                    hide_labels(self.labels_chain_closed)
            else:
                hide_labels(self.labels_chain4)
                hide_labels(self.labels_chain_closed)
        else:
            self.window.hide()


class Measure(Interactive):
    description = "Measure distances and angles"
    interactive_info = InteractiveInfo("plugins/core/measure.svg", mouse=True)

    measurements = MeasurementsWindow()

    def button_press(self, drawing_area, event):
        if event.button == 1:
            gl_object = drawing_area.get_nearest(event.x, event.y)
            if isinstance(gl_object, GLTransformationMixin) and \
               isinstance(gl_object.transformation, Translation):
                self.measurements.add_object(gl_object)
                self.finish()
                return
            elif isinstance(gl_object, Vector):
                first = gl_object.children[0].target
                last = gl_object.children[1].target
                if len(self.measurements.model_objects) > 0:
                    if (first == self.measurements.model_objects[0] or \
                        last  == self.measurements.model_objects[0]) and \
                       (first != self.measurements.model_objects[-1] or \
                        last  != self.measurements.model_objects[-1]):
                        self.measurements.reverse()
                self.measurements.add_object(first)
                self.measurements.add_object(last)
                self.finish()
                return
        elif event.button == 2:
            self.measurements.reverse()
            self.finish()
            return
        elif event.button == 3:
            self.measurements.remove_last_object()
            self.finish()
            return
        self.measurements.clear()
        self.finish()


actions = {
    "Measure": Measure
}

interactive_groups = {
    "measure": InteractiveGroup(
        image_name="plugins/core/measure.svg",
        description="Measurement tool",
        order=5
    )
}
