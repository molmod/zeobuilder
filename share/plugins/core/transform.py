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
from zeobuilder.actions.composed import Interactive, InteractiveWithMemory, ImmediateWithMemory, Immediate, CancelException, UserError
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.actions.collections.interactive import InteractiveInfo, InteractiveGroup
from zeobuilder.nodes.glmixin import GLTransformationMixin
from zeobuilder.nodes.vector import Vector
from zeobuilder.nodes.analysis import calculate_center, some_fixed, list_by_parent
from zeobuilder.gui.fields_dialogs import FieldsDialogSimple
from zeobuilder.transformations import Translation, Rotation, Complete
import zeobuilder.actions.primitive as primitive
import zeobuilder.gui.fields as fields

from molmod.vectors import angle
from molmod.quaternions import quaternion_product, quaternion_from_rotation_matrix, quaternion_to_rotation_matrix

import numpy, gtk

import math, copy


#
# Immediate transformations
#


class TransformationReset(Immediate):
    description = "Reset the transformation"
    menu_info = MenuInfo("default/_Object:tools/_Transform:immediate", "_Reset", order=(0, 4, 1, 2, 0, 0))

    def analyze_selection():
        # A) calling ancestors
        if not Immediate.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        if cache.some_nodes_fixed: return False
        if len(cache.transformed_nodes) == 0: return False
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)

    def do(self):
        for node in context.application.cache.transformed_nodes:
            primitive.SetPublishedProperty(node, "transformation", node.Transformation())


class TransformationInvert(Immediate):
    description = "Apply inversion"
    menu_info = MenuInfo("default/_Object:tools/_Transform:immediate", "_Invert", order=(0, 4, 1, 2, 0, 1))

    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        transformed_nodes = cache.transformed_nodes
        translated_nodes = cache.translated_nodes
        if len(transformed_nodes) == 0: return False
        if (len(translated_nodes) == 1) and (len(cache.rotated_nodes) == 0): return False
        if some_fixed(transformed_nodes): return False
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)

    def do(self):
        cache = context.application.cache
        # Translate where possible, if necessary
        translated_nodes = cache.translated_nodes
        if len(translated_nodes) > 0:
            absolute_inversion_center = translated_nodes[-1].get_absolute_frame().translation_vector
            victims_by_parent = list_by_parent(cache.transformed_nodes[:-1])
            for parent, victims in victims_by_parent.iteritems():
                local_inversion_center = parent.get_absolute_frame().vector_apply_inverse(absolute_inversion_center)
                for victim in victims:
                    t = Translation()
                    t.translation_vector = 2 * (local_inversion_center - victim.transformation.translation_vector)
                    primitive.Transform(victim, t)

        # Apply an inversion rotation where possible
        r = Rotation()
        r.inversion_rotation()
        for victim in cache.rotated_nodes:
            primitive.Transform(victim, r, after=False)


#
# Transformation dialogs
#


class RotateDialog(ImmediateWithMemory):
    description = "Apply rotation (dialog)"
    menu_info = MenuInfo("default/_Object:tools/_Transform:dialogs", "R_otate objects", order=(0, 4, 1, 2, 1, 0))

    rotation = FieldsDialogSimple(
        "Rotation",
        fields.composed.Rotation(
            invalid_message="Make sure that the fields that describe the rotation, are correct.",
            label_text="Rotate around axis n",
        ),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK))
    )

    def analyze_selection(parameters=None):
        # A) calling ancestor
        if not ImmediateWithMemory.analyze_selection(parameters): return False
        # B) validating
        node = context.application.cache.node
        if not isinstance(node, GLTransformationMixin): return False
        if not isinstance(node.transformation, Rotation): return False
        if node.get_fixed(): return False
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)

    def ask_parameters(self):
        self.parameters.rotation = Rotation()
        if self.rotation.run(self.parameters.rotation) != gtk.RESPONSE_OK:
            self.parameters.clear()

    def do(self):
        primitive.Transform(context.application.cache.node, self.parameters.rotation, after=False)


