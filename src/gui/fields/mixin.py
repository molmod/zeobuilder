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


class ReadMixin(object):
    mutable_attribute = False

    def __init__(self, attribute=None):
        assert self.mutable_attribute or attribute != None, "%s requires an immutable attribute." % self.__class__
        self.attribute = attribute

    def applicable(self, node):
        #print self.attribute
        if (self.attribute is not None) and (self.attribute not in node.__dict__):
            return False
        else:
            if self.mutable_attribute:
                if self.attribute is None:
                    return self.applicable_attribute(node)
                else:
                    return self.applicable_attribute(eval("node.%s" % self.attribute))
            else:
                return self.attribute is not None

    def applicable_attribute(self, node):
        raise NotImplementedError

    def read(self, node=None):
        if self.node != None:
            if node == None: node = self.node
            representation = self.convert_to_representation(self.read_from_node(node))
            self.write_to_widget(representation, True)

    def read_multiplex(self):
        if self.nodes != None:
            common = self.convert_to_representation(self.read_from_node(self.nodes[0]))
            for node in self.nodes[1:]:
                if common != self.convert_to_representation(self.read_from_node(node)):
                    self.set_inconsistent_capability(True)
                    self.write_to_widget(None, True)
                    return
            self.set_inconsistent_capability(False)
            self.write_to_widget(common, True)

    def write(self, node=None):
        pass

    def write_multiplex(self):
        pass

    def check(self):
        pass

    def set_inconsistent_capability(self, inconsistent):
        pass

    def changed_names(self):
        return []

    def read_from_node(self, node):
        if self.mutable_attribute:
            if self.attribute == None:
                return self.read_from_attribute(node)
            else:
                return self.read_from_attribute(eval("node.%s" % self.attribute))
        else:
            return eval("node.%s" % self.attribute)

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

    def write(self, node=None):
        if self.node != None and (self.changed() or node!=None):
            representation = self.read_from_widget()
            if node == None:
                self.write_to_node(self.convert_to_value(representation), self.node)
                #self.read()
            else:
                self.write_to_node(self.convert_to_value(representation), node)

    def write_multiplex(self):
        if self.nodes != None and self.changed():
            representation = self.read_from_widget()
            for node in self.nodes:
                self.write_to_node(self.convert_to_value(representation), node)
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

    def write_to_node(self, value, node):
        if self.mutable_attribute:
            if self.attribute == None:
                self.write_to_attribute(value, node)
            else:
                self.write_to_attribute(value, eval("node.%s" % self.attribute))
        else:
            exec "node.%s = value" % self.attribute

    def write_to_attribute(self, value, attribute):
        # Yo only want to implement this if self.mutable_attribute == True
        raise NotImplementedError

    def changed(self):
        representation = self.read_from_widget()
        return representation != self.original and representation != None

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
        #print self.label_text, self.nodes, self.node, self.get_active()
        if self.get_active() and self.changed():
            try:
                self.convert_to_value(self.read_from_widget())
            except ValueError, e:
                invalid_field = InvalidField(self, str(e))
                invalid_field.prepend_message(self.invalid_message)
                raise invalid_field

