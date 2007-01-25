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
from zeobuilder.actions.composed import Interactive, InteractiveWithMemory, ImmediateWithMemory, Immediate, CancelException, UserError, Parameters
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.actions.collections.interactive import InteractiveInfo, InteractiveGroup
from zeobuilder.nodes.glmixin import GLTransformationMixin
from zeobuilder.nodes.vector import Vector
from zeobuilder.nodes.analysis import calculate_center, some_fixed, list_by_parent
from zeobuilder.gui.fields_dialogs import FieldsDialogSimple
import zeobuilder.actions.primitive as primitive
import zeobuilder.gui.fields as fields
import zeobuilder.authors as authors

from molmod.transformations import Translation, Rotation, Complete, rotation_around_center

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
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestors
        if not Immediate.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        if cache.some_nodes_fixed: return False
        if len(cache.transformed_nodes) == 0: return False
        # C) passed all tests:
        return True

    def do(self):
        for node in context.application.cache.transformed_nodes:
            primitive.SetProperty(node, "transformation", node.Transformation())


class TransformationInvert(Immediate):
    description = "Apply inversion"
    menu_info = MenuInfo("default/_Object:tools/_Transform:immediate", "_Invert", order=(0, 4, 1, 2, 0, 1))
    authors = [authors.toon_verstraelen]

    @staticmethod
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

    def do(self):
        cache = context.application.cache

        # Translate where possible, if necessary
        translated_nodes = cache.translated_nodes
        if len(translated_nodes) > 0:
            if isinstance(cache.last, GLTransformationMixin) and \
               isinstance(cache.last.transformation, Translation):
                absolute_inversion_center = cache.last.get_absolute_frame().t
            else:
                absolute_inversion_center = numpy.zeros(3, float)
            victims_by_parent = list_by_parent(cache.transformed_nodes)
            for parent, victims in victims_by_parent.iteritems():
                local_inversion_center = parent.get_absolute_frame().vector_apply_inverse(absolute_inversion_center)
                for victim in victims:
                    translation = Translation()
                    translation.t = 2 * (local_inversion_center - victim.transformation.t)
                    primitive.Transform(victim, translation)

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
    authors = [authors.toon_verstraelen]

    parameters_dialog = FieldsDialogSimple(
        "Rotation",
        fields.composed.Rotation(
            label_text="Rotate around axis n",
            attribute_name="rotation",
        ),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK))
    )

    @staticmethod
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

    @classmethod
    def default_parameters(cls):
        result = Parameters()
        result.rotation = Rotation()
        return result

    def do(self):
        primitive.Transform(context.application.cache.node, self.parameters.rotation, after=False)