class RotateAroundCenterDialog(ImmediateWithMemory):
    description = "Apply rotation"
    menu_info = MenuInfo("default/_Object:tools/_Transform:dialogs", "Rotate objects around c_enter", order=(0, 4, 1, 2, 1, 1))

    rotation_around_center = FieldsDialogSimple(
        "Rotation around Center",
        fields.group.Notebook([
            ("Center", fields.composed.Translation(
                invalid_message="Make sure that the fields that describe the translation, are correct.",
                label_text="Rotation center t",
            )),
            ("Rotation", fields.composed.Rotation(
                invalid_message="Make sure that the fields that describe the rotation, are correct.",
                label_text="Rotate around axis n",
            ))
        ]),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK))
    )

    def analyze_selection(parameters=None):
        # A) calling ancestor
        if not ImmediateWithMemory.analyze_selection(parameters): return False
        cache = context.application.cache
        if cache.parent is None: return False
        transformed_nodes = cache.transformed_nodes
        if len(transformed_nodes) == 0: return False
        if len(transformed_nodes) == 1 and not isinstance(transformed_nodes[0].transformation, Translation): return False
        if cache.some_nodes_fixed: return False
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)

    def ask_parameters(self):
        cache = context.application.cache
        nodes = cache.nodes
        parent = cache.parent
        self.parameters.complete = Complete()

        last = nodes[-1]
        if isinstance(last, Vector):
            last_but_one = nodes[-2]
            if (len(nodes) >= 2) and isinstance(last_but_one, Vector):
                b1, e1 = last.translations_relative_to(parent)
                b2, e2 = last_but_one.translations_relative_to(parent)
                if (b1 is not None) and (e1 is not None) and (b2 is not None) and (e2 is not None):
                    if last.children[0].target == last_but_one.children[0].target:
                        self.parameters.complete.translation_vector = copy.copy(b1)
                    angle = angle(e1 - b1, e2 - b2) / math.pi * 180
                    rotation_vector = numpy.cross(e1 - b1, e2 - b2)
                    self.parameters.complete.set_rotation_properties(angle, rotation_vector, False)
            else:
                b, e = last.translations_relative_to(self.parent)
                if (b is not None) and (e is not None):
                    self.parameters.complete.translation_vector = b
                    self.parameters.complete.set_rotation_properties(45.0, e - b, False)
        elif isinstance(last, GLTransformationMixin) and isinstance(last.transformation, Translation):
            self.parameters.complete.translation_vector = last.get_frame_relative_to(parent).translation_vector
        else:
            self.parameters.complete.translation_vector = calculate_center(cache.translations)

        if self.rotation_around_center.run(self.parameters.complete) != gtk.RESPONSE_OK:
            self.parameters.clear()
        else:
            self.parameters.complete.translation_vector -= numpy.dot(self.parameters.complete.rotation_matrix, self.parameters.complete.translation_vector)

    def do(self):
        for victim in context.application.cache.transformed_nodes:
            primitive.Transform(victim, self.parameters.complete)


class TranslateDialog(ImmediateWithMemory):
    description = "Apply translation"
    menu_info = MenuInfo("default/_Object:tools/_Transform:dialogs", "_Translate objects", order=(0, 4, 1, 2, 1, 2))

    translation = FieldsDialogSimple(
        "Translation",
        fields.composed.Translation(
            invalid_message="Make sure that the fields that describe the translation, are correct.",
            label_text="Translate with vector t",
        ),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK))
    )

    def analyze_selection(parameters=None):
        # A) calling ancestor
        if not ImmediateWithMemory.analyze_selection(parameters): return False
        cache = context.application.cache
        if cache.parent is None: return False
        if len(cache.translated_nodes) == 0: return False
        if cache.some_nodes_fixed: return False
        # B) validating
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)

    def ask_parameters(self):
        self.parameters.translation = Translation()
        cache = context.application.cache
        last = cache.nodes[-1]
        if isinstance(last, Vector):
            b, e = last.translations_relative_to(cache.parent)
            if (b is not None) and (e is not None):
                self.parameters.translation.translation_vector = e - b
        if self.translation.run(self.parameters.translation) != gtk.RESPONSE_OK:
            self.parameters.clear()
        print self.parameters

    def do(self):
        for victim in context.application.cache.translated_nodes:
            primitive.Transform(victim, self.parameters.translation)


