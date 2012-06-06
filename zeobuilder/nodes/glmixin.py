# -*- coding: utf-8 -*-
# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 - 2012 Toon Verstraelen <Toon.Verstraelen@UGent.be>, Center
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
#--


from zeobuilder import context
from zeobuilder.nodes.helpers import BoundingBox
from zeobuilder.nodes.meta import NodeClass, Property
from zeobuilder.nodes.analysis import common_parent
from zeobuilder.gui.fields_dialogs import DialogFieldInfo
import zeobuilder.gui.fields as fields

from molmod import Translation, Rotation, Complete

import gobject, numpy


__all__ = ["GLMixinError", "GLMixin", "GLTransformationMixin"]


class GLMixinError(Exception):
    pass


class GLMixin(gobject.GObject):

    __metaclass__ = NodeClass
    double_sided = False

    #
    # State
    #

    def initnonstate(self):
        self.gl_active = False
        self.connect("on-selected", self.on_select_changed)
        self.connect("on-deselected", self.on_select_changed)

    #
    # Properties
    #

    def set_visible(self, visible, init=False):
        if init:
            self.visible = visible
        elif self.visible != visible:
            self.visible = visible
            self.invalidate_total_list()

    properties = [
        Property("visible", True, lambda self: self.visible, set_visible)
    ]

    #
    # Dialog fields (see action EditProperties)
    #

    dialog_fields = set([
        DialogFieldInfo("Markup", (1, 2), fields.edit.CheckButton(
            label_text="Visible (also hides children)",
            attribute_name="visible",
        )),
        DialogFieldInfo("Basic", (0, 3), fields.read.BBox(
            label_text="Bounding box",
            attribute_name="bounding_box",
        )),
    ])

    #
    # OpenGL
    #

    def initialize_gl(self):
        assert not self.gl_active
        vb = context.application.vis_backend
        self.gl_active = True
        self.bounding_box = BoundingBox()
        self.draw_list = vb.create_list(self)
        self.boundingbox_list = vb.create_list()
        self.total_list = vb.create_list()
        ##print "Created lists (%i, %i, %i): %s" % (self.draw_list, self.boundingbox_list, self.total_list, self.get_name())
        self.draw_list_valid = True
        self.boundingbox_list_valid = True
        self.total_list_valid = True
        self.invalidate_all_lists()
        if isinstance(self.parent, GLMixin):
            self.parent.invalidate_all_lists()

    def cleanup_gl(self):
        assert self.gl_active
        self.gl_active = False
        vb = context.application.vis_backend
        ##print "Deleting lists (%i, %i, %i): %s" % (self.draw_list, self.boundingbox_list, self.total_list, self.get_name())
        vb.delete_list(self.draw_list)
        vb.delete_list(self.boundingbox_list)
        vb.delete_list(self.total_list)
        del self.bounding_box
        del self.draw_list
        del self.boundingbox_list
        del self.total_list
        del self.draw_list_valid
        del self.boundingbox_list_valid
        del self.total_list_valid
        if isinstance(self.parent, GLMixin):
            self.parent.invalidate_all_lists()


    #
    # Invalidation
    #

    def invalidate_draw_list(self):
        if self.gl_active and self.draw_list_valid:
            self.draw_list_valid = False
            context.application.main.drawing_area.queue_draw()
            context.application.scene.add_revalidation(self.revalidate_draw_list)
            self.emit("on-draw-list-invalidated")
            ##print "EMIT %s: on-draw-list-invalidated" % self.get_name()
            if isinstance(self.parent, GLMixin):
                self.parent.invalidate_boundingbox_list()


    def invalidate_boundingbox_list(self):
        ##print "TRY: %s: on-boundingbox-list-invalidated"  % self.get_name()
        if self.gl_active and self.boundingbox_list_valid:
            self.boundingbox_list_valid = False
            context.application.main.drawing_area.queue_draw()
            context.application.scene.add_revalidation(self.revalidate_boundingbox_list)
            self.emit("on-boundingbox-list-invalidated")
            ##print "EMIT %s: on-boundingbox-list-invalidated"  % self.get_name()
            if isinstance(self.parent, GLMixin):
                self.parent.invalidate_boundingbox_list()

    def invalidate_total_list(self):
        if self.gl_active and self.total_list_valid:
            self.total_list_valid = False
            context.application.main.drawing_area.queue_draw()
            context.application.scene.add_revalidation(self.revalidate_total_list)
            self.emit("on-total-list-invalidated")
            ##print "EMIT %s: on-total-list-invalidated" % self.get_name()
            if isinstance(self.parent, GLMixin):
                self.parent.invalidate_boundingbox_list()

    def invalidate_all_lists(self):
        self.invalidate_total_list()
        self.invalidate_boundingbox_list()
        self.invalidate_draw_list()

    #
    # Revalidation
    #

    def revalidate_draw_list(self):
        if self.gl_active:
            vb = context.application.vis_backend
            ##print "Compiling draw list (%i): %s" % (self.draw_list, self.get_name())
            vb.begin_list(self.draw_list)
            self.prepare_draw()
            self.draw()
            self.finish_draw()
            vb.end_list()
            self.draw_list_valid = True

    def revalidate_boundingbox_list(self):
        if self.gl_active:
            vb = context.application.vis_backend
            ##print "Compiling selection list (%i): %s" % (self.boundingbox_list, self.get_name())
            vb.begin_list(self.boundingbox_list)
            self.revalidate_bounding_box()
            self.bounding_box.draw()
            vb.end_list()
            self.boundingbox_list_valid = True

    def revalidate_bounding_box(self):
        self.bounding_box.clear()

    def revalidate_total_list(self):
        if self.gl_active:
            vb = context.application.vis_backend
            ##print "Compiling total list (%i): %s" % (self.total_list, self.get_name())
            vb.begin_list(self.total_list)
            if self.visible:
                vb.push_name(self.draw_list)
                self.draw_selection()
                vb.call_list(self.draw_list)
                vb.pop_name()
            vb.end_list()
            self.total_list_valid = True

    #
    # Draw
    #

    def draw_selection(self):
        vb = context.application.vis_backend
        if self.selected:
            vb.set_bright(True)
        else:
            vb.set_bright(False)

    def call_list(self):
        ##print "Executing total list (%i): %s" % (self.total_list, self.get_name())
        context.application.vis_backend.call_list(self.total_list)

    def prepare_draw(self):
        pass

    def draw(self):
        pass

    def finish_draw(self):
        pass

    #
    # Frame
    #

    def get_bounding_box_in_parent_frame(self):
        return self.bounding_box

    def get_absolute_frame(self):
        return self.get_absolute_parentframe()

    def get_absolute_parentframe(self):
        if not isinstance(self.parent, GLMixin):
            return Complete.identity()
        else:
            return self.parent.get_absolute_frame()

    def get_frame_up_to(self, upper_parent):
        if (upper_parent == self) or (self.parent == upper_parent):
            return Complete.identity()
        else:
            return self.get_parentframe_up_to(upper_parent)

    def get_parentframe_up_to(self, upper_parent):
        if not isinstance(self.parent, GLMixin):
            assert upper_parent is None, "upper_parent must be (an indirect) parent of self."
            return Complete.identity()
        elif self.parent == upper_parent:
            return Complete.identity()
        else:
            return self.parent.get_frame_up_to(upper_parent)

    def get_frame_relative_to(self, other):
        common = common_parent([self, other])
        return other.get_frame_up_to(common).inv * self.get_frame_up_to(common)

    #
    # Signal handlers
    #

    def on_select_changed(self, foo):
        self.invalidate_total_list()

