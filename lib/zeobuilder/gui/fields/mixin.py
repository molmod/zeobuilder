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
# Contact information:
#
# Supervisors
#
# Prof. Dr. Michel Waroquier and Prof. Dr. Ir. Veronique Van Speybroeck
#
# Center for Molecular Modeling
# Ghent University
# Proeftuinstraat 86, B-9000 GENT - BELGIUM
# Tel: +32 9 264 65 59
# Fax: +32 9 264 65 60
# Email: Michel.Waroquier@UGent.be
# Email: Veronique.VanSpeybroeck@UGent.be
#
# Author
#
# Ir. Toon Verstraelen
# Center for Molecular Modeling
# Ghent University
# Proeftuinstraat 86, B-9000 GENT - BELGIUM
# Tel: +32 9 264 65 56
# Email: Toon.Verstraelen@UGent.be
#
# --


from zeobuilder import context
from zeobuilder.undefined import Undefined

import gtk

import StringIO


__all__ = [
    "SpecialState", "ambiguous",
    "ReadMixin", "EditMixin", "InvalidField", "FaultyMixin",
    "TableMixin", "TextViewMixin",
]


changed_indicator = "<span foreground=\"red\">*</span>"


class SpecialState(object):
    def __init__(self, label):
        self.label = label

    def __str__(self):
        return self.label

ambiguous = SpecialState(":::ambiguous:::")


class Attribute(object):
    def __get__(self, owner, ownertype):
        if owner.attribute_name is None:
            result = owner.current_instance
        else:
            result = owner.current_instance.__dict__[owner.attribute_name]
        if isinstance(result, Undefined):
            return result.last
        else:
            return result

    def __set__(self, owner, value):
        if owner.attribute_name is None:
            raise AttributeError("Can not assign to an attribute when no attribute_name is given.")
        else:
            owner.current_instance.__dict__[owner.attribute_name] = value

class AttributeUndefined(object):
    def __get__(self, owner, ownertype):
        if owner.attribute_name is None:
            result = owner.current_instance
        else:
            result = owner.current_instance.__dict__[owner.attribute_name]
        return isinstance(result, Undefined)


class ReadMixin(object):
    attribute = Attribute()
    undefined = AttributeUndefined()
    reset_representation = None

    def __init__(self, attribute_name=None):
        self.attribute_name = attribute_name

    def get_widgets_separate(self):
        assert self.data_widget is not None
        return self.label, self.data_widget, None

    def applicable(self, instance):
        if (self.attribute_name is not None) and (self.attribute_name not in instance.__dict__):
            #print "The attribute_name '%s' is not in the instance dictionary: %s." % (self.attribute_name, instance.__dict__)
            return False
        else:
            self.current_instance = instance
            #if not self.applicable_attribute():
            #    print "The attribute_name '%s' is not of the correct format." % self.attribute_name
            return self.applicable_attribute()
            del self.current_instance

    def applicable_attribute(self):
        return True

    def read(self):
        if self.get_active():
            sensitive = not self.undefined_from_instance(self.instance)
            self.set_sensitive(sensitive)
            self.original_sensitive = sensitive
            self.write_to_widget(self.convert_to_representation(self.read_from_instance(self.instance)), True)

    def read_multiplex(self):
        if self.get_active():
            first = self.convert_to_representation(self.read_from_instance(self.instances[0]))
            first_undefined = self.undefined_from_instance(self.instances[0])
            for instance in self.instances[1:]:
                next = self.convert_to_representation(self.read_from_instance(self.instances[0]))
                next_undefined = self.undefined_from_instance(self.instances[0])
                if first != next or first_undefined != next_undefined:
                    self.set_ambiguous_capability(True)
                    self.write_to_widget(ambiguous, True)
                    return
            self.set_sensitive(not first_undefined)
            self.original_sensitive = not first_undefined
            self.set_ambiguous_capability(False)
            self.write_to_widget(first, True)

    def write(self):
        pass

    def write_multiplex(self):
        pass

    def check(self):
        pass

    def set_ambiguous_capability(self, ambiguous):
        pass

    def changed_names(self):
        return []

    def read_from_instance(self, instance):
        self.current_instance = instance
        result = self.read_from_attribute()
        del self.current_instance
        return result

    def read_from_attribute(self):
        return self.attribute

    def undefined_from_instance(self, instance):
        self.current_instance = instance
        result = self.undefined
        del self.current_instance
        return result

    def convert_to_representation(self, value):
        return value

    def write_to_widget(self, representation, original=False):
        raise NotImplementedError


