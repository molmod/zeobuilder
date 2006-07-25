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

from elementary import Group
from mixin import EditMixin, ambiguous, insensitive

import gtk

__all__ = ["Table", "Notebook"]


NO_BUTTONS = 0
CHECK_BUTTONS = 1
RADIO_BUTTONS = 2


class Table(Group):
    self_containing = True

    def __init__(self, fields, label_text=None, table_border_width=6, buttons=NO_BUTTONS):
        Group.__init__(self, fields, label_text)
        self.table_border_width = table_border_width
        self.buttons = buttons

    def create_widgets(self):
        Group.create_widgets(self)
        self.container = gtk.Table(1, 3)
        self.container.set_row_spacings(6)
        self.container.set_col_spacings(6)
        self.container.set_border_width(self.table_border_width)
        last_row = 0
        first_edit = 0
        if self.label is not None:
            self.container.resize(1, self.container.get_property("n-columns")+1)
            self.container.attach(self.label, 0, 3, 0, 1, xoptions=gtk.FILL, yoptions=0)
            first_edit += 1
            last_row += 1
        if self.buttons != NO_BUTTONS:
            self.container.resize(1, self.container.get_property("n-columns")+1)
            first_edit += 1
        first_radio_button = None
        for field in self.fields:
            if field.get_active():
                self.container.resize(last_row + 1, 3)
                container_left = first_edit
                container_right = first_edit + 3
                if not field.self_containing:
                    if field.label is not None:
                        self.container.attach(field.label, first_edit, first_edit+1, last_row, last_row+1, xoptions=gtk.FILL, yoptions=0)
                        container_left += 1
                    if isinstance(field, EditMixin) and field.bu_popup is not None:
                        container_right -= 1
                        self.container.attach(field.bu_popup, first_edit+2, first_edit+3, last_row, last_row+1, xoptions=0, yoptions=0)
                self.container.attach(field.container, container_left, container_right, last_row, last_row+1, xoptions=field.xoptions, yoptions=field.yoptions)
                if self.buttons == CHECK_BUTTONS:
                    toggle_button = gtk.CheckButton()
                elif self.buttons == RADIO_BUTTONS:
                    if first_radio_button is None:
                        toggle_button = gtk.RadioButton()
                        first_radio_button = toggle_button
                    else:
                        toggle_button = gtk.RadioButton(first_radio_button)
                if self.buttons != NO_BUTTONS:
                    self.container.attach(toggle_button, first_edit-1, first_edit, last_row, last_row+1, xoptions=gtk.FILL, yoptions=gtk.FILL)
                    field.old_representation = ambiguous
                    field.sensitive_button = toggle_button
                    toggle_button.connect("toggled", self.on_button_toggled, field)
                last_row += 1
        if self.label is not None:
            da = gtk.DrawingArea()
            da.set_size_request(10, 0)
            self.container.attach(da, 0, 1, 1, last_row+1, xoptions=0)

    def read(self, instance=None):
        Group.read(self, instance=None)
        if self.buttons != NO_BUTTONS:
            for field in self.fields:
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
    self_containing = True

    def __init__(self, fields, border_width=6):
        Group.__init__(self, fields, "")
        self.border_width = border_width

    def create_widgets(self):
        Group.create_widgets(self)
        self.container = gtk.HBox()
        self.container.set_spacing(6)
        self.container.set_border_width(self.border_width)
        for field in self.fields:
            if field.get_active():
                assert field.self_containing, "For the HBox, all the fields must be self-containing"
                self.container.pack_start(field.container)


class Notebook(Group):
    def __init__(self, named_fields, label_text=None):
        Group.__init__(self, [field for (name, field) in named_fields], label_text)
        self.named_fields = named_fields
        self.self_containing = True

    def create_widgets(self):
        Group.create_widgets(self)
        self.container = gtk.Notebook()
        self.container.set_border_width(6)
        for name, field in self.named_fields:
            assert field.self_containing
            if field.get_active():
                self.container.append_page(field.container, gtk.Label(name))

    def show(self, field):
        Group.show(self, field)
        self.container.set_current_page(self.container.page_num(field.container))
