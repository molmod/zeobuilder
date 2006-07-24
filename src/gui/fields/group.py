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
from mixin import EditMixin

import gtk

__all__ = ["Table", "Notebook"]


class Table(Group):
    self_containing = True

    def __init__(self, fields, label_text=None, table_border_width=6):
        Group.__init__(self, fields, label_text)
        self.table_border_width = table_border_width

    def create_widgets(self):
        Group.create_widgets(self)
        self.container = gtk.Table(1, 3)
        self.container.set_row_spacings(6)
        self.container.set_col_spacings(6)
        self.container.set_border_width(self.table_border_width)
        if self.label != None:
            self.container.resize(1, 4)
            self.container.attach(self.label, 0, 3, 0, 1, xoptions=gtk.FILL, yoptions=0)
            first_edit = 1
            last_row = 1
        else:
            last_row = 0
            first_edit = 0
        for field in self.fields:
            if field.get_active():
                self.container.resize(last_row + 1, 3)
                container_left = first_edit
                container_right = first_edit + 3
                if not field.self_containing:
                    if field.label != None:
                        self.container.attach(field.label, first_edit, first_edit+1, last_row, last_row+1, xoptions=gtk.FILL, yoptions=0)
                        container_left += 1
                    if isinstance(field, EditMixin) and field.bu_popup != None:
                        container_right -= 1
                        self.container.attach(field.bu_popup, first_edit+2, first_edit+3, last_row, last_row+1, xoptions=0, yoptions=0)
                self.container.attach(field.container, container_left, container_right, last_row, last_row+1, xoptions=field.xoptions, yoptions=field.yoptions)
                last_row += 1
        if self.label != None:
            da = gtk.DrawingArea()
            da.set_size_request(10, 0)
            self.container.attach(da, 0, 1, 1, last_row+1, xoptions=0)

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