class RotateAroundCenterDialog(ImmediateWithMemory):
    description = "Apply rotation"
    menu_info = MenuInfo("default/_Object:tools/_Transform:dialogs", "Rotate objects around c_enter", order=(0, 4, 1, 2, 1, 1))
    authors = [authors.toon_verstraelen]

    parameters_dialog = FieldsDialogSimple(
        "Rotation around Center",
        fields.group.Notebook([
            ("Center", fields.composed.Translation(
                label_text="Rotation center t",
            )),
            ("Rotation", fields.composed.Rotation(
                label_text="Rotate around axis n",
            ))
        ]),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK))
    )

    @staticmethod
    def analyze_selection(parameters=None):
        # A) calling ancestor
        if not ImmediateWithMemory.analyze_selection(parameters): return False
        cache = context.application.cache
        if cache.parent is None: return False
        if len(cache.nodes) == 1:
            if not isinstance(cache.last, GLTransformationMixin) or \
               not isinstance(cache.last.transformation, Rotation): return False
        elif len(cache.nodes) == 2:
            if not isinstance(cache.last, GLTransformationMixin) or \
               not isinstance(cache.last.transformation, Translation): return False
            if not isinstance(cache.next_to_last, GLTransformationMixin) or \
               not isinstance(cache.next_to_last.transformation, Complete): return False
        else:
            return False
        if cache.some_nodes_fixed: return False
        # C) passed all tests:
        return True

    @classmethod
    def default_parameters(cls):
        result = Parameters()
        result.complete = Complete()
        return result

    def ask_parameters(self):
        cache = context.application.cache
        nodes = cache.nodes
        last = cache.last
        next_to_last = cache.next_to_last
        parent = cache.parent

        if isinstance(last, Vector):
            if (len(nodes) >= 2) and isinstance(next_to_last, Vector):
                b1 = last.children[0].translation_relative_to(parent)
                e1 = last.children[1].translation_relative_to(parent)
                b2 = next_to_last.children[0].translation_relative_to(parent)
                e2 = next_to_last.children[1].translation_relative_to(parent)
                if (b1 is not None) and (e1 is not None) and (b2 is not None) and (e2 is not None):
                    if last.children[0].target == next_to_last.children[0].target:
                        self.parameters.complete.t = copy.copy(b1)
                    angle = angle(e1 - b1, e2 - b2)
                    rotation_vector = numpy.cross(e1 - b1, e2 - b2)
                    self.parameters.complete.set_rotation_properties(angle, rotation_vector, False)
            else:
                b = last.children[0].translation_relative_to(self.parent)
                e = last.children[1].translation_relative_to(self.parent)
                if (b is not None) and (e is not None):
                    self.parameters.complete.t = b
                    self.parameters.complete.set_rotation_properties(math.pi*0.25, e - b, False)
        elif isinstance(last, GLTransformationMixin) and isinstance(last.transformation, Translation):
            self.parameters.complete.t = last.get_frame_relative_to(parent).t
        else:
            self.parameters.complete.t = calculate_center(cache.translations)

        if self.parameters_dialog.run(self.parameters.complete) != gtk.RESPONSE_OK:
            self.parameters.clear()
        else:
            self.parameters.complete.t -= numpy.dot(self.parameters.complete.r, self.parameters.complete.t)

    def do(self):
        for victim in context.application.cache.transformed_nodes:
            primitive.Transform(victim, self.parameters.complete)


def parent_of_translated_nodes(cache):
    parent = cache.translated_nodes[0].parent
    if parent is None: return None
    for node in cache.translated_nodes[1:]:
        if node.parent != parent: return None
    return parent
parent_of_translated_nodes.authors=[authors.toon_verstraelen]


class TranslateDialog(ImmediateWithMemory):
    description = "Apply translation"
    menu_info = MenuInfo("default/_Object:tools/_Transform:dialogs", "_Translate objects", order=(0, 4, 1, 2, 1, 2))
    authors = [authors.toon_verstraelen]

    parameters_dialog = FieldsDialogSimple(
        "Translation",
        fields.composed.Translation(
            label_text="Translate with vector t",
        ),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK))
    )

    @staticmethod
    def analyze_selection(parameters=None):
        # A) calling ancestor
        if not ImmediateWithMemory.analyze_selection(parameters): return False
        # B) validating
        cache = context.application.cache
        if len(cache.translated_nodes) == 0: return False
        if cache.parent_of_translated_nodes is None: return False
        if cache.some_nodes_fixed: return False
        # C) passed all tests:
        return True

    @classmethod
    def default_parameters(cls):
        result = Parameters()
        result.translation = Translation()
        return result

    def ask_parameters(self):
        cache = context.application.cache
        last = cache.last
        parent = cache.parent_of_translated_nodes
        if isinstance(last, Vector):
            b = last.children[0].translation_relative_to(parent)
            e = last.children[1].translation_relative_to(parent)
            if (b is not None) and (e is not None):
                self.parameters.translation.t = e - b
        else:
            self.use_last_parameters()
        if self.parameters_dialog.run(self.parameters.translation) != gtk.RESPONSE_OK:
            self.parameters.clear()

    def do(self):
        for victim in context.application.cache.translated_nodes:
            primitive.Transform(victim, self.parameters.translation)


