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

from base import Single, Multiple
from mixin import ReadMixin, EditMixin, FaultyMixin, InvalidField, ambiguous, insensitive

import gtk

__all__ = ["Read", "Edit", "Faulty", "Composed", "Group"]


class Read(Single, ReadMixin):
    def __init__(self, label_text=None, attribute_name=None):
        Single.__init__(self, label_text)
        ReadMixin.__init__(self, attribute_name)

    def applicable(self, instance):
        return ReadMixin.applicable(self, instance)


class Edit(Single, EditMixin):
    def __init__(self, label_text=None, attribute_name=None, show_popup=True):
        Single.__init__(self, label_text)
        EditMixin.__init__(self, attribute_name, show_popup)

    def applicable(self, instance):
        return EditMixin.applicable(self, instance)

    def create_widgets(self):
        Single.create_widgets(self)
        EditMixin.create_widgets(self)

    def destroy_widgets(self):
        Single.destroy_widgets(self)
        EditMixin.destroy_widgets(self)


class Faulty(Single, FaultyMixin):
    def __init__(self, invalid_message, label_text=None, attribute_name=None, show_popup=True):
        Single.__init__(self, label_text)
        FaultyMixin.__init__(self, invalid_message, attribute_name, show_popup)

    def applicable(self, instance):
        return FaultyMixin.applicable(self, instance)

    def create_widgets(self):
        Single.create_widgets(self)
        FaultyMixin.create_widgets(self)

    def destroy_widgets(self):
        Single.destroy_widgets(self)
        FaultyMixin.destroy_widgets(self)


class Composed(Multiple, FaultyMixin):
    self_containing = True
    mutable_attribute = True

    def __init__(self, fields, invalid_message, label_text=None, attribute_name=None, show_popup=True, show_field_popups=False, table_border_width=6, vertical=True):
        for field in fields:
            field.on_widget_changed = self.on_widget_changed
            field.update_label = self.update_label
            field.changed = self.changed
        Multiple.__init__(self, fields, label_text)
        FaultyMixin.__init__(self, invalid_message, attribute_name, show_popup)
        self.show_field_popups = show_field_popups
        self.table_border_width = table_border_width
        self.vertical = vertical

    def applicable(self, instance):
        return FaultyMixin.applicable(self, instance)

    def create_widgets(self):
        #def on_widget_changed_substitude(widget):
        #    self.on_widget_change(widget)

        for field in self.fields:
            # to make the subfields also believe they are active
            field.instance = self.instance
            field.instances = self.instances
            field.create_widgets()
        Multiple.create_widgets(self)
        FaultyMixin.create_widgets(self)

    def tabulate_widgets(self):
        if self.vertical:
            self.tabulate_widgets_vertical()
        else:
            self.tabulate_widgets_horizontal()

    def tabulate_widgets_vertical(self):
        if self.show_field_popups:
            cols = 3
        else:
            cols = 2

        if (self.label is not None) or (self.bu_popup is not None):
            hbox = gtk.HBox(spacing=6)
            if self.label is not None: hbox.pack_start(self.label, expand=False, fill=False)
            if self.bu_popup is not None: hbox.pack_end(self.bu_popup, expand=False, fill=False)
            self.container = gtk.Table(4, cols)
            self.container.attach(hbox, 0, cols, 0, 1, yoptions=0)
            first_edit = 1
        else:
            self.container = gtk.Table(3, cols)
            first_edit = 0
        self.container.set_row_spacings(6)
        self.container.set_col_spacings(6)
        self.container.set_border_width(self.table_border_width)
        for index, field in enumerate(self.fields):
            if field.self_containing:
                self.container.attach(field.container, 0, cols, first_edit + index, first_edit + index + 1, xoptions=field.xoptions, yoptions=field.yoptions)
            else:
                self.container.attach(field.label, 0, 1, first_edit + index, first_edit + index + 1, xoptions=gtk.FILL, yoptions=0)
                self.container.attach(field.container, 1, 2, first_edit + index, first_edit + index + 1, xoptions=field.xoptions, yoptions=field.yoptions)
                if self.show_field_popups:
                    self.container.attach(field.popup, 2, 3, first_edit + index, first_edit + index + 1, xoptions=gtk.FILL, yoptions=0)

    def tabulate_widgets_horizontal(self):
        cols = len(self.fields)
        if (self.label is not None) or (self.bu_popup is not None):
            hbox = gtk.HBox(spacing=6)
            if self.label is not None: hbox.pack_start(self.label, expand=False, fill=False)
            if self.bu_popup is not None: hbox.pack_end(self.bu_popup, expand=False, fill=False)
            self.container = gtk.Table(2, cols)
            self.container.attach(hbox, 0, cols, 0, 1, yoptions=0)
            first_edit = 1
        else:
            self.container = gtk.Table(1, cols)
            first_edit = 0
        self.container.set_row_spacings(6)
        self.container.set_col_spacings(6)
        self.container.set_border_width(self.table_border_width)
        for index, field in enumerate(self.fields):
            assert field.self_containing, "In the horizontal table layout the fields must be self-containing."
            self.container.attach(
                field.container,
                index, index+1,
                first_edit, first_edit+1,
                xoptions=field.xoptions,
                yoptions=field.yoptions
            )

    def destroy_widgets(self):
        Multiple.destroy_widgets(self)
        FaultyMixin.destroy_widgets(self)

    def read(self, instance=None):
        FaultyMixin.read(self, instance)

    def read_multiplex(self):
        FaultyMixin.read_multiplex(self)

    def write(self, instance=None):
        FaultyMixin.write(self, instance)

    def write_multiplex(self):
        FaultyMixin.write_multiplex(self)

    def check(self):
        if self.get_active():
            try:
                Multiple.check(self)
            except InvalidField, e:
                if self.invalid_message is not None:
                    e.prepend_message(self.invalid_message)
                raise e

    def convert_to_representation(self, value):
        return tuple(field.convert_to_representation(value[index]) for index, field in enumerate(self.fields))

    def write_to_widget(self, representation, original=False):
        if representation == ambiguous or representation == insensitive:
            for field in self.fields:
                field.write_to_widget(representation, original)
        else:
            for index, field in enumerate(self.fields):
                field.write_to_widget(representation[index], original)
        FaultyMixin.write_to_widget(self, representation, original)

    def read_from_widget(self):
        result = tuple(field.read_from_widget() for field in self.fields)
        if insensitive in result:
            return insensitive # if one is insensitive, they all are. We know for sure.
        elif ambiguous in result:
            # if one is ambiguous, we have to test the all to be sure.
            all_ambiguous = True
            for item in result:
                if item != ambiguous:
                    all_ambiguous = False
                    break
            if all_ambiguous:
                return ambiguous
            else:
                return result
        else:
            return result

    def convert_to_value(self, representation):
        return tuple(field.convert_to_value(representation[index]) for index, field in enumerate(self.fields))


class Group(Multiple):
    def init_widgets(self, instance):
        for field in self.fields:
            field.init_widgets(instance)
        Multiple.init_widgets(self, instance)

    def init_widgets_multiplex(self, instances):
        for field in self.fields:
            field.init_widgets_multiplex(instances)
        Multiple.init_widgets_multiplex(self, instances)

    def applicable(self, instance):
        for field in self.fields:
            if field.get_active(): return True
        return False

    def changed_names(self):
        if not self.get_active(): return []
        changed = []
        for field in self.fields:
            changed.extend(field.changed_names())
        return changed