class RoundRotation(Immediate):
    description = "Round rotation"
    menu_info = MenuInfo("default/_Object:tools/_Transform:special", "_Round rotation", order=(0, 4, 1, 2, 5, 0))
    axes = {"x": numpy.array([1, 0, 0], float),
            "y": numpy.array([0, 1, 0], float),
            "z": numpy.array([0, 0, 1], float)}

    select_quaternion = FieldsDialogSimple(
        "Select a rotation",
        fields.edit.List(
            columns=[("Fit", "cost_function"), ("Rotation", "name")],
            attribute_name="quaternion",
            show_popup=False
        ),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK))
    )

    def analyze_selection(parameters=None):
        # A) calling ancestor
        if not ImmediateWithMemory.analyze_selection(parameters): return False
        # B) validating
        node = context.application.cache.node
        if not isinstance(node, GLTransformationMixin): return False
        if not isinstance(node.transformation, Rotation): return False
        if node.get_fixed(): return False
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)


    def do(self):
        class Record(object):
            def __init__(self, name, quaternion):
                self.name = name
                self.quaternion = quaternion
                self.cost_function = 0.0

        rounded_quaternions = []
        victim = context.application.cache.node
        factor, selected_quaternion = quaternion_from_rotation_matrix(victim.transformation.rotation_matrix)

        step = 15
        for axis_name, axis in self.axes.iteritems():
            for angle_index in xrange(1, 360/step):
                angle = angle_index * step
                name = "%s (%s)" % (axis_name, angle)
                rad = angle*math.pi/360
                quaternion = numpy.concatenate(([math.cos(rad)], math.sin(rad) * axis), 1)
                rounded_quaternions.append(Record(name, quaternion))

        new_quaternions = [Record("Identity", numpy.array([1.0, 0.0, 0.0, 0.0]))]
        for record1 in rounded_quaternions:
            for record2 in rounded_quaternions:
                if record1.name[0] != record2.name[0]:
                    new_quaternions.append(
                        Record(
                            "%s after %s" % (record1.name, record2.name),
                            quaternion_product(record1.quaternion, record2.quaternion)
                        )
                    )

        def filter_out_high_cost(records):
            for record in records:
                #print selected_quaternion, record.quaternion
                cost_function = int(math.acos(numpy.dot(selected_quaternion, record.quaternion))*180.0/math.pi)
                if cost_function < 10:
                    record.cost_function = cost_function
                else:
                    record.quaternion = None

            return filter(lambda record: record.quaternion is not None, records)

        new_quaternions = filter_out_high_cost(new_quaternions)

        for index1, record1 in enumerate(new_quaternions):
            if record1.quaternion is not None:
                for record2 in new_quaternions[:index1]:
                    if record2.quaternion is not None:
                        if 1 - numpy.dot(record1.quaternion, record2.quaternion) < 1e-3:
                            record2.quaternion = None
                for record2 in rounded_quaternions:
                    if 1 - numpy.dot(record1.quaternion, record2.quaternion) < 1e-3:
                        record1.quaternion = None
                        break

        new_quaternions = filter(lambda record: record.quaternion is not None, new_quaternions)

        rounded_quaternions = filter_out_high_cost(rounded_quaternions)

        rounded_quaternions.extend(new_quaternions)

        if len(rounded_quaternions) == 0:
            raise UserError, "No similar rounded rotations found."

        rounded_quaternions.sort(lambda x, y: cmp(x.cost_function, y.cost_function))

        self.select_quaternion.main_field.records = rounded_quaternions
        user_record = Record("", rounded_quaternions[0].quaternion)
        if self.select_quaternion.run(user_record) != gtk.RESPONSE_OK:
            raise CancelException

        if user_record.quaternion is not None:
            new_transformation = copy.deepcopy(victim.transformation)
            new_transformation.rotation_matrix = factor * quaternion_to_rotation_matrix(user_record.quaternion)
            primitive.SetPublishedProperty(victim, "transformation", new_transformation)