class MirrorDialog(ImmediateWithMemory):
    description = "Apply mirror transformation"
    menu_info = MenuInfo("default/_Object:tools/_Transform:dialogs", "_Mirror", order=(0, 4, 1, 2, 1, 3))
    authors = [authors.toon_verstraelen]

    parameters_dialog = FieldsDialogSimple(
        "Mirror transformation",
        fields.group.Table(fields=[
            fields.composed.ComposedArray(
                FieldClass=fields.faulty.Length,
                array_name="c.%s",
                suffices=["x", "y", "z"],
                attribute_name="center",
                label_text="Point on the mirror plane.",
                scientific=False,
            ),
            fields.composed.ComposedArray(
                FieldClass=fields.faulty.Float,
                array_name="n.%s",
                suffices=["x", "y", "z"],
                attribute_name="normal",
                label_text="Normal of the mirror plane.",
                scientific=False,
            ),
        ]),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK))
    )

    @staticmethod
    def analyze_selection(parameters=None):
        # A) calling ancestor
        if not ImmediateWithMemory.analyze_selection(parameters): return False
        # B) validating
        cache = context.application.cache
        if len(cache.translated_nodes) == 0: return False
        if cache.parent_of_translated_nodes is None: return False
        if cache.some_nodes_fixed: return False
        # C) passed all tests:
        return True

    @classmethod
    def default_parameters(cls):
        result = Parameters()
        result.center = numpy.zeros(3, float)
        result.normal = numpy.zeros(3, float)
        return result

    def ask_parameters(self):
        cache = context.application.cache
        last = cache.last
        next_to_last = cache.next_to_last
        parent = cache.parent_of_translated_nodes
        Plane = context.application.plugins.get_node("Plane")
        if isinstance(last, Plane):
            f = last.parent.get_frame_relative_to(parent)
            self.parameters.center = f.vector_apply(last.center)
            self.parameters.normal = f.vector_apply(last.normal)

            #b = last.children[0].translation_relative_to(parent)
            #e = last.children[1].translation_relative_to(parent)
            #if (b is not None) and (e is not None):
            #    self.parameters.translation.t = e - b
        else:
            self.use_last_parameters()
        if self.parameters_dialog.run(self.parameters) != gtk.RESPONSE_OK:
            self.parameters.clear()

    def do(self):
        transformation = rotation_around_center(
            self.parameters.center,
            math.pi,
            self.parameters.normal,
            True
        )

        for victim in context.application.cache.translated_nodes:
            primitive.Transform(victim, transformation)


class RoundRotation(Immediate):
    description = "Round rotation"
    menu_info = MenuInfo("default/_Object:tools/_Transform:special", "_Round rotation", order=(0, 4, 1, 2, 5, 0))
    authors = [authors.toon_verstraelen]
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

    @staticmethod
    def analyze_selection(parameters=None):
        # A) calling ancestor
        if not ImmediateWithMemory.analyze_selection(parameters): return False
        # B) validating
        cache = context.application.cache
        if len(cache.nodes) == 0 or len(cache.nodes) > 2: return False
        for node in cache.nodes:
            if not isinstance(node, GLTransformationMixin): return False
            if not isinstance(node.transformation, Rotation): return False
            if node.get_fixed(): return False
        # C) passed all tests:
        return True


    def do(self):
        class Record(object):
            def __init__(self, name, quaternion):
                self.name = name
                self.quaternion = quaternion
                self.cost_function = 0.0

        rounded_quaternions = []

        cache = context.application.cache
        if len(cache.nodes) == 1:
            victim = cache.last
            master = None
            factor, selected_quaternion = quaternion_from_rotation_matrix(victim.transformation.r)
        elif len(cache.nodes) == 2:
            master = cache.last
            victim = cache.next_to_last
            factor, selected_quaternion = quaternion_from_rotation_matrix(victim.get_frame_relative_to(master).r)

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
                cosine = numpy.dot(selected_quaternion, record.quaternion)
                if cosine > 1: cosine = 1
                elif cosine < -1: cosine = -1
                cost_function = int(math.acos(cosine)*180.0/math.pi)
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
            raise UserError("No similar rounded rotations found.")

        rounded_quaternions.sort(key=(lambda x: x.cost_function))

        self.select_quaternion.main_field.records = rounded_quaternions
        user_record = Record("", rounded_quaternions[0].quaternion)
        if self.select_quaternion.run(user_record) != gtk.RESPONSE_OK:
            raise CancelException

        if user_record.quaternion is not None:
            if len(cache.nodes) == 1:
                new_transformation = copy.deepcopy(victim.transformation)
                new_transformation.r = factor * quaternion_to_rotation_matrix(user_record.quaternion)
                primitive.SetProperty(victim, "transformation", new_transformation)
            elif len(cache.nodes) == 2:
                old_transformation = copy.deepcopy(victim.transformation)
                victim.transformation.r = numpy.identity(3, float)
                victim.transformation.r = numpy.dot(
                    master.get_frame_relative_to(victim).r,
                    factor * quaternion_to_rotation_matrix(user_record.quaternion),
                )
                primitive.SetProperty(victim, "transformation", old_transformation, done=True)


