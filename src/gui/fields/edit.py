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


from elementary import Edit
from mixin import ambiguous, insensitive
from molmod.data import periodic
from zeobuilder.conversion import express_measure
import popups

import gtk, gobject, numpy

import StringIO


__all__ = ["CheckButton", "ComboBox", "Element", "TextView", "Color"]


class CheckButton(Edit):
    Popup = popups.Default

    def create_widgets(self):
        Edit.create_widgets(self)
        self.check_button = gtk.CheckButton()
        self.check_button.connect("toggled", self.on_widget_changed)
        self.check_button.connect("clicked", self.on_cb_clicked)
        self.check_button.add(self.label)
        self.data_widget = self.check_button

    def destroy_widgets(self):
        self.check_button = None
        Edit.destroy_widgets(self)

    def get_widgets_separate(self):
        assert self.data_widget is not None
        return None, self.data_widget, self.bu_popup

    def read_from_widget(self):
        if not self.check_button.get_property("sensitive"):
            return insensitive
        if self.check_button.get_inconsistent():
            return ambiguous
        else:
            return self.check_button.get_active()

    def write_to_widget(self, representation, original=False):
        if representation == insensitive:
            self.check_button.set_active(False)
            self.check_button.set_inconsistent(True)
            self.check_button.set_sensitive(False)
        else:
            self.check_button.set_sensitive(True)
            if representation == ambiguous:
                self.check_button.set_active(False)
                self.check_button.set_inconsistent(True)
            else:
                self.check_button.set_inconsistent(False)
                self.check_button.set_active(representation)
        Edit.write_to_widget(self, representation, original)

    def on_cb_clicked(self, widget):
        self.check_button.set_inconsistent(False)
        self.on_widget_changed(widget)


class ComboBox(Edit):
    Popup = popups.Default

    def __init__(self, choices, label_text=None, attribute_name=None, show_popup=True, history_name=None):
        Edit.__init__(self, label_text, attribute_name, show_popup, history_name)
        self.choices = choices
        self.paths = {}

    def create_widgets(self):
        Edit.create_widgets(self)
        # create a model
        self.combo_model = gtk.ListStore(gobject.TYPE_PYOBJECT, gobject.TYPE_STRING)
        self.combo_box = gtk.ComboBox(self.combo_model)
        text_cell_renderer = gtk.CellRendererText()
        self.combo_box.pack_start(text_cell_renderer)
        self.combo_box.add_attribute(text_cell_renderer, "text", 1)
        self.combo_box.connect('changed', self.on_widget_changed)
        self.data_widget = self.combo_box
        self.can_ambiguous = False
        for value, label in self.choices:
            iter = self.combo_model.append([value, label])
            self.paths[value] = self.combo_model.get_path(iter)

    def destroy_widgets(self):
        self.combo_box = None
        self.paths = {}
        self.combo_model = None
        Edit.destroy_widgets(self)

    def write_to_widget(self, representation, original=False):
        if representation == insensitive:
            self.combo_box.set_sensitive(False)
        else:
            self.combo_box.set_sensitive(True)
            if representation == ambiguous:
                iter = self.combo_model.get_iter_first()
            else:
                iter = self.combo_model.get_iter(representation)
            self.combo_box.set_active_iter(iter)
        Edit.write_to_widget(self, representation, original)

    def convert_to_representation(self, value):
        return self.paths.get(value)

    def read_from_widget(self):
        if not self.combo_box.get_property("sensitive"):
            return insensitive
        else:
            iter = self.combo_box.get_active_iter()
            if iter is None:
                return ambiguous
            representation = self.combo_model.get_path(iter)
            if self.can_ambiguous and representation == self.combo_model.get_path(self.combo_model.get_iter_first()):
                return ambiguous
            else:
                return representation

    def convert_to_value(self, representation):
        return self.combo_model.get_value(self.combo_model.get_iter(representation), 0)

    def set_ambiguous_capability(self, can_ambiguous):
        if self.can_ambiguous and not can_ambiguous:
            self.can_ambiguous = False
            self.combo_model.remove(self.combo_model.get_iter_first())
        elif not self.can_ambiguous and can_ambiguous:
            self.can_ambiguous = True
            self.combo_model.prepend([ambiguous, str(ambiguous)])