#
# Interactive rotations
#


class RotateMouseMixin(object):
    def button_press(self, drawing_area, event):
        if event.button == 1: # XY rotate
            self.former_x = event.x
            self.former_y = event.y
        if event.button == 3: # Z rotate
            self.former_rotz = 180/math.pi*math.atan2(-(event.y - self.screen_rotation_center[1]), event.x - self.screen_rotation_center[0])

    def button_motion(self, drawing_area, event, start_button):
        if start_button == 2: return
        if start_button == 1: # XY rotation
            rotx = (event.x - self.former_x) / float(drawing_area.allocation.width) * 360
            roty = (event.y - self.former_y) / float(drawing_area.allocation.width) * 360
            rotation_axis = numpy.array([-roty, -rotx, 0.0])
            rotation_angle = math.sqrt(rotx*rotx + roty*roty)
            self.former_x = event.x
            self.former_y = event.y
        if start_button == 3: # Z rotation
            rotz = 180/math.pi*math.atan2(-(event.y - self.screen_rotation_center[1]), event.x - self.screen_rotation_center[0])
            rotation_axis = numpy.array([0.0, 0.0, -1.0])
            rotation_angle = rotz - self.former_rotz
            self.former_rotz = rotz
        if self.user_to_parent is not None:
            rotation_axis = numpy.dot(self.user_to_parent, rotation_axis)
        if self.rotation_axis is not None:
            rotation_axis = self.rotation_axis * {True: 1, False: -1}[numpy.dot(self.rotation_axis, rotation_axis) > 0]
        temp = Rotation()
        temp.set_rotation_properties(rotation_angle, rotation_axis, False)
        return temp

    def button_release(self, drawing_area, event):
        self.finish()


class RotateKeyboardMixin(object):
    def key_press(self, drawing_area, event):
        rotation_angle = 5.0
        if event.keyval == 65365:
            rotation_axis = numpy.array([ 0.0,  0.0, -1.0])
        elif event.keyval == 65366:
            rotation_axis = numpy.array([ 0.0,  0.0,  1.0])
        elif event.keyval == 65363:
            rotation_axis = numpy.array([ 0.0, -1.0,  0.0])
        elif event.keyval == 65361:
            rotation_axis = numpy.array([ 0.0,  1.0,  0.0])
        elif event.keyval == 65364:
            rotation_axis = numpy.array([-1.0,  0.0,  0.0])
        elif event.keyval == 65362:
            rotation_axis = numpy.array([ 1.0,  0.0,  0.0])
        else:
            return None

        if self.user_to_parent is not None:
            rotation_axis = numpy.dot(self.user_to_parent, rotation_axis)
        if self.rotation_axis is not None:
            rotation_axis = self.rotation_axis * {True: 1, False: -1}[numpy.dot(self.rotation_axis, rotation_axis) > 0]
        temp = Rotation()
        temp.set_rotation_properties(rotation_angle, rotation_axis, False)
        return temp

    def key_release(self, drawing_area, event):
        self.finish()