#
# Interactive rotations
#


class RotateMouseMixin(object):
    #def get_screen_rotation_center(self):
    #    raise NotImplementedError

    def button_press(self, drawing_area, event):
        if event.button == 1: # XY rotate
            self.former_x = event.x
            self.former_y = event.y
        elif event.button == 3: # Z rotate
            srcx, srcy = self.screen_rotation_center
            self.former_rotz = math.atan2(-(event.y - srcy), event.x - srcx)

    def button_motion(self, drawing_area, event, start_button):
        if start_button == 2:
            return
        elif start_button == 1: # XY rotation
            rotx = (event.x - self.former_x) / float(drawing_area.allocation.width) * 360
            roty = (event.y - self.former_y) / float(drawing_area.allocation.width) * 360
            rotation_axis = numpy.array([-roty, -rotx, 0.0], float)
            rotation_angle = math.sqrt(rotx*rotx + roty*roty)/30
            self.former_x = event.x
            self.former_y = event.y
        elif start_button == 3: # Z rotation
            srcx, srcy = self.screen_rotation_center
            rotz = math.atan2(-(event.y - srcy), event.x - srcx)
            rotation_axis = numpy.array([0.0, 0.0, -1.0], float)
            rotation_angle = rotz - self.former_rotz
            self.former_rotz = rotz
        return rotation_angle, rotation_axis

    def button_release(self, drawing_area, event):
        self.finish()


class RotateKeyboardError(Exception):
    pass


class RotateKeyboardMixin(object):
    def key_press(self, drawing_area, event):
        rotation_angle = math.pi/36.0
        rotation_axis = numpy.zeros(3, float)
        if event.keyval == 65363:
            #print "right"
            rotation_axis[1] = -1
        elif event.keyval == 65361:
            #print "left"
            rotation_axis[1] = +1
        elif event.keyval == 65362:
            #print "up"
            rotation_axis[0] = +1
        elif event.keyval == 65364:
            #print "down"
            rotation_axis[0] = -1
        elif event.keyval == 65365:
            #print "page up, to front"
            rotation_axis[2] = +1
        elif event.keyval == 65366:
            #print "page down, to back"
            rotation_axis[2] = -1
        else:
            raise RotateKeyboardError("Key %i is not supported" % event.keyval)

        return rotation_angle, rotation_axis

    def key_release(self, drawing_area, event):
        self.finish()