gobject.signal_new("on-draw-list-invalidated", GLMixin, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
gobject.signal_new("on-boundingbox-list-invalidated", GLMixin, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
gobject.signal_new("on-total-list-invalidated", GLMixin, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())


class GLTransformationMixin(GLMixin):

    #
    # State
    #

    def initnonstate(self, Transformation):
        GLMixin.initnonstate(self)
        self.Transformation = Transformation

    #
    # Properties
    #

    def default_transformation(self):
        return self.Transformation.identity()

    def set_transformation(self, transformation, init=False):
        if not transformation.__class__ == self.Transformation:
            # create an object of the proper type and take only the attributes
            # of interest.
            if isinstance(transformation, Translation):
                t = transformation.t
            else:
                t = None
            if isinstance(transformation, Rotation):
                r = transformation.r
            else:
                r = None
            if self.Transformation == Translation:
                if t is None:
                    transformation = Translation.identity()
                else:
                    transformation = Translation(t)
            elif self.Transformation == Rotation:
                if r is None:
                    transformation = Rotation.identity()
                else:
                    transformation = Rotation(r)
            else: # self.Transformation == Complete:
                if r is None:
                    r = numpy.identity(3, float)
                if t is None:
                    t = numpy.zeros(3, float)
                transformation = Complete(r, t)
        self.transformation = transformation
        if not init:
            self.invalidate_transformation_list()

    properties = [
        Property("transformation", default_transformation, lambda self: self.transformation, set_transformation)
    ]

    #
    # Dialog fields (see action EditProperties)
    #

    dialog_fields = set([
        DialogFieldInfo("Transformation", (3, 0), fields.composed.Translation(
            label_text="Translation with vector t",
            attribute_name="transformation",
        )),
        DialogFieldInfo("Transformation", (3, 1), fields.composed.Rotation(
            label_text="Rotation around axis n",
            attribute_name="transformation",
        )),
        DialogFieldInfo("Transformation", (3, 2), fields.composed.Complete(
            label_text="The transformation is a rotation followed by a translation.",
            attribute_name="transformation",
        )),
        DialogFieldInfo("Transformation", (3, 3), fields.read.Handedness()),
    ])

    #
    # OpenGL
    #

    def initialize_gl(self):
        vb = context.application.vis_backend
        self.transformation_list = vb.create_list()
        ##print "Created transformation list (%i): %s" % (self.transformation_list, self.get_name())
        self.transformation_list_valid = True
        GLMixin.initialize_gl(self)

    def cleanup_gl(self):
        GLMixin.cleanup_gl(self)
        vb = context.application.vis_backend
        ##print "Deleting transformation list (%i): %s" % (self.transformation_list, self.get_name())
        vb.delete_list(self.transformation_list)
        del self.transformation_list
        del self.transformation_list_valid

    #
    # Invalidation
    #

    def invalidate_transformation_list(self):
        ##print "CALL %s: on-transformation-list-invalidated" % self.get_name()
        if self.gl_active and self.transformation_list_valid:
            self.transformation_list_valid = False
            context.application.main.drawing_area.queue_draw()
            context.application.scene.add_revalidation(self.revalidate_transformation_list)
            self.emit("on-transformation-list-invalidated")
            ##print "EMIT %s: on-transformation-list-invalidated" % self.get_name()
            if isinstance(self.parent, GLMixin):
                self.parent.invalidate_boundingbox_list()

    def invalidate_all_lists(self):
        self.invalidate_transformation_list()
        GLMixin.invalidate_all_lists(self)

    #
    # Revalidation
    #

    def revalidate_transformation_list(self):
        if self.gl_active:
            vb = context.application.vis_backend
            ##print "Compiling transformation list (%i): %s" % (self.transformation_list,  self.get_name())
            vb.begin_list(self.transformation_list)
            vb.transform(self.transformation)
            vb.end_list()
            self.transformation_list_valid = True

    def revalidate_total_list(self):
        if self.gl_active:
            vb = context.application.vis_backend
            ##print "Compiling total list (%i): %s" % (self.total_list, self.get_name())
            vb.begin_list(self.total_list)
            if self.visible:
                vb.push_name(self.draw_list)
                vb.push_matrix()
                vb.call_list(self.transformation_list)
                self.draw_selection()
                vb.call_list(self.draw_list)
                vb.pop_matrix()
                vb.pop_name()
            vb.end_list()
            self.total_list_valid = True

    #
    # Frame
    #

    def get_bounding_box_in_parent_frame(self):
        return self.bounding_box.transformed(self.transformation)

    def get_absolute_frame(self):
        if not isinstance(self.parent, GLMixin):
            return self.transformation
        else:
            return self.get_absolute_parentframe() * self.transformation

    def get_frame_up_to(self, upper_parent):
        if (upper_parent == self):
            return Complete.identity()
        elif (self.parent == upper_parent):
            return self.transformation
        else:
            return self.get_parentframe_up_to(upper_parent) * self.transformation

gobject.signal_new("on-transformation-list-invalidated", GLTransformationMixin, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())