class EditMixin(ReadMixin):
    Popup = None

    def __init__(self, attribute_name=None, show_popup=True, history_name=None):
        ReadMixin.__init__(self, attribute_name)
        self.show_popup = show_popup
        self.history_name = history_name

        # stores the representation read from the instance attribute
        self.original_representation = None
        self.original_sensitive = None

        self.bu_popup = None
        self.popup = None

    def create_widgets(self):
        if (self.show_popup) and (self.Popup is not None):
            self.bu_popup = gtk.Button()
            self.bu_popup.set_property("can_focus", False)
            image = gtk.Image()
            image.set_from_stock(gtk.STOCK_INDEX, gtk.ICON_SIZE_MENU)
            self.bu_popup.add(image)
            self.bu_popup.connect("button_release_event", self.do_popup)
            self.popup = self.Popup(self)

    def destroy_widgets(self):
        if self.bu_popup is not None:
            self.bu_popup.destroy()
            self.bu_popup = None
            self.popup = None

    def get_widgets_separate(self):
        assert self.data_widget is not None
        return self.label, self.data_widget, self.bu_popup

    def do_popup(self, bu_popup, event):
        self.popup.do_popup(bu_popup, event.button, event.time)

    def write(self):
        if self.get_active() and self.changed():
            representation = self.read_from_widget()
            if self.get_sensitive():
                self.save_history(representation)
                value = self.convert_to_value(representation)
            else:
                value = Undefined(self.convert_to_value(representation))
            self.write_to_instance(value, self.instance)

    def write_multiplex(self):
        if self.get_active() and self.changed():
            representation = self.read_from_widget()
            if self.get_sensitive():
                self.save_history(representation)
                value = self.convert_to_value(representation)
            else:
                value = Undefined(self.convert_to_value(representation))
            for instance in self.instances:
                self.write_to_instance(value, instance)

    def save_history(self, representation):
        if self.history_name is not None:
            context.application.configuration.add_to_history(self.history_name, representation)

    def changed_names(self):
        if self.get_active() and self.changed():
            return [self.attribute_name]
        else:
            return []

    def write_to_widget(self, representation, original=False):
        if original:
            self.original_representation = representation
        if self.history_name is not None:
            saved_representations =  context.application.configuration.get_saved_representations(self.history_name)
            self.saved_name = None
            for name, saved_representation in saved_representations.iteritems():
                if saved_representation == representation:
                    self.saved_name = name
                    break
        self.update_label()

    def read_from_widget(self):
        # This shoud just return the values from the widgets without any
        # conversion.
        raise NotImplementedError

    def convert_to_value(self, representation):
        # This should convert a representation in a value
        return representation

    def write_to_instance(self, value, instance):
        self.current_instance = instance
        if value is None: self.attribute = None
        self.write_to_attribute(value)
        del self.current_instance

    def write_to_attribute(self, value):
        self.attribute = value

    def changed(self):
        if self.get_sensitive() != self.original_sensitive: return True
        representation = self.read_from_widget()
        return not (
            representation == self.original_representation or
            representation == ambiguous or
            not self.get_sensitive()
        )

    def on_widget_changed(self, widget):
        self.update_label()

    def update_label(self):
        if self.label is None:
            return
        if self.changed():
            #print "ON ", self.attribute_name, id(self), self.label_text
            if len(self.label.get_label()) == len(self.label_text):
                self.label.set_label(self.label_text + changed_indicator)
        else:
            #print "OFF", self.attribute_name, id(self), self.label_text
            if len(self.label.get_label()) > len(self.label_text):
                self.label.set_label(self.label_text)

    def set_sensitive(self, sensitive):
        if self.get_active():
            if self.bu_popup is not None:
                self.bu_popup.set_sensitive(sensitive)