class RotateObjectBase(InteractiveWithMemory):
    @staticmethod
    def analyze_selection(parameters=None):
        if not InteractiveWithMemory.analyze_selection(parameters): return False
        cache = context.application.cache
        if len(cache.nodes) == 1:
            if cache.last.get_fixed(): return False
            if not isinstance(cache.last, GLTransformationMixin): return False
            if not isinstance(cache.last.transformation, Rotation): return False
        elif len(cache.nodes) == 2:
            if cache.next_to_last.get_fixed(): return False
            if not isinstance(cache.next_to_last, GLTransformationMixin): return False
            if not isinstance(cache.next_to_last.transformation, Complete): return False
            if not (
                isinstance(cache.last, Vector) or
                (
                    isinstance(cache.last, GLTransformationMixin) and
                    isinstance(cache.last.transformation, Translation)
                )
            ): return False
        else:
            return False
        return True

    def interactive_init(self):
        InteractiveWithMemory.interactive_init(self)
        cache = context.application.cache
        if len(cache.nodes) == 1:
            self.victim = cache.node
            helper = None
        else:
            self.victim = cache.next_to_last
            helper = cache.last
        self.rotation_axis = None
        self.changed = False
        rotation_center_object = None
        if helper is not None:
            # take the information out of the helper nodes
            if isinstance(helper, Vector):
                b = helper.children[0].translation_relative_to(self.victim.parent)
                e = helper.children[1].translation_relative_to(self.victim.parent)
                if not ((b is None) or (e is None)):
                    rotation_center_object = helper.children[0].target
                    self.rotation_axis = e - b
                    norm = numpy.dot(self.rotation_axis, self.rotation_axis)
                    if norm > 0.0:
                        self.rotation_axis /= norm
                    else:
                        self.rotation_axis = None
            else:
                rotation_center_object = helper
        else:
            rotation_center_object = self.victim

        self.rotation_center = rotation_center_object.get_frame_relative_to(self.victim.parent).t
        drawing_area = context.application.main.drawing_area
        self.screen_rotation_center = drawing_area.position_of_object(rotation_center_object)
        self.eye_to_model_rotation = drawing_area.eye_to_model_rotation(self.victim)
        self.old_transformation = copy.deepcopy(self.victim.transformation)

    def do_rotation(self, rotation_angle, rotation_axis):
        rotation_axis = numpy.dot(self.eye_to_model_rotation, rotation_axis)
        if self.rotation_axis is not None:
            if numpy.dot(self.rotation_axis, rotation_axis) > 0:
                rotation_axis = self.rotation_axis
            else:
                rotation_axis = -self.rotation_axis
        rotation = Rotation()
        rotation.set_rotation_properties(rotation_angle, rotation_axis, False)
        transformation = self.victim.transformation

        if isinstance(self.victim.transformation, Translation):
            transformation.t -= self.rotation_center
            transformation.t = numpy.dot(numpy.transpose(rotation.r), transformation.t)
            transformation.t += self.rotation_center
        if isinstance(self.victim.transformation, Rotation):
            transformation.r = numpy.dot(numpy.transpose(rotation.r), transformation.r)
        self.victim.revalidate_transformation_list()
        context.application.main.drawing_area.queue_draw()
        #self.victim.invalidate_transformation_list()
        self.changed = True

    def finish(self):
        if self.changed:
            self.parameters.transformation = copy.deepcopy(self.victim.transformation)
            self.parameters.transformation.apply_inverse_before(self.old_transformation)
            primitive.SetProperty(self.victim, "transformation", self.old_transformation, done=True)
            self.victim.invalidate_transformation_list() # make sure that bonds and connectors are updated after transformation
        InteractiveWithMemory.finish(self)

    def immediate_do(self):
        primitive.Transform(context.application.cache.node, self.parameters.transformation)


class RotateObjectMouse(RotateObjectBase, RotateMouseMixin):
    description = "Rotate object"
    interactive_info = InteractiveInfo("plugins/core/rotate.svg", mouse=True, order=0)
    authors = [authors.toon_verstraelen]

    def button_motion(self, drawing_area, event, start_button):
        self.do_rotation(*RotateMouseMixin.button_motion(self, drawing_area, event, start_button))


class RotateObjectKeyboard(RotateObjectBase, RotateKeyboardMixin):
    description = "Rotate object"
    interactive_info = InteractiveInfo("plugins/core/rotate.svg", keyboard=True, order=0)
    authors = [authors.toon_verstraelen]
    sensitive_keys = [65365, 65366, 65363, 65361, 65364, 65362]

    def key_press(self, drawing_area, event):
        self.do_rotation(*RotateKeyboardMixin.key_press(self, drawing_area, event))


class RotateWorldBase(Interactive):
    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Interactive.analyze_selection(): return False
        # B) validating
        if context.application.main is None: return False
        # C) passed all tests:
        return True

    def interactive_init(self):
        Interactive.interactive_init(self)
        drawing_area = context.application.main.drawing_area
        self.screen_rotation_center = drawing_area.position_of_vector(drawing_area.scene.viewer.t)

    def do_rotation(self, drawing_area, rotation_angle, rotation_axis):
        rotation = Rotation()
        rotation.set_rotation_properties(rotation_angle, rotation_axis, False)
        drawing_area.scene.rotation.apply_before(rotation)
        drawing_area.queue_draw()


