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

from elementary import Group, TabulateComposed
from mixin import EditMixin, ambiguous, insensitive

import gtk

__all__ = ["Table", "Notebook"]


NO_BUTTONS = 0
CHECK_BUTTONS = 1
RADIO_BUTTONS = 2


class Table(Group):
    def __init__(self, fields, label_text=None, buttons=NO_BUTTONS):
        Group.__init__(self, fields, label_text)
        self.buttons = buttons

    def create_widgets(self):
        Group.create_widgets(self)
        last_row = 0
        first_edit = 0
        if self.buttons == NO_BUTTONS:
            self.data_widget = gtk.Table(1, 3)
        else:
            self.data_widget = gtk.Table(1, 4)
            first_edit += 1
        self.data_widget.set_row_spacings(6)
        self.data_widget.set_col_spacings(6)

        first_radio_button = None

        for field in self.fields:
            if field.get_active():
                data_widget_left = first_edit
                data_widget_right = first_edit + 3
                if field.high_widget:
                    self.data_widget.set_row_spacings(12)
                    container = field.get_widgets_short_container()
                    container.set_border_width(0)
                    self.data_widget.attach(
                        container,
                        data_widget_left, data_widget_right,
                        last_row, last_row+1,
                        xoptions=gtk.EXPAND|gtk.FILL, yoptions=0
                    )
                else:
                    label, data_widget, bu_popup = field.get_widgets_separate()
                    if label is not None:
                        self.data_widget.attach(label, first_edit, first_edit+1, last_row, last_row+1, xoptions=gtk.FILL, yoptions=0)
                        data_widget_left += 1
                    if bu_popup is not None:
                        self.data_widget.attach(field.bu_popup, first_edit+2, first_edit+3, last_row, last_row+1, xoptions=0, yoptions=0)
                        data_widget_right -= 1
                    self.data_widget.attach(field.data_widget, data_widget_left, data_widget_right, last_row, last_row+1, xoptions=gtk.EXPAND|gtk.FILL, yoptions=0)

                if self.buttons == CHECK_BUTTONS:
                    toggle_button = gtk.CheckButton()
                elif self.buttons == RADIO_BUTTONS:
                    if first_radio_button is None:
                        toggle_button = gtk.RadioButton()
                        first_radio_button = toggle_button
                    else:
                        toggle_button = gtk.RadioButton(first_radio_button)
                if self.buttons != NO_BUTTONS:
                    self.data_widget.attach(toggle_button, 0, 1, last_row, last_row+1, xoptions=gtk.FILL, yoptions=gtk.FILL)
                    field.old_representation = ambiguous
                    field.sensitive_button = toggle_button
                    toggle_button.connect("toggled", self.on_button_toggled, field)
                last_row += 1

    def destroy_widgets(self):
        if self.buttons != NO_BUTTONS:
            for field in self.fields:
                if field.get_active():
                    field.sensitive_button.destroy()
                    field.sensitive_button = None

    def read(self):
        Group.read(self)
        if self.buttons != NO_BUTTONS and self.get_active():
            for field in self.fields:
                if field.get_active():
                    field.sensitive_button.set_active(field.read_from_widget() != insensitive)

    def on_button_toggled(self, toggle_button, field):
        if toggle_button.get_active():
            #print "making sensitive"
            #print "  current_representation =", field.read_from_widget()
            if field.read_from_widget() == insensitive:
                #print "  resetting to old_representation =", field.old_representation
                field.write_to_widget(field.old_representation)
        else:
            #print "making insensitive"
            old_representation = field.read_from_widget()
            #print "  old_representation =", old_representation
            if old_representation != insensitive:
                #print "  saving old_representation"
                field.old_representation = field.read_from_widget()
            #print "  setting representation = %s" % insensitive
            field.write_to_widget(insensitive)


class HBox(Group):
    def __init__(self, fields, label_text=None):
        Group.__init__(self, fields, label_text)

    def create_widgets(self):
        Group.create_widgets(self)
        self.data_widget = gtk.HBox()
        self.data_widget.set_spacing(6)
        for field in self.fields:
            if field.get_active():
                self.data_widget.pack_start(field.get_widgets_short_container())


class Notebook(Group):
    def __init__(self, named_fields, label_text=None):
        Group.__init__(self, [field for (name, field) in named_fields], label_text)
        self.named_fields = named_fields

    def create_widgets(self):
        Group.create_widgets(self)
        self.data_widget = gtk.Notebook()
        for name, field in self.named_fields:
            if field.get_active():
                self.data_widget.append_page(
                    field.get_widgets_short_container(),
                    gtk.Label(name)
                )
                field.container.set_border_width(12)

    def show(self, field):
        Group.show(self, field)
        self.data_widget.set_current_page(self.data_widget.page_num(field.container))