class RotateObjectBase(InteractiveWithMemory):
    def analyze_selection(parameters=None):
        if not InteractiveWithMemory.analyze_selection(parameters): return False
        application = context.application
        if application.main is None: return False
        nodes = application.cache.nodes
        if len(nodes) == 0: return False
        if nodes[0].get_fixed(): return False
        if len(nodes) == 1:
            if not isinstance(nodes[0], GLTransformationMixin): return False
            if not isinstance(nodes[0].transformation, Rotation): return False
        elif len(nodes) == 2:
            if not isinstance(nodes[0], GLTransformationMixin): return False
            if not (isinstance(nodes[1], Vector) or (isinstance(nodes[1], GLTransformationMixin) and isinstance(nodes[1].transformation, Translation))): return False
        else:
            return False
        return True
    analyze_selection = staticmethod(analyze_selection)

    def interactive_init(self):
        InteractiveWithMemory.interactive_init(self)
        nodes = context.application.cache.nodes
        self.victim = nodes[0]
        self.rotation_axis = None
        self.changed = False
        if len(nodes) == 2:
            helper = nodes[1]
            # take the information out of the helper nodes
            if isinstance(helper, Vector):
                b, e = helper.translations_relative_to(self.victim.parent)
                if not ((b is None) or (e is None)):
                    self.rotation_center = b
                    self.rotation_axis = e - b
                    norm = numpy.dot(self.rotation_axis, self.rotation_axis)
                    if norm > 0.0:
                        self.rotation_axis /= norm
                    else:
                        self.rotation_axis = None
            else:
                self.rotation_center = copy.copy(helper.get_frame_relative_to(self.victim.parent).translation_vector)
        else:
            self.rotation_center = copy.copy(self.victim.transformation.translation_vector)

        drawing_area = context.application.main.drawing_area
        # use the modelview to translate screen coordinates to x,y,z coordinats in the victims parent frame
        self.model_view = drawing_area.scene.get_parent_model_view(self.victim)
        # now find the screen position of the center of the object
        self.screen_rotation_center = drawing_area.position_on_screen(self.model_view.vector_apply(self.rotation_center))
        #print "rotation_center: " + str(self.rotation_center)
        # reduce the viewer frame to a 3x3 matrix
        self.user_to_parent = numpy.transpose(self.model_view.rotation_matrix)

        self.old_transformation = copy.deepcopy(self.victim.transformation)


    def apply_rotation(self, rotation):
        tr = self.victim.transformation
        if isinstance(self.victim.transformation, Translation):
            tr.translation_vector -= self.rotation_center
            tr.translation_vector = numpy.dot(numpy.transpose(rotation.rotation_matrix), tr.translation_vector)
            tr.translation_vector += self.rotation_center
        if isinstance(self.victim.transformation, Rotation):
            tr.rotation_matrix = numpy.dot(numpy.transpose(rotation.rotation_matrix), tr.rotation_matrix)
        self.victim.revalidate_transformation_list()
        context.application.main.drawing_area.queue_draw()
        #self.victim.invalidate_transformation_list()

    def finish(self):
        if self.changed:
            self.parameters.transformation = copy.deepcopy(self.victim.transformation)
            self.parameters.transformation.apply_inverse_before(self.old_transformation)
            primitive.SetPublishedProperty(self.victim, "transformation",
                                           self.old_transformation, done=True)
        InteractiveWithMemory.finish(self)

    def immediate_do(self):
        primitive.Transform(context.application.cache.node, self.parameters.transformation)


class RotateObjectMouse(RotateObjectBase, RotateMouseMixin):
    description = "Rotate object"
    interactive_info = InteractiveInfo("rotate.svg", mouse=True, order=0)

    def button_motion(self, drawing_area, event, start_button):
        self.apply_rotation(RotateMouseMixin.button_motion(self, drawing_area, event, start_button))
        self.changed = True