class RotateWorldMouse(RotateWorldBase, RotateMouseMixin):
    description = "Rotate world"
    interactive_info = InteractiveInfo("plugins/core/rotate.svg", mouse=True, order=1)
    authors = [authors.toon_verstraelen]

    def button_motion(self, drawing_area, event, start_button):
        self.do_rotation(drawing_area, *RotateMouseMixin.button_motion(self, drawing_area, event, start_button))


class RotateWorldKeyboard(RotateWorldBase, RotateKeyboardMixin):
    description = "Rotate world"
    interactive_info = InteractiveInfo("plugins/core/rotate.svg", keyboard=True, order=1)
    authors = [authors.toon_verstraelen]
    sensitive_keys = [65365, 65366, 65363, 65361, 65364, 65362]

    def key_press(self, drawing_area, event):
        self.do_rotation(drawing_area, *RotateKeyboardMixin.key_press(self, drawing_area, event))


#
# Interactive Translations
#


class TranslateMixin(object):
    #def get_victim_depth(self, drawing_area):
    #    raise NotImplementedError

    def convert(self, translation, drawing_area):
        depth = self.get_victim_depth(drawing_area)
        translation[0:2] *= drawing_area.depth_to_scale(depth)
        translation[2] *= (1 + abs(self.get_victim_depth(drawing_area))) * 0.01
        return translation


class TranslateMouseMixin(TranslateMixin):
    def button_press(self, drawing_area, event):
        if event.button == 1: # XY translate
            self.former_x = event.x
            self.former_y = event.y
        elif event.button == 3: # Z translate
            self.former_x = event.x

    def button_motion(self, drawing_area, event, start_button):
        translation = numpy.zeros(3, float)

        if start_button == 2:
            return vector
        elif start_button == 1: # XY translation
            translation[0] =   event.x - self.former_x
            translation[1] = -(event.y - self.former_y)
            self.former_x = event.x
            self.former_y = event.y
        elif start_button == 3: # Z translation
            translation[2] = event.x - self.former_x
            self.former_x = event.x

        return self.convert(translation, drawing_area)

    def button_release(self, drawing_area, event):
        self.finish()


class TranslateKeyboardMixin(TranslateMixin):
    def key_press(self, drawing_area, event):
        translation = numpy.zeros(3, float)
        # on key press corresponds to a movement of the mouse with five pixels
        pixels = 5

        if event.keyval == 65363:
            #print "right"
            translation[0] = +pixels
        elif event.keyval == 65361:
            #print "left"
            translation[0] = -pixels
        elif event.keyval == 65362:
            #print "up"
            translation[1] = +pixels
        elif event.keyval == 65364:
            #print "down"
            translation[1] = -pixels
        elif event.keyval == 65365:
            #print "page up, to front"
            translation[2] = +pixels
        elif event.keyval == 65366:
            #print "page down, to back"
            translation[2] = -pixels

        return self.convert(translation, drawing_area)

    def key_release(self, drawing_area, event):
        self.finish()


class TranslateObjectBase(InteractiveWithMemory):
    @staticmethod
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

    def interactive_init(self):
        InteractiveWithMemory.interactive_init(self)
        self.victim = context.application.cache.node
        self.eye_to_model_rotation = context.application.main.drawing_area.eye_to_model_rotation(self.victim)
        self.changed = False

        self.old_transformation = copy.deepcopy(self.victim.transformation)

    def get_victim_depth(self, drawing_area):
        return drawing_area.depth_of_object(self.victim)

    def do_translation(self, vector, drawing_area):
        self.victim.transformation.t += numpy.dot(self.eye_to_model_rotation, vector)
        self.victim.revalidate_transformation_list()
        drawing_area.queue_draw()
        self.changed = True

    def finish(self):
        if self.changed:
            self.parameters.transformation = copy.deepcopy(self.victim.transformation)
            self.parameters.transformation.apply_inverse_before(self.old_transformation)
            primitive.SetProperty(self.victim, "transformation", self.old_transformation, done=True)
            self.victim.invalidate_transformation_list() # make sure that bonds and connectors are updated after transformation
        InteractiveWithMemory.finish(self)

    def immediate_do(self):
        primitive.Transform(context.application.cache.node, self.parameters.transformation)


