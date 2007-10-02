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


from base import Single, Multiple
from mixin import ReadMixin, EditMixin, FaultyMixin, ambiguous


__all__ = ["Read", "Edit", "Faulty", "Composed", "Group"]


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

    def set_sensitive(self, sensitive):
        EditMixin.set_sensitive(self, sensitive)
        Single.set_sensitive(self, sensitive)


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

    def set_sensitive(self, sensitive):
        FaultyMixin.set_sensitive(self, sensitive)
        Single.set_sensitive(self, sensitive)


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

    def save_history(self, representations):
        FaultyMixin.save_history(self, representations)
        for field, representation in zip(self.fields, representations):
            field.save_history(representation)

    def check(self):
        Multiple.check(self)
        FaultyMixin.check(self)

    def convert_to_representation(self, value):
        return tuple(field.convert_to_representation(value[index]) for index, field in enumerate(self.fields))

    def write_to_widget(self, representation, original=False):
        if representation == ambiguous:
            for field in self.fields:
                field.write_to_widget(ambiguous, original)
        else:
            for index, field in enumerate(self.fields):
                field.write_to_widget(representation[index], original)
        FaultyMixin.write_to_widget(self, representation, original)

    def read_from_widget(self):
        result = tuple(field.read_from_widget() for field in self.fields)
        if ambiguous in result:
            # if one is ambiguous, we have to test them all to be sure.
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

    def set_sensitive(self, sensitive):
        FaultyMixin.set_sensitive(self, sensitive)
        Multiple.set_sensitive(self, sensitive)


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