class RotateObjectKeyboard(RotateObjectBase, RotateKeyboardMixin):
    description = "Rotate object"
    interactive_info = InteractiveInfo("rotate.svg", keyboard=True, order=0)
    sensitive_keys = [65365, 65366, 65363, 65361, 65364, 65362]

    def key_press(self, drawing_area, event):
        rotation = RotateKeyboardMixin.key_press(self, drawing_area, event)
        if rotation is not None: self.apply_rotation(rotation)
        self.changed = True


class RotateWorldBase(Interactive):
    def analyze_selection():
        # A) calling ancestor
        if not Interactive.analyze_selection(): return False
        # B) validating
        if context.application.main is None: return False
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)


    def interactive_init(self):
        Interactive.interactive_init(self)
        drawing_area = context.application.main.drawing_area
        self.screen_rotation_center = drawing_area.position_on_screen(drawing_area.scene.viewer.translation_vector)
        self.user_to_parent = None
        self.rotation_axis = None


class RotateWorldMouse(RotateWorldBase, RotateMouseMixin):
    description = "Rotate world"
    interactive_info = InteractiveInfo("rotate.svg", mouse=True, order=1)

    def button_motion(self, drawing_area, event, start_button):
        drawing_area.scene.rotation.apply_before(RotateMouseMixin.button_motion(self, drawing_area, event, start_button))
        drawing_area.queue_draw()


class RotateWorldKeyboard(RotateWorldBase, RotateKeyboardMixin):
    description = "Rotate world"
    interactive_info = InteractiveInfo("rotate.svg", keyboard=True, order=1)
    sensitive_keys = [65365, 65366, 65363, 65361, 65364, 65362]

    def key_press(self, drawing_area, event):
        rotation = RotateKeyboardMixin.key_press(self, drawing_area, event)
        if rotation is None: return
        drawing_area.scene.rotation.apply_before(rotation)
        drawing_area.queue_draw()


#
# Interactive Translations
#


class TranslateMouseMixin(object):
    def button_press(self, drawing_area, event):
        if event.button == 1: # XY translate
            self.former_x = event.x
            self.former_y = event.y
        elif event.button == 3: # Z translate
            self.former_x = event.x
        self.depth_scale = drawing_area.center_in_depth_scale(self.victim_depth)

    def button_motion(self, drawing_area, event, start_button):
        self.has_changed = True
        if start_button == 2: return numpy.array([0.0, 0.0, 0.0])
        elif start_button == 1: # XY translation
            trans = self.depth_scale * numpy.array([event.x - self.former_x, -(event.y - self.former_y), 0.0])
            self.former_x = event.x
            self.former_y = event.y
        elif start_button == 3: # Z translation
            delta_z = (1 + abs(self.victim_depth)) * (event.x - self.former_x) * 0.01
            trans = numpy.array([0.0, 0.0, delta_z])
            self.update_victim_depth()
            self.former_x = event.x
        if self.user_to_parent is None:
            return trans
        else:
            return numpy.dot(self.user_to_parent, trans)

    def button_release(self, drawing_area, event):
        self.finish()


class TranslateKeyboardMixin(object):
    def key_press(self, drawing_area, event):
        if event.keyval == 65365:
            translation_vector = numpy.array([ 0.0,  0.0, -0.1])
        elif event.keyval == 65366:
            translation_vector = numpy.array([ 0.0,  0.0,  0.1])
        elif event.keyval == 65363:
            translation_vector = numpy.array([ 0.1,  0.0,  0.0])
        elif event.keyval == 65361:
            translation_vector = numpy.array([-0.1,  0.0,  0.0])
        elif event.keyval == 65364:
            translation_vector = numpy.array([ 0.0, -0.1,  0.0])
        elif event.keyval == 65362:
            translation_vector = numpy.array([ 0.0,  0.1,  0.0])
        else:
            return None

        self.update_victim_depth()
        translation_vector *= 0.02 * (1 + abs(self.victim_depth))

        if self.user_to_parent is None:
            return translation_vector
        else:
            return numpy.dot(self.user_to_parent, translation_vector)

    def key_release(self, drawing_area, event):
        self.finish()