class TranslateObjectMouse(TranslateObjectBase, TranslateMouseMixin):
    description = "Translate the selected object"
    interactive_info = InteractiveInfo("plugins/core/translate.svg", mouse=True, order=0)
    authors = [authors.toon_verstraelen]

    def button_motion(self, drawing_area, event, start_button):
        self.do_translation(TranslateMouseMixin.button_motion(self, drawing_area, event, start_button), drawing_area)


class TranslateObjectKeyboard(TranslateObjectBase, TranslateKeyboardMixin):
    description = "Translate the selected object"
    interactive_info = InteractiveInfo("plugins/core/translate.svg", keyboard=True, order=0)
    authors = [authors.toon_verstraelen]
    sensitive_keys = [65365, 65366, 65363, 65361, 65364, 65362]

    def key_press(self, drawing_area, event):
        self.do_translation(TranslateKeyboardMixin.key_press(self, drawing_area, event), drawing_area)


class TranslateWorldBase(Interactive):
    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Interactive.analyze_selection(): return False
        # B) validating
        if context.application.main is None: return False
        # C) passed all tests:
        return True

    def interactive_init(self):
        Interactive.interactive_init(self)
        self.eye_to_model_rotation = context.application.main.drawing_area.eye_to_model_rotation(None)

    def get_victim_depth(self, drawing_area):
        return -drawing_area.scene.modelview_matrix[2,3]

    def do_translation(self, vector, drawing_area):
        drawing_area.scene.rotation_center.t -= numpy.dot(self.eye_to_model_rotation, vector)
        drawing_area.queue_draw()


class TranslateWorldMouse(TranslateWorldBase, TranslateMouseMixin):
    description = "Translate world"
    interactive_info = InteractiveInfo("plugins/core/translate.svg", mouse=True, order=1)
    authors = [authors.toon_verstraelen]

    def button_motion(self, drawing_area, event, start_button):
        self.do_translation(TranslateMouseMixin.button_motion(self, drawing_area, event, start_button), drawing_area)


class TranslateWorldKeyboard(TranslateWorldBase, TranslateKeyboardMixin):
    description = "Translate world"
    interactive_info = InteractiveInfo("plugins/core/translate.svg", keyboard=True, order=1)
    authors = [authors.toon_verstraelen]
    sensitive_keys = [65365, 65366, 65363, 65361, 65364, 65362]

    def key_press(self, drawing_area, event):
        self.do_translation(TranslateKeyboardMixin.key_press(self, drawing_area, event), drawing_area)


class TranslateViewerBase(Interactive):
    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Interactive.analyze_selection(): return False
        # B) validating
        if context.application.main is None: return False
        # C) passed all tests:
        return True

    def get_victim_depth(self, drawing_area):
        scene = drawing_area.scene
        return scene.viewer.t[2] + scene.znear

    def do_translation(self, vector, drawing_area):
        scene = drawing_area.scene
        scene.viewer.t[:2] -= vector[:2]
        if (scene.opening_angle > 0):
            scene.viewer.t[2] -= vector[2]
        else:
            window_size = scene.window_size*(1 + 0.01*vector[2])
            if window_size < 0.001: window_size = 0.001
            elif window_size > 1000: window_size = 1000
            drawing_area.set_window_size(window_size)
        drawing_area.queue_draw()

class TranslateViewerMouse(TranslateViewerBase, TranslateMouseMixin):
    description = "Translate the viewer position"
    interactive_info = InteractiveInfo("plugins/core/translate_viewer.svg", mouse=True, order=0)
    authors = [authors.toon_verstraelen]

    def button_motion(self, drawing_area, event, start_button):
        self.do_translation(TranslateMouseMixin.button_motion(self, drawing_area, event, start_button), drawing_area)