class List(Edit):
    Popup = popups.Default
    high_widget = True

    def __init__(self, columns, label_text=None, attribute_name=None, show_popup=True, history_name=None):
        Edit.__init__(self, label_text, attribute_name, show_popup, history_name)
        self.columns = columns
        self.paths = {}
        self.records = []

    def create_widgets(self):
        Edit.create_widgets(self)
        # create a model
        self.list_store = gtk.ListStore(gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT)
        self.list_view = gtk.TreeView(self.list_store)
        self.list_selection = self.list_view.get_selection()

        for index, (column_title, column_attribute) in enumerate(self.columns):
            text_cell_renderer = gtk.CellRendererText()
            column = gtk.TreeViewColumn(column_title, text_cell_renderer)
            def data_func(column, cell, model, iter, i):
                cell.set_property("text", model.get_value(iter, 1)[i])
            column.set_cell_data_func(text_cell_renderer, data_func, index)
            self.list_view.append_column(column)

        self.data_widget = gtk.ScrolledWindow()
        self.data_widget.set_shadow_type(gtk.SHADOW_IN)
        self.data_widget.add(self.list_view)
        self.data_widget.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.data_widget.set_size_request(-1, 250)
        self.can_ambiguous = False
        self.list_selection.connect('changed', self.on_widget_changed)

        for record in self.records:
            value = record.__dict__[self.attribute_name]
            iter = self.list_store.append([
                value,
                [
                    record.__dict__[column_attribute]
                    for column_title, column_attribute
                    in self.columns
                ]
            ])
            self.paths[id(value)] = self.list_store.get_path(iter)

    def destroy_widgets(self):
        self.list_view = None
        self.paths = {}
        self.list_store = None
        Edit.destroy_widgets(self)

    def write_to_widget(self, representation, original=False):
        if representation == insensitive:
            self.list_view.set_sensitive(False)
        else:
            self.list_view.set_sensitive(True)
            if representation == ambiguous:
                iter = self.list_store.get_iter_first()
            else:
                iter = self.list_store.get_iter(representation)
            self.list_selection.select_iter(iter)
        Edit.write_to_widget(self, representation, original)

    def convert_to_representation(self, value):
        return self.paths.get(id(value))

    def read_from_widget(self):
        if not self.list_view.get_property("sensitive"):
            return insensitive
        else:
            model, iter = self.list_selection.get_selected()
            if iter is None:
                return ambiguous
            representation = self.list_store.get_path(iter)
            if self.can_ambiguous and representation == self.list_store.get_path(self.list_store.get_iter_first()):
                return ambiguous
            else:
                return representation

    def convert_to_value(self, representation):
        return self.list_store.get_value(self.list_store.get_iter(representation), 0)

    def set_ambiguous_capability(self, can_ambiguous):
        if self.can_ambiguous and not can_ambiguous:
            self.can_ambiguous = False
            self.list_store.remove(self.list_store.get_iter_first())
        elif not self.can_ambiguous and can_ambiguous:
            self.can_ambiguous = True
            self.list_store.prepend([str(ambiguous)] + [" "] * (len(self.fields)-1) + [ambiguous])


class Element(Edit):
    Popup = popups.Element
    high_widget = True

    mendeljev_labels = [(1, 0, "1"), (2, 1, "2"), (3, 3, "3"), (4, 3, "4"), (5, 3, "5"),  (6, 3, "6"),
                        (7, 3, "7"), (8, 3, "8"), (9, 3, "9"), (10, 3, "10"), (11, 3, "11"),  (12, 3, "12"),
                        (13, 1, "13"), (14, 1, "14"), (15, 1, "15"), (16, 1, "16"), (17, 1, "17"),  (18, 0, "18"),
                        (0, 1, "K"), (0, 2, "L"), (0, 3, "M"), (0, 4, "N"), (0, 5, "O"),  (0, 6, "P"),
                        (0, 7, "Q"), (3, 9, "P"), (3, 10, "Q")]

    def __init__(self, label_text=None, attribute_name=None, show_popup=True, history_name=None):
        Edit.__init__(self, label_text, attribute_name, show_popup, history_name)

    def create_widgets(self):
        Edit.create_widgets(self)
        to_mendeljev = gtk.Tooltips()
        self.buttons = {}
        ta_elements = gtk.Table(11, 19, homogeneous=True)
        ta_elements.set_row_spacings(0)
        ta_elements.set_col_spacings(0)
        # Use periodic to fill the table with buttons.
        for atom_info in periodic.atoms_by_number.itervalues():
            bu_element = gtk.ToggleButton("")
            bu_element.set_property("can-focus", False)
            label = bu_element.get_child()
            label.set_label("<small>%s</small>" % atom_info.symbol)
            label.set_use_markup(True)
            bu_element.connect("toggled", self.on_bu_element_toggled, atom_info.number)
            bu_element.connect("toggled", self.on_widget_changed)
            tip = str(atom_info.number) + ": " + atom_info.name
            if atom_info.mass is not None:
                if atom_info.artificial:
                    tip = tip + "\nMass = *%s" % express_measure(atom_info.mass, measure="Mass")
                else:
                    tip = tip + "\nMass = %s" % express_measure(atom_info.mass, measure="Mass")
            if atom_info.radius is not None:
                tip = tip + "\nRadius = " + express_measure(atom_info.radius, "Length")
            to_mendeljev.set_tip(bu_element, tip)
            ta_elements.attach(
                bu_element,
                int(atom_info.col), int(atom_info.col) + 1,
                int(atom_info.row), int(atom_info.row) + 1
            )
            self.buttons[atom_info.number] = bu_element
        # also add a few indicative labels
        for c, r, label_text in self.mendeljev_labels:
            indicative = gtk.Label("<b><small>" + label_text + "</small></b>")
            indicative.set_use_markup(True)
            ta_elements.attach(indicative, c, c+1, r, r+1)

        self.bu_former = None
        self.data_widget = ta_elements

    def destroy_widgets(self):
        self.buttons = None
        self.bu_former = None
        Edit.destroy_widgets(self)

    def on_bu_element_toggled(self, widget, number):
        if widget.get_active() == True:
            if (self.bu_former != widget) and (self.bu_former is not None):
                # Put out the former bu_element
                temp = self.bu_former
                self.bu_former = widget
                temp.set_active(False)
            self.number = number
        else:
            if self.bu_former == widget:
                widget.set_active(True)

    def write_to_widget(self, representation, original=False):
        self.number = None
        self.bu_former = None
        if representation == insensitive:
            for bu in self.buttons.itervalues():
                bu.set_sensitive(False)
        else:
            for bu in self.buttons.itervalues():
                bu.set_sensitive(True)
                bu.set_active(False)
            self.bu_former = self.buttons[representation]
            if representation in self.buttons.keys():
                self.buttons[representation].set_active(True)
        Edit.write_to_widget(self, representation, original)

    def read_from_widget(self):
        if self.number is None:
            return insensitive
        else:
            return self.number