class TranslateObjectBase(InteractiveWithMemory):
    def analyze_selection(parameters=None):
        if not InteractiveWithMemory.analyze_selection(parameters): return False
        application = context.application
        if application is None: return False
        victim = application.cache.node
        if victim is None: return False
        if victim.get_fixed(): return False
        if not isinstance(victim, GLTransformationMixin): return False
        if not isinstance(victim.transformation, Translation): return False
        return True
    analyze_selection = staticmethod(analyze_selection)

    def interactive_init(self):
        InteractiveWithMemory.interactive_init(self)
        self.victim = context.application.cache.node
        self.update_victim_depth()
        self.user_to_parent = numpy.transpose(self.model_view.rotation_matrix)
        self.changed = False

        self.old_transformation = copy.deepcopy(self.victim.transformation)

    def update_victim_depth(self):
        self.model_view = context.application.main.drawing_area.scene.get_parent_model_view(self.victim)
        self.victim_depth = abs(self.model_view.vector_apply(self.victim.transformation.translation_vector)[2])

    def finish(self):
        if self.changed:
            self.parameters.transformation = copy.deepcopy(self.victim.transformation)
            self.parameters.transformation.apply_inverse_before(self.old_transformation)
            primitive.SetPublishedProperty(self.victim, "transformation", self.old_transformation, done=True)
        InteractiveWithMemory.finish(self)

    def immediate_do(self):
        primitive.Transform(context.application.cache.node, self.parameters.transformation)


class TranslateObjectMouse(TranslateObjectBase, TranslateMouseMixin):
    description = "Translate the selected object"
    interactive_info = InteractiveInfo("translate.svg", mouse=True, order=0)

    def button_motion(self, drawing_area, event, start_button):
        self.victim.transformation.translation_vector += TranslateMouseMixin.button_motion(self, drawing_area, event, start_button)
        self.victim.revalidate_transformation_list()
        drawing_area.queue_draw()
        #self.victim.invalidate_transformation_list()
        self.changed = True


class TranslateObjectKeyboard(TranslateObjectBase, TranslateKeyboardMixin):
    description = "Translate the selected object"
    interactive_info = InteractiveInfo("translate.svg", keyboard=True, order=0)
    sensitive_keys = [65365, 65366, 65363, 65361, 65364, 65362]

    def key_press(self, drawing_area, event):
        self.victim.transformation.translation_vector += TranslateKeyboardMixin.key_press(self, drawing_area, event)
        self.victim.revalidate_transformation_list()
        context.application.main.drawing_area.queue_draw()
        #self.victim.invalidate_transformation_list()
        self.changed = True


class TranslateWorldBase(Interactive):
    def analyze_selection():
        # A) calling ancestor
        if not Interactive.analyze_selection(): return False
        # B) validating
        if context.application.main is None: return False
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)

    def interactive_init(self):
        Interactive.interactive_init(self)
        self.model_view = context.application.main.drawing_area.scene.get_parent_model_view(None)
        self.victim_depth = abs(self.model_view.translation_vector[2])
        self.user_to_parent = numpy.transpose(self.model_view.rotation_matrix)

    def update_victim_depth(self):
        self.model_view = context.application.main.drawing_area.scene.get_parent_model_view(None)
        self.victim_depth = abs(self.model_view.translation_vector[2])


class TranslateWorldMouse(TranslateWorldBase, TranslateMouseMixin):
    description = "Translate world"
    interactive_info = InteractiveInfo("translate.svg", mouse=True, order=1)

    def button_motion(self, drawing_area, event, start_button):
        drawing_area.scene.center.translation_vector -= TranslateMouseMixin.button_motion(self, drawing_area, event, start_button)
        drawing_area.queue_draw()


