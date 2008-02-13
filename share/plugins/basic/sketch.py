# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 Toon Verstraelen <Toon.Verstraelen@UGent.be>
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
from zeobuilder.actions.composed import Interactive
from zeobuilder.actions.collections.interactive import InteractiveInfo, InteractiveGroup
from zeobuilder.nodes.model_object import ModelObject
from zeobuilder.nodes.glcontainermixin import GLContainerMixin
from zeobuilder.nodes.glmixin import GLTransformationMixin
from zeobuilder.nodes.vector import Vector
from zeobuilder.nodes.analysis import common_parent
from zeobuilder.expressions import Expression
from zeobuilder.gui.glade_wrapper import GladeWrapper
from zeobuilder.gui.fields_dialogs import FieldsDialogSimple
import zeobuilder.gui.fields as fields
import zeobuilder.actions.primitive as primitive
import zeobuilder.authors as authors

from molmod.transformations import Translation

import gtk, numpy


ERASE_RECTANGLE = 0
ERASE_ELLIPSE = 1
ERASE_LINE = 2


class SketchOptions(GladeWrapper):
    edit_erase_filter = FieldsDialogSimple(
        "Edit the Erase filter",
        fields.faulty.Expression(
            label_text="Erase filter expression",
            attribute_name="erase_filter",
            show_popup=True,
            history_name="filter",
        ),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK))
    )

    def __init__(self):
        GladeWrapper.__init__(self, "plugins/basic/gui.glade", "wi_sketch", "window")
        self.window.hide()
        self.init_callbacks(self.__class__)
        self.init_proxies([
            "cb_object", "cb_vector", "cb_erase_filter", "bu_edit_erase_filter",
        ])

        self.erase_filter = Expression("True")

        # Initialize the GUI
        #  1) common parts of the comboboxes
        def render_icon(column, cell, model, iter):
            cell.set_property(
                "pixbuf",
                context.application.plugins.get_node(model.get_value(iter, 0)).icon
            )

        #  2) fill the objects combo box
        self.object_store = gtk.ListStore(str)
        self.object_store.append(["Point"])
        self.object_store.append(["Sphere"])
        self.object_store.append(["Box"])
        self.cb_object.set_model(self.object_store)

        renderer_pixbuf = gtk.CellRendererPixbuf()
        self.cb_object.pack_start(renderer_pixbuf, expand=False)
        self.cb_object.set_cell_data_func(renderer_pixbuf, render_icon)
        renderer_text = gtk.CellRendererText()
        self.cb_object.pack_start(renderer_text, expand=True)
        self.cb_object.add_attribute(renderer_text, "text", 0)

        self.cb_object.set_active(0)

        #  3) fill the vector combo box
        self.vector_store = gtk.ListStore(str)
        self.vector_store.append(["Arrow"])
        self.vector_store.append(["Spring"])
        self.cb_vector.set_model(self.vector_store)

        renderer_pixbuf = gtk.CellRendererPixbuf()
        self.cb_vector.pack_start(renderer_pixbuf, expand=False)
        self.cb_vector.set_cell_data_func(renderer_pixbuf, render_icon)
        renderer_text = gtk.CellRendererText()
        self.cb_vector.pack_start(renderer_text, expand=True)
        self.cb_vector.add_attribute(renderer_text, "text", 0)

        self.cb_vector.set_active(0)

    def on_window_delete_event(self, window, event):
        return True

    def on_bu_edit_erase_filter_clicked(self, button):
        self.edit_erase_filter.run(self)

    def add_new(self, position, parent):
        new = context.application.plugins.get_node(
            self.object_store.get_value(self.cb_object.get_active_iter(), 0)
        )()
        new.transformation.t[:] = position
        primitive.Add(new, parent, select=False)
        return new

    def replace(self, gl_object):
        if not gl_object.get_fixed():
            state = gl_object.__getstate__()
            state.pop("name", None)
            state.pop("transformation", None)
            new = context.application.plugins.get_node(
                self.object_store.get_value(self.cb_object.get_active_iter(), 0)
            )(**state)
            new.transformation.t[:] = gl_object.transformation.t
            for reference in gl_object.references[::-1]:
                if not reference.check_target(new):
                    return
            parent = gl_object.parent
            primitive.Add(new, parent, select=False)
            for reference in gl_object.references[::-1]:
                reference.set_target(new)
            primitive.Delete(gl_object)

    def connect(self, gl_object1, gl_object2):
        new = context.application.plugins.get_node(
            self.vector_store.get_value(self.cb_vector.get_active_iter(), 0)
        )(targets=[gl_object1, gl_object2])
        primitive.Add(
            new,
            common_parent([gl_object1.parent, gl_object2.parent]),
            select=False
        )

    def erase_at(self, p, parent):
        for node in context.application.main.drawing_area.yield_hits((p[0]-2, p[1]-2, p[0]+2, p[1]+2)):
            try:
                match = (
                    node is not None and node != parent and
                    node.is_indirect_child_of(parent) and
                    node.model == context.application.model and (
                        not self.cb_erase_filter.get_active() or
                        self.erase_filter(node)
                    )
                )
            except Exception:
                raise UserError("An exception occured while evaluating the erase filter expression.")
            if match:
                primitive.Delete(node)

    def tool_draw(self, p1, p2):
        drawing_area = context.application.main.drawing_area
        r1 = drawing_area.screen_to_camera(p1)
        r2 = drawing_area.screen_to_camera(p2)
        context.application.vis_backend.tool("line", r1, r2)

    def tool_special(self, p1, p2):
        pass

    def move_special(self, gl_object1, gl_object2, p1, p2):
        pass

    def click_special(self, gl_object):
        pass