class TranslateViewerKeyboard(TranslateViewerBase, TranslateKeyboardMixin):
    description = "Translate the viewer position"
    interactive_info = InteractiveInfo("plugins/core/translate_viewer.svg", keyboard=True, order=0)
    authors = [authors.toon_verstraelen]
    sensitive_keys = [65365, 65366, 65363, 65361, 65364, 65362]

    def key_press(self, drawing_area, event):
        self.do_translation(TranslateKeyboardMixin.key_press(self, drawing_area, event), drawing_area)


class TranslateRotationCenterBase(Interactive):
    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Interactive.analyze_selection(): return False
        # B) validating
        if context.application.main is None: return False
        # C) passed all tests:
        return True

    def interactive_init(self):
        Interactive.interactive_init(self)
        self.eye_to_model_rotation = context.application.main.drawing_area.eye_to_model_rotation(None)

    def get_victim_depth(self, drawing_area):
        scene = drawing_area.scene
        return scene.viewer.t[2] + scene.znear

    def do_translation(self, vector, drawing_area):
        scene = drawing_area.scene
        tmp = vector.copy()
        tmp[2] = 0
        transformed_vector = numpy.dot(self.eye_to_model_rotation, tmp)
        scene.viewer.t[:2] -= vector[:2]
        scene.rotation_center.t += transformed_vector
        if (scene.opening_angle > 0):
            scene.viewer.t[2] -= vector[2]
            scene.rotation_center.t[2] += transformed_vector[2]
        else:
            window_size = scene.window_size*(1 + 0.01*vector[-1])
            if window_size < 0.001: window_size = 0.001
            elif window_size > 1000: window_size = 1000
            drawing_area.set_window_size(window_size)
        drawing_area.queue_draw()


class TranslateRotationCenterMouse(TranslateRotationCenterBase, TranslateMouseMixin):
    description = "Translate the rotation center"
    interactive_info = InteractiveInfo("plugins/core/translate_center.svg", mouse=True, order=0)
    authors = [authors.toon_verstraelen]

    def button_motion(self, drawing_area, event, start_button):
        self.do_translation(TranslateMouseMixin.button_motion(self, drawing_area, event, start_button), drawing_area)


class TranslateRotationCenterKeyboard(TranslateRotationCenterBase, TranslateKeyboardMixin):
    description = "Translate the rotation center"
    interactive_info = InteractiveInfo("plugins/core/translate_center.svg", keyboard=True, order=0)
    authors = [authors.toon_verstraelen]
    sensitive_keys = [65365, 65366, 65363, 65361, 65364, 65362]

    def key_press(self, drawing_area, event):
        self.do_translation(TranslateKeyboardMixin.key_press(self, drawing_area, event), drawing_area)


cache_plugins = {
    "parent_of_translated_nodes": parent_of_translated_nodes,
}


actions = {
    "TransformationReset": TransformationReset,
    "TransformationInvert": TransformationInvert,
    "RotateDialog": RotateDialog,
    "RotateAroundCenterDialog": RotateAroundCenterDialog,
    "TranslateDialog": TranslateDialog,
    "MirrorDialog": MirrorDialog,
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
    "TranslateRotationCenterMouse": TranslateRotationCenterMouse,
    "TranslateRotationCenterKeyboard": TranslateRotationCenterKeyboard,
}


interactive_groups = {
    "rotate": InteractiveGroup(
        image_name="plugins/core/rotate.svg",
        description="Rotate",
        initial_mask=gtk.gdk.CONTROL_MASK,
        order=1,
        authors=[authors.toon_verstraelen],
    ),
    "translate": InteractiveGroup(
        image_name="plugins/core/translate.svg",
        description="Translate",
        initial_mask=gtk.gdk.SHIFT_MASK,
        order=2,
        authors=[authors.toon_verstraelen],
    ),
    "translate_viewer": InteractiveGroup(
        image_name="plugins/core/translate_viewer.svg",
        description="Translate the viewer",
        initial_mask=None,
        order=4,
        authors=[authors.toon_verstraelen],
    ),
    "translate_center": InteractiveGroup(
        image_name="plugins/core/translate_center.svg",
        description="Translate the rotation center",
        initial_mask=(gtk.gdk.CONTROL_MASK | gtk.gdk.SHIFT_MASK),
        order=3,
        authors=[authors.toon_verstraelen],
    ),
}
