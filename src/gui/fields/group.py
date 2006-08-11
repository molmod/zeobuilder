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
from mixin import EditMixin, TableMixin, ambiguous

import gtk

__all__ = ["Table", "Notebook"]


class Table(Group, TableMixin):
    def __init__(self, fields, label_text=None, short=True, cols=1):
        Group.__init__(self, fields, label_text)
        TableMixin.__init__(self, short, cols)

    def create_widgets(self):
        Group.create_widgets(self)
        TableMixin.create_widgets(self)


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