class Sketch(Interactive):
    description = "Sketch objects and connectors"
    interactive_info = InteractiveInfo("plugins/basic/geom_sketch.svg", mouse=True)
    authors = [authors.toon_verstraelen]

    options = SketchOptions()

    def hit_criterion(self, gl_object):
        return (
            isinstance(gl_object, GLTransformationMixin) and
            isinstance(gl_object.transformation, Translation)
        )

    def button_press(self, drawing_area, event):
        camera = context.application.camera
        self.first_hit = drawing_area.get_nearest(event.x, event.y)
        if not self.hit_criterion(self.first_hit):
            self.first_hit = None

        if self.first_hit is not None:
            tmp = camera.object_to_camera(self.first_hit)
            self.begin = drawing_area.camera_to_screen(tmp).astype(float)
            self.parent = self.first_hit.parent
        else:
            self.begin = numpy.array([event.x, event.y], float)
            node = context.application.cache.node
            if isinstance(node, GLContainerMixin):
                self.parent = node
            elif isinstance(node, ModelObject) and isinstance(node.parent, GLContainerMixin):
                self.parent = node.parent
            else:
                self.parent = None

        if self.parent is None:
            self.parent = context.application.model.universe
        if self.first_hit is None:
            self.origin = self.parent.get_absolute_frame().t
        else:
            self.origin = self.first_hit.get_absolute_frame().t
        self.end = numpy.array([event.x, event.y], float)

        if event.button == 1:
            self.first_added = (self.first_hit is None)
            if self.first_added:
                self.first_hit = self.options.add_new(
                    self.parent.get_absolute_frame().vector_apply_inverse(
                        camera.vector_in_plane(
                            drawing_area.screen_to_camera(
                                numpy.array([event.x, event.y], float)
                            ),
                            self.origin,
                        )
                    ),
                    self.parent
                )
            self.tool = self.options.tool_draw
        elif event.button == 2 and self.first_hit is not None:
            self.tool = self.options.tool_special
            # a special modification of the selected object is going to happen
        elif event.button == 3:
            self.tool = self.options.erase_at
            self.tool(numpy.array([event.x, event.y], float), self.parent)

        if self.tool is None:
            self.finish()

    def button_motion(self, drawing_area, event, start_button):
        if self.tool == self.options.erase_at:
            self.tool(numpy.array([event.x, event.y], float), self.parent)
        else:
            self.end = numpy.array([event.x, event.y], float)
            self.tool(self.begin, self.end)

    def button_release(self, drawing_area, event):
        camera = context.application.camera
        context.application.vis_backend.tool("clear")
        self.end = numpy.array([event.x, event.y], float)

        if self.tool == self.options.erase_at:
            self.tool(numpy.array([event.x, event.y], float), self.parent)
            self.finish()
            return

        self.last_hit = drawing_area.get_nearest(event.x, event.y)
        if not self.hit_criterion(self.last_hit):
            self.last_hit = None
        moved = (
            (abs(self.begin - self.end) > 2).any()
        ) and (
            ((self.first_hit is None) and (self.last_hit is None)) or
            (self.first_hit != self.last_hit)
        )

        if moved:
            if self.tool == self.options.tool_draw:
                if self.last_hit is None:
                    self.last_hit = self.options.add_new(
                        self.parent.get_absolute_frame().vector_apply_inverse(
                            camera.vector_in_plane(
                                drawing_area.screen_to_camera(
                                    numpy.array([event.x, event.y], float)
                                ),
                                self.origin
                            )
                        ),
                        self.parent
                    )
                self.options.connect(self.first_hit, self.last_hit)
            elif self.tool == self.options.tool_special:
                self.options.move_special(self.first_hit, self.last_hit, self.begin, self.end)
        else:
            if self.tool == self.options.tool_draw and not self.first_added:
                self.options.replace(self.first_hit)
            elif self.tool == self.options.tool_special:
                self.options.click_special(self.first_hit)

        self.finish()


actions = {
    "Sketch": Sketch
}


class SketchInteractiveGroup(InteractiveGroup):
    def activate(self):
        InteractiveGroup.activate(self)
        Sketch.options.window.show()

    def deactivate(self):
        InteractiveGroup.deactivate(self)
        Sketch.options.window.hide()


interactive_groups = {
    "geom_sketch": SketchInteractiveGroup(
        image_name="plugins/basic/geom_sketch.svg",
        description="Geometric sketch tool",
        order=6,
        authors=[authors.toon_verstraelen],
    )
}



