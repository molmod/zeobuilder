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
from zeobuilder.actions.composed import Interactive
from zeobuilder.actions.collections.interactive import InteractiveInfo, InteractiveGroup
from zeobuilder.nodes.model_object import ModelObject
from zeobuilder.nodes.glcontainermixin import GLContainerMixin
from zeobuilder.nodes.glmixin import GLTransformationMixin
from zeobuilder.nodes.analysis import common_parent
from zeobuilder.nodes.reference import TargetError
from zeobuilder.expressions import Expression
from zeobuilder.gui.glade_wrapper import GladeWrapper
from zeobuilder.gui.fields_dialogs import FieldsDialogSimple
from zeobuilder.gui import fields
from zeobuilder.gui.fields_dialogs import DialogFieldInfo
import zeobuilder.gui.fields as fields
import zeobuilder.actions.primitive as primitive
import zeobuilder.authors as authors

from molmod.transformations import Translation
from molmod.data.bonds import BOND_SINGLE, BOND_DOUBLE, BOND_TRIPLE, BOND_HYBRID, BOND_HYDROGEN
from molmod.data.periodic import periodic

import gtk, numpy


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
        GladeWrapper.__init__(self, "plugins/molecular/gui.glade", "wi_sketch", "window")
        self.window.hide()
        self.init_callbacks(self.__class__)
        self.init_proxies([
            "cb_object",
            "cb_vector",
            "cb_erase_filter",
            "bu_edit_erase_filter",
            "la_current",
            "bu_set_atom",
            "cb_bondtype",
            "hbox_atoms",
            "hbox_quickpicks"
        ])

        self.erase_filter = Expression("True")
        #Initialize atom number - this can be changed anytime with the edit_atom_number dialog
        self.atom_number = 6;

        # Initialize the GUI
        #  1) common parts of the comboboxes
        def render_icon(column, cell, model, iter):
            cell.set_property(
                "pixbuf",
                context.application.plugins.get_node(model.get_value(iter, 0)).icon
            )

        #  2) fill the objects combo box
        self.object_store = gtk.ListStore(str)
        self.object_store.append(["Atom"])
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
        self.vector_store.append(["Bond"])
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

        # 4) fill the bond type combo box
        self.bondtype_store = gtk.ListStore(str,int)
        self.bondtype_store.append(["Single bond",BOND_SINGLE])
        self.bondtype_store.append(["Double bond",BOND_DOUBLE])
        self.bondtype_store.append(["Triple bond",BOND_TRIPLE])
        self.bondtype_store.append(["Hybrid bond",BOND_HYBRID])
        self.bondtype_store.append(["Hydrogen bond",BOND_HYDROGEN])
        self.cb_bondtype.set_model(self.bondtype_store)

        #no icons like the others, just text here
        renderer_text = gtk.CellRendererText()
        self.cb_bondtype.pack_start(renderer_text, expand=True)
        self.cb_bondtype.add_attribute(renderer_text, "text", 0)

        self.cb_bondtype.set_active(0)

        # register quick pick config setting
        config = context.application.configuration
        config.register_setting(
            "sketch_quickpicks",
            [6,7,8,9,10,11],
        )

        # 5)create the "quick pick" atom buttons
        for index in xrange(len(config.sketch_quickpicks)):
            atomnumber = config.sketch_quickpicks[index]
            bu_element = gtk.Button("")
            bu_element.set_label("%s" % periodic[atomnumber].symbol)
            bu_element.connect("clicked", self.on_bu_element_clicked, index)
            # add to hbox
            self.hbox_quickpicks.pack_start(bu_element)
            bu_element.show()

    def on_window_delete_event(self, window, event):
        return True

    def on_bu_edit_erase_filter_clicked(self, button):
        self.edit_erase_filter.run(self)

    def on_bu_set_atom_clicked(self, button):
        self.edit_atom_number = FieldsDialogSimple(
            "Select atom number",
            fields.edit.Element(attribute_name="atom_number"),
            ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK))
        )
        self.edit_atom_number.run(self)
        atom_symbol = periodic[self.atom_number].symbol
        self.la_current.set_label("Current: %s " % str(atom_symbol))

    def on_cb_object_changed(self, combo):
        # When the selected object is an atom, show the extra button.
        self.hbox_atoms.hide()
        self.la_current.hide()
        if(self.object_store.get_value(self.cb_object.get_active_iter(),0)=="Atom"):
            self.hbox_atoms.show()
            self.la_current.show()

    def on_bu_element_clicked(self, widget, index):
        self.atom_number = context.application.configuration.sketch_quickpicks[index]
        atom_symbol = periodic[self.atom_number].symbol
        self.la_current.set_label("Current: %s" % str(atom_symbol))

    def on_cb_vector_changed(self, combo):
        # When the selected object is an atom, show the extra button.
        if (self.vector_store.get_value(self.cb_vector.get_active_iter(),0)=="Bond"):
            self.cb_bondtype.show()
        else:
            self.cb_bondtype.hide()

    def get_new(self, state={}):
        object_type = self.object_store.get_value(self.cb_object.get_active_iter(), 0)

        new = context.application.plugins.get_node(object_type)()
        #if it's an 'Atom', set the atom number to the current atom number?
        if object_type == "Atom":
            new.set_number(self.atom_number)
            new.set_name(periodic[self.atom_number].symbol)
        return new

    def add_new(self, position, parent):
        new = self.get_new()
        new.transformation.t[:] = position
        primitive.Add(new, parent)
        return new

    def replace(self, gl_object):
        if not gl_object.get_fixed():
            state = gl_object.__getstate__()
            state.pop("name", None)
            state.pop("transformation", None)
            new = self.get_new(state)
            new.transformation.t[:] = gl_object.transformation.t
            for reference in gl_object.references[::-1]:
                if not reference.check_target(new):
                    return
            parent = gl_object.parent
            primitive.Add(new, parent)
            for reference in gl_object.references[::-1]:
                reference.set_target(new)
            primitive.Delete(gl_object)

    def connect(self, gl_object1, gl_object2):
        try:
            new = context.application.plugins.get_node(
                self.vector_store.get_value(self.cb_vector.get_active_iter(), 0)
            )(targets=[gl_object1, gl_object2])
        except TargetError:
            return

        if(self.vector_store.get_value(self.cb_vector.get_active_iter(), 0)=="Bond"):
            new.set_bond_type(self.bondtype_store.get_value(self.cb_bondtype.get_active_iter(),1))

        primitive.Add(new, common_parent([gl_object1.parent, gl_object2.parent]))

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
    interactive_info = InteractiveInfo("plugins/molecular/sketch.svg", mouse=True)
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
    "sketch": SketchInteractiveGroup(
        image_name="plugins/molecular/sketch.svg",
        description="Sketch tool",
        order=7,
        authors=[authors.toon_verstraelen],
    )
}


