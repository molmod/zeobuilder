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
from mixin import ReadMixin, EditMixin, FaultyMixin, InvalidField, \
                  TableMixin, ambiguous, insensitive

import gtk, numpy


__all__ = ["Read", "Edit", "Faulty", "Composed", "ComposedInTable", "Group"]


class Read(Single, ReadMixin):
    def __init__(self, label_text=None, attribute_name=None):
        Single.__init__(self, label_text)
        ReadMixin.__init__(self, attribute_name)

    def applicable(self, instance):
        return ReadMixin.applicable(self, instance)


class Edit(Single, EditMixin):
    def __init__(self, label_text=None, attribute_name=None, show_popup=True, history_name=None):
        Single.__init__(self, label_text)
        EditMixin.__init__(self, attribute_name, show_popup, history_name)

    def applicable(self, instance):
        return EditMixin.applicable(self, instance)

    def create_widgets(self):
        Single.create_widgets(self)
        EditMixin.create_widgets(self)

    def destroy_widgets(self):
        Single.destroy_widgets(self)
        EditMixin.destroy_widgets(self)


class Faulty(Single, FaultyMixin):
    def __init__(self, label_text=None, attribute_name=None, show_popup=True, history_name=None):
        Single.__init__(self, label_text)
        FaultyMixin.__init__(self, attribute_name, show_popup, history_name)

    def applicable(self, instance):
        return FaultyMixin.applicable(self, instance)

    def create_widgets(self):
        Single.create_widgets(self)
        FaultyMixin.create_widgets(self)

    def destroy_widgets(self):
        Single.destroy_widgets(self)
        FaultyMixin.destroy_widgets(self)


class Composed(Multiple, FaultyMixin):
    high_widget = True

    def __init__(self, fields, label_text=None, attribute_name=None, show_popup=True, history_name=None, show_field_popups=False):
        for field in fields:
            if isinstance(field, EditMixin):
                field.show_popup = show_field_popups
        Multiple.__init__(self, fields, label_text)
        FaultyMixin.__init__(self, attribute_name, show_popup, history_name)
        self.show_field_popups = show_field_popups

    def applicable(self, instance):
        return FaultyMixin.applicable(self, instance)

    def create_widgets(self):
        for field in self.fields:
            field.on_widget_changed = self.on_widget_changed
            field.update_label = self.update_label
            field.changed = self.changed
            field.get_active = self.get_active
            # make the subfields also believe they are active
            field.instance = self.instance
            field.instances = self.instances
            field.create_widgets()
        Multiple.create_widgets(self)
        FaultyMixin.create_widgets(self)

    def destroy_widgets(self):
        Multiple.destroy_widgets(self)
        FaultyMixin.destroy_widgets(self)

    def read(self):
        FaultyMixin.read(self)

    def read_multiplex(self):
        FaultyMixin.read_multiplex(self)

    def write(self):
        FaultyMixin.write(self)

    def write_multiplex(self):
        FaultyMixin.write_multiplex(self)

    def check(self):
        Multiple.check(self)
        FaultyMixin.check(self)

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


class ComposedInTable(Composed, TableMixin):
    def __init__(self, fields, label_text=None, attribute_name=None, show_popup=True, history_name=None, show_field_popups=False, short=True, cols=1):
        Composed.__init__(self, fields, label_text, attribute_name, show_popup, history_name, show_field_popups)
        TableMixin.__init__(self, short, cols)

    def create_widgets(self):
        Composed.create_widgets(self)
        TableMixin.create_widgets(self)

    def destroy_widgets(self):
        Composed.destroy_widgets(self)
        TableMixin.destroy_widgets(self)


class Group(Multiple):
    def init_widgets(self, instance):
        for field in self.fields:
            field.init_widgets(instance)
        Multiple.init_widgets(self, instance)

    def init_widgets_multiplex(self, instances):
        for field in self.fields:
            field.init_widgets_multiplex(instances)
        Multiple.init_widgets_multiplex(self, instances)

    def get_widgets_separate(self):
        assert self.data_widget is not None
        return self.label, self.data_widget, None

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


class Checkable(Single):
    def __init__(self, slave):
        Single.__init__(self)
        self.slave = slave
        slave.parent = self
        self.check_button = None

    def init_widgets(self, instance):
        self.slave.init_widgets(instance)
        Single.init_widgets(self, instance)

    def init_widgets_multiplex(self, instances):
        self.slave.init_widgets_multiplex(instances)
        Single.init_widgets_multiplex(self, instances)

    def get_active(self):
        return self.slave.get_active()

    def applicable(self, instance):
        return self.slave.get_active()

    def changed_names(self):
        if not self.get_active():
            return []
        else:
            return self.slave.changed_names()

    def create_widgets(self):
        Single.create_widgets(self)
        self.slave.old_representation = ambiguous
        self.slave.create_widgets()
        self.slave.write_to_widget(ambiguous)
        self.check_button = gtk.CheckButton()
        self.check_button.connect("toggled", self.check_button_toggled)
        if self.slave.label is not None:
            self.check_button.add(self.slave.label)

    def destroy_widgets(self):
        if self.check_button is not None:
            self.check_button.destroy()
            self.check_button = None
        self.slave.destroy_widgets()
        Single.destroy_widgets(self)

    def get_widgets_separate(self):
        return self.check_button, self.slave.data_widget, self.slave.bu_popup

    def read(self):
        if self.get_active():
            self.slave.read()
            self.check_button.set_active(self.slave.read_from_widget() != insensitive)

    def read_multiplex(self):
        if self.get_active():
            self.slave.read_multiplex()
            self.check_button.set_active(self.slave.read_from_widget() != insensitive)

    def write(self):
        if self.get_active():
            self.slave.write()

    def write_multiplex(self):
        if self.get_active():
            self.slave.write_multiplex()

    def check(self):
        if self.get_active():
            self.slave.check()

    def grab_focus(self):
        self.slave.grab_focus()

    def check_button_toggled(self, check_button):
        if check_button.get_active():
            if self.slave.read_from_widget() == insensitive:
                self.slave.write_to_widget(self.slave.old_representation)
        else:
            old_representation = self.slave.read_from_widget()
            if old_representation != insensitive:
                self.slave.old_representation = old_representation
            self.slave.write_to_widget(insensitive)