class InvalidField(Exception):
    def __init__(self, field, message):
        Exception.__init__(self)
        self.field = field
        self.message = message


class FaultyMixin(EditMixin):
    def check(self):
        #print self.label_text, self.instances, self.instance, self.get_active()
        if self.get_active() and self.changed():
            try:
                self.convert_to_value(self.read_from_widget())
            except ValueError, e:
                invalid_field = InvalidField(self, str(e))
                raise invalid_field


class TableMixin(object):
    def __init__(self, short=True, cols=1):
        self.short = short
        self.cols = cols

    def create_widgets(self):
        fields_active = sum(field.get_active() for field in self.fields)
        rows = fields_active / self.cols + (fields_active % self.cols > 0)
        if rows > 1 or self.short:
            self.high_widget = True
        else:
            self.high_widget = False
            for field in self.fields:
                if field.high_widget:
                    self.high_widget = True
                    break
        table = gtk.Table(rows, self.cols * 3)
        first_radio_button = None
        index = 0
        for field in self.fields:
            if not field.get_active():
                continue
            col = index % self.cols
            row = index / self.cols
            left = col * 3
            right = left + 3

            if field.high_widget:
                if self.short:
                    container = field.get_widgets_short_container()
                    table.attach(
                        container, left, right, row, row + 1,
                        xoptions=gtk.EXPAND|gtk.FILL,
                        yoptions=gtk.EXPAND|gtk.FILL,
                    )
                else:
                    container = field.get_widgets_flat_container()
                    table.attach(
                        container, left, right, row, row + 1,
                        xoptions=gtk.EXPAND|gtk.FILL, yoptions=0,
                    )
                container.set_border_width(0)
            else:
                label, data_widget, bu_popup = field.get_widgets_separate()
                if label is not None:
                    table.attach(
                        label, left, left + 1, row, row + 1,
                        xoptions=gtk.FILL, yoptions=0,
                    )
                    left += 1
                if bu_popup is not None:
                    table.attach(
                        bu_popup, right - 1, right, row, row + 1,
                        xoptions=0, yoptions=0,
                    )
                    right -= 1
                table.attach(
                    data_widget, left, right, row, row + 1,
                    xoptions=gtk.EXPAND|gtk.FILL, yoptions=0,
                )
            index += 1
        table.set_row_spacings(6)
        for col in xrange(self.cols * 3 - 1):
            if col % 3 == 2:
                table.set_col_spacing(col, 24)
            else:
                table.set_col_spacing(col, 6)
        self.data_widget = table


class TextViewMixin(object):
    def __init__(self, width=250, height=300):
        self.attribute_is_stream = False
        self.width = width
        self.height = height

    def create_widgets(self):
        self.text_view = gtk.TextView()
        self.text_view.set_wrap_mode(gtk.WRAP_WORD)
        self.text_view.set_accepts_tab(False)
        self.text_buffer = self.text_view.get_buffer()
        self.text_buffer.connect("changed", self.on_widget_changed)
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_shadow_type(gtk.SHADOW_IN)
        scrolled_window.set_shadow_type(gtk.SHADOW_IN)
        scrolled_window.set_size_request(self.width, self.height)
        scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
        scrolled_window.add(self.text_view)
        self.data_widget = scrolled_window

    def destroy_widgets(self):
        self.textview = None

    def convert_to_representation(self, value):
        if isinstance(value, StringIO.StringIO):
            self.attribute_is_stream = True
            return value.getvalue()
        else:
            self.attribute_is_stream = False
            return value

    def write_to_widget(self, representation):
        if representation == ambiguous: representation = ""
        self.text_buffer.set_text(representation)

    def convert_to_value(self, representation):
        if self.attribute_is_stream:
            return StringIO.StringIO(representation)
        else:
            return representation

    def read_from_widget(self):
        start, end = self.text_buffer.get_bounds()
        representation = self.text_buffer.get_slice(start, end)
        if representation == "":
            return ambiguous
        else:
            return representation