class TranslateWorldKeyboard(TranslateWorldBase, TranslateKeyboardMixin):
    description = "Translate world"
    interactive_info = InteractiveInfo("translate.svg", keyboard=True, order=1)
    sensitive_keys = [65365, 65366, 65363, 65361, 65364, 65362]

    def key_press(self, drawing_area, event):
        context.application.main.drawing_area.scene.center.translation_vector -= TranslateKeyboardMixin.key_press(self, drawing_area, event)
        context.application.main.drawing_area.queue_draw()


class TranslateViewerBase(Interactive):
    def analyze_selection():
        # A) calling ancestor
        if not Interactive.analyze_selection(): return False
        # B) validating
        if context.application.main is None: return False
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)

    def interactive_init(self):
        Interactive.interactive_init(self)
        self.update_victim_depth()
        self.user_to_parent = None

    def update_victim_depth(self):
        self.victim_depth = abs(context.application.main.drawing_area.scene.viewer.translation_vector[2])


class TranslateViewerMouse(TranslateViewerBase, TranslateMouseMixin):
    description = "Translate the viewer position"
    interactive_info = InteractiveInfo("translate_viewer.svg", mouse=True, order=0)

    def button_motion(self, drawing_area, event, start_button):
        scene = drawing_area.scene
        if (scene.opening_angle > 0) or (start_button == 1):
            scene.viewer.translation_vector += TranslateMouseMixin.button_motion(self, drawing_area, event, start_button)
        else:
            scene.window_size *= (1 + 0.01*TranslateMouseMixin.button_motion(self, drawing_area, event, start_button)[-1])
            if scene.window_size < 0.001: scene.window_size = 0.001
            elif scene.window_size > 1000: scene.window_size = 1000
        drawing_area.queue_draw()

class TranslateViewerKeyboard(TranslateViewerBase, TranslateKeyboardMixin):
    description = "Translate the viewer position"
    interactive_info = InteractiveInfo("translate_viewer.svg", keyboard=True, order=0)
    sensitive_keys = [65365, 65366, 65363, 65361, 65364, 65362]

    def key_press(self, drawing_area, event):
        context.application.main.drawing_area.scene.viewer.translation_vector += TranslateKeyboardMixin.key_press(self, drawing_area, event)
        context.application.main.drawing_area.queue_draw()


actions = {
    "TransformationReset": TransformationReset,
    "TransformationInvert": TransformationInvert,
    "RotateDialog": RotateDialog,
    "RotateAroundCenterDialog": RotateAroundCenterDialog,
    "TranslateDialog": TranslateDialog,
    "RoundRotation": RoundRotation,
    "RotateObjectMouse": RotateObjectMouse,
    "RotateObjectKeyboard": RotateObjectKeyboard,
    "RotateWorldMouse": RotateWorldMouse,
    "RotateWorldKeyboard": RotateWorldKeyboard,
    "TranslateObjectMouse": TranslateObjectMouse,
    "TranslateObjectKeyboard": TranslateObjectKeyboard,
    "TranslateWorldMouse": TranslateWorldMouse,
    "TranslateWorldKeyboard": TranslateWorldKeyboard,
    "TranslateViewerMouse": TranslateViewerMouse,
    "TranslateViewerKeyboard": TranslateViewerKeyboard,
}


interactive_groups = {
    "rotation": InteractiveGroup(
        image_name="rotate.svg",
        description="Rotation tool",
        initial_mask=gtk.gdk.CONTROL_MASK,
        order=1
    ),
    "translation": InteractiveGroup(
        image_name="translate.svg",
        description="Translation tool",
        initial_mask=gtk.gdk.SHIFT_MASK,
        order=2
    ),
    "viewer_translation": InteractiveGroup(
        image_name="translate_viewer.svg",
        description="Viewer Translation tool",
        initial_mask=(gtk.gdk.CONTROL_MASK | gtk.gdk.SHIFT_MASK),
        order=3
    )
}
