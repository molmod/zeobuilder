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
from mixin import EditMixin, TableMixin, ambiguous, insensitive, NO_BUTTONS

import gtk

__all__ = ["Table", "Notebook"]


class Table(Group, TableMixin):
    def __init__(self, fields, label_text=None, short=True, cols=1, buttons=NO_BUTTONS):
        Group.__init__(self, fields, label_text)
        TableMixin.__init__(self, short, cols, buttons)

    def create_widgets(self):
        Group.create_widgets(self)
        TableMixin.create_widgets(self)

    def destroy_widgets(self):
        Group.destroy_widgets(self)
        TableMixin.destroy_widgets(self)

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
                field.old_representation = old_representation
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

    def get_description(self, caller):
        n = self.data_widget
        label = n.get_tab_label(n.get_nth_page(n.page_num(caller.container)))
        return label.get_text()

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
