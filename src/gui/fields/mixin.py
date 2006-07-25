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


import gtk

__all__ = ["ReadMixin", "EditMixin", "InvalidField", "FaultyMixin"]


changed_indicator = "<span foreground=\"red\">*</span>"


class Ambiguous(object):
    def __str__(self):
        return "(ambiguous state)"


ambiguous = Ambiguous()



class ReadMixin(object):
    mutable_attribute = False

    def __init__(self, attribute=None):
        assert self.mutable_attribute or attribute != None, "%s requires an immutable attribute." % self.__class__
        self.attribute = attribute

    def applicable(self, instance):
        #print self.attribute
        if (self.attribute is not None) and (self.attribute not in instance.__dict__):
            return False
        else:
            if self.mutable_attribute:
                if self.attribute is None:
                    return self.applicable_attribute(instance)
                else:
                    return self.applicable_attribute(eval("instance.%s" % self.attribute))
            else:
                return self.attribute is not None

    def applicable_attribute(self, instance):
        raise NotImplementedError

    def read(self, instance=None):
        if self.instance is not None:
            if instance is None: instance = self.instance
            representation = self.convert_to_representation(self.read_from_instance(instance))
            self.write_to_widget(representation, True)

    def read_multiplex(self):
        if self.instances is not None:
            common = self.convert_to_representation(self.read_from_instance(self.instances[0]))
            for instance in self.instances[1:]:
                if common != self.convert_to_representation(self.read_from_instance(instance)):
                    self.set_ambiguous_capability(True)
                    self.write_to_widget(ambiguous, True)
                    return
            self.set_ambiguous_capability(False)
            self.write_to_widget(common, True)

    def write(self, instance=None):
        pass

    def write_multiplex(self):
        pass

    def check(self):
        pass

    def set_ambiguous_capability(self, inconsistent):
        pass

    def changed_names(self):
        return []

    def read_from_instance(self, instance):
        if self.mutable_attribute:
            if self.attribute == None:
                return self.read_from_attribute(instance)
            else:
                return self.read_from_attribute(eval("instance.%s" % self.attribute))
        else:
            return eval("instance.%s" % self.attribute)

    def read_from_attribute(self, attribute):
        return attribute

    def convert_to_representation(self, value):
        return value

    def write_to_widget(self, representation, original=False):
        raise NotImplementedError


class EditMixin(ReadMixin):
    Popup = None

    def __init__(self, attribute=None, show_popup=True):
        ReadMixin.__init__(self, attribute)
        self.original = None
        self.show_popup = show_popup
        self.bu_popup = None

    def create_widgets(self):
        if (self.show_popup) and (self.Popup != None):
            self.bu_popup = gtk.Button()
            self.bu_popup.set_property("can_focus", False)
            image = gtk.Image()
            image.set_from_stock(gtk.STOCK_INDEX, gtk.ICON_SIZE_MENU)
            self.bu_popup.add(image)
            self.bu_popup.connect("button_release_event", self.on_bu_popup_released)

    def destroy_widgets(self):
        if self.bu_popup != None:
            self.bu_popup.destroy()
            self.bu_popup = None

    def write(self, instance=None):
        if self.instance != None and (self.changed() or instance!=None):
            representation = self.read_from_widget()
            if instance == None:
                self.write_to_instance(self.convert_to_value(representation), self.instance)
                #self.read()
            else:
                self.write_to_instance(self.convert_to_value(representation), instance)

    def write_multiplex(self):
        if self.instances != None and self.changed():
            representation = self.read_from_widget()
            for instance in self.instances:
                self.write_to_instance(self.convert_to_value(representation), instance)
            #self.read_multiplex()

    def changed_names(self):
        if self.get_active() and self.changed():
            return [self.attribute]
        else:
            return []

    def write_to_widget(self, representation, original=False):
        if original: self.original = representation
        self.update_label()

    def read_from_widget(self):
        # This shoud just return the values from the widgets without any
        # conversion.
        raise NotImplementedError

    def convert_to_value(self, representation):
        # This should convert a representation in a value
        return representation

    def write_to_instance(self, value, instance):
        if self.mutable_attribute:
            if self.attribute == None:
                self.write_to_attribute(value, instance)
            else:
                self.write_to_attribute(value, eval("instance.%s" % self.attribute))
        else:
            exec "instance.%s = value" % self.attribute

    def write_to_attribute(self, value, attribute):
        # Yo only want to implement this if self.mutable_attribute == True
        raise NotImplementedError

    def changed(self):
        representation = self.read_from_widget()
        return representation != self.original and representation != ambiguous

    def on_widget_changed(self, widget):
        self.update_label()

    def on_bu_popup_released(self, button, event):
        self.Popup(self, button.get_parent_window()).popup(event.button, event.time)

    def update_label(self):
        if self.label == None:
            return
        if self.changed():
            if len(self.label.get_label()) == len(self.label_text):
                self.label.set_label(self.label_text + changed_indicator)
        else:
            if len(self.label.get_label()) > len(self.label_text):
                self.label.set_label(self.label_text)


class InvalidField(Exception):
    def __init__(self, field, message):
        Exception.__init__(self)
        self.field = field
        self.message = message

    def prepend_message(self, new_line):
        self.message = new_line + "\n" + self.message


class FaultyMixin(EditMixin):
    def __init__(self, invalid_message, attribute=None, show_popup=True):
        EditMixin.__init__(self, attribute, show_popup)
        self.invalid_message = invalid_message

    def check(self):
        #print self.label_text, self.instances, self.instance, self.get_active()
        if self.get_active() and self.changed():
            try:
                self.convert_to_value(self.read_from_widget())
            except ValueError, e:
                invalid_field = InvalidField(self, str(e))
                invalid_field.prepend_message(self.invalid_message)
                raise invalid_field