class TextView(Edit):
    Popup = popups.Default
    high_widget = True

    def __init__(self, label_text=None, attribute_name=None, show_popup=True, history_name=None, line_breaks=False):
        Edit.__init__(self, label_text, attribute_name, show_popup, history_name)
        self.line_breaks = line_breaks
        self.attribute_is_stream = False

    def create_widgets(self):
        Edit.create_widgets(self)
        self.text_view = gtk.TextView()
        self.text_buffer = self.text_view.get_buffer()
        self.text_buffer.connect("changed", self.on_widget_changed)
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_shadow_type(gtk.SHADOW_IN)
        scrolled_window.set_shadow_type(gtk.SHADOW_IN)
        scrolled_window.set_size_request(350, 250)
        scrolled_window.add(self.text_view)
        self.data_widget = scrolled_window

    def destroy_widgets(self):
        self.textview = None
        Edit.destroy_widgets(self)

    def convert_to_representation(self, value):
        if isinstance(value, StringIO.StringIO):
            self.attribute_is_stream = True
            return value.getvalue()
        else:
            self.attribute_is_stream = False
            return value

    def write_to_widget(self, representation, original=False):
        if representation == insensitive:
            self.text_view.set_sensitive(False)
        else:
            self.text_view.set_sensitive(True)
            if representation == ambiguous: representation = ""
            self.text_buffer.set_text(representation)
        Edit.write_to_widget(self, representation, original)

    def convert_to_value(self, representation):
        if self.attribute_is_stream:
            return StringIO.StringIO(representation)
        else:
            return representation

    def read_from_widget(self):
        if not self.text_view.get_property("sensitive"):
            return insensitive
        else:
            start, end = self.text_buffer.get_bounds()
            representation = self.text_buffer.get_slice(start, end)
            if not self.line_breaks:
                representation = representation.replace("\n", " ")
            if representation == "":
                return ambiguous
            else:
                return representation


class Color(Edit):
    Popup = popups.Default

    def create_widgets(self):
        Edit.create_widgets(self)
        self.color_button = gtk.ColorButton()
        self.color_button.connect("color-set", self.on_widget_changed)
        self.color_child = self.color_button.get_child()
        self.ambiguous_label = gtk.Label(str(ambiguous))
        self.ambiguous_label.show_all()
        self.data_widget = self.color_button

    def destroy_widgets(self):
        self.color_button = None
        Edit.destroy_widgets(self)

    def convert_to_representation(self, value):
        return tuple((value[0:3]*66535).astype(int))

    def write_to_widget(self, representation, original=False):
        if representation == insensitive:
            self.color_button.set_sensitive(False)
        else:
            self.color_button.set_sensitive(True)
            self.color_button.remove(self.color_button.get_child())
            if representation == ambiguous:
                self.color_button.add(self.ambiguous_label)
            else:
                self.color_button.add(self.color_child)
                self.color_button.set_color(gtk.gdk.Color(*representation))
        Edit.write_to_widget(self, representation, original)

    def convert_to_value(self, representation):
        result = numpy.array(representation + (1.0,), float)
        result[0:3] /= 66535
        return result

    def read_from_widget(self):
        if not self.color_button.get_property("sensitive"):
            return insensitive
        else:
            if self.color_button.get_child() == self.ambiguous_label:
                return ambiguous
            else:
                tmp = self.color_button.get_color()
                return (tmp.red, tmp.green, tmp.blue)

    def on_widget_changed(self, widget):
        Edit.on_widget_changed(self, widget)
        self.color_button.remove(self.color_button.get_child())
        self.color_button.add(self.color_child)

