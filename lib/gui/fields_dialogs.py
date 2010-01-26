# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 - 2010 Toon Verstraelen <Toon.Verstraelen@UGent.be>, Center
# for Molecular Modeling (CMM), Ghent University, Ghent, Belgium; all rights
# reserved unless otherwise stated.
#
# This file is part of Zeobuilder.
#
# Zeobuilder is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# In addition to the regulations of the GNU General Public License,
# publications and communications based in parts on this program or on
# parts of this program are required to cite the following article:
#
# "ZEOBUILDER: a GUI toolkit for the construction of complex molecules on the
# nanoscale with building blocks", Toon Verstraelen, Veronique Van Speybroeck
# and Michel Waroquier, Journal of Chemical Information and Modeling, Vol. 48
# (7), 1530-1541, 2008
# DOI:10.1021/ci8000748
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

from simple import field_error
import fields
from zeobuilder import context
from zeobuilder.application import TestApplication

import gtk, gobject


__all__ = ["FieldsDialogBase", "FieldsDialogSimple", "FieldsDialogMultiplex"]


class FieldsDialogBase(object):
    def __init__(self, title, main_field, action_buttons):
        self.title = title
        self.main_field = main_field
        self.action_buttons = action_buttons

    def create_dialog(self):
        self.dialog = gtk.Dialog()
        self.dialog.set_transient_for(context.parent_window)
        self.dialog.connect("response", self.on_dialog_response)
        self.dialog.connect("show", self.on_dialog_show)
        self.dialog.set_title(self.title)
        for action_button in self.action_buttons:
            button = self.dialog.add_button(action_button[0], action_button[1])
            if action_button[1] == gtk.RESPONSE_OK:
                button.set_property("can-default", True)
                button.set_property("has-default", True)

    def add_main_widget(self, widget):
        self.dialog.vbox.pack_start(widget, False, False)

    def destroy_dialog(self):
        self.dialog.destroy()
        del self.dialog

    def run(self, data):
        # build up the dialog
        self.init_widgets(data)
        self.create_dialog()
        self.add_main_widget(self.main_field.get_widgets_short_container())
        self.main_field.container.show_all()
        self.valid = True
        # fill in the fields

        self.read()
        response_id = self.dialog.run()
        while not (self.hide or (response_id == gtk.RESPONSE_NONE) or \
                   (response_id == gtk.RESPONSE_DELETE_EVENT) or \
                   (response_id == gtk.RESPONSE_CANCEL)):
            if not self.hide and self.valid:
                self.read()
            response_id = self.dialog.run()
        # hide myself
        self.main_field.destroy_widgets()
        self.destroy_dialog()
        return response_id

    def on_dialog_response(self, dialog, response_id):
        self.hide = True
        if (response_id == gtk.RESPONSE_OK) or \
           (response_id == gtk.RESPONSE_APPLY) or \
           (response_id > 0):
            try:
                self.main_field.check()
                self.valid = True
                # first read out the widgets and update the instance
                self.write()
            except fields.mixin.InvalidField, e:
                trace = e.field.get_trace()
                if trace is None:
                    trace = "The problem is due to the combination of all the fields."
                field_error(trace, e.message)
                e.field.show()
                e.field.grab_focus()
                self.valid = False
                self.hide = False

    def on_dialog_show(self, dialog):
        def response():
            dialog.response(gtk.RESPONSE_CLOSE)
        if isinstance(context.application, TestApplication):
            gobject.idle_add(response)

    def init_widgets(self, data):
        raise NotImplementedError

    def read(self):
        raise NotImplementedError

    def write(self):
        raise NotImplementedError


class FieldsDialogSimple(FieldsDialogBase):
    def init_widgets(self, instance):
        self.main_field.init_widgets(instance)

    def read(self):
        self.main_field.read()

    def write(self):
        self.main_field.write()


class FieldsDialogMultiplex(FieldsDialogBase):
    def init_widgets(self, instances):
        self.main_field.init_widgets_multiplex(instances)

    def read(self):
        self.main_field.read_multiplex()

    def write(self):
        self.main_field.write_multiplex()


class DialogFieldInfo(object):
    def __init__(self, category, order, field):
        self.category = category
        self.order = order
        self.field = field


def create_tabbed_main_field(dialog_fields):
    unique_dialog_fields = {}
    categories = set()

    for dialog_field_info in dialog_fields:
        key = (dialog_field_info.category, dialog_field_info.order)
        existing = unique_dialog_fields.get(key)
        if existing is None:
            unique_dialog_fields[key] = dialog_field_info
        else:
            assert existing.field.label_text == dialog_field_info.field.label_text, \
                "Labels with duplicate order=%s in category %s: '%s' (%s) and '%s' (%s)" % (
                    dialog_field_info.order, dialog_field_info.category,
                    existing.field.label_text, existing.field,
                    dialog_field_info.field.label_text, dialog_field_info.field
                )
        categories.add(dialog_field_info.category)

    fields_by_category = dict((category, []) for category in categories)
    for dialog_field_info in unique_dialog_fields.itervalues():
        fields_by_category[dialog_field_info.category].append(dialog_field_info)
    fields_by_category = fields_by_category.items()

    fields_by_category.sort(key=(lambda cf: min(dfi.order for dfi in cf[1])))
    for category, field_infos in fields_by_category:
        field_infos.sort(key=(lambda dfi: dfi.order))

    #print
    #for category, field_infos in fields_by_category:
    #    print "C", category
    #    for dialog_field_info in field_infos:
    #        print "DFI", dialog_field_info.order, dialog_field_info.field.label_text

    return fields.group.Notebook([
        (category, fields.group.Table([
            dialog_field_info.field
            for dialog_field_info
            in field_infos
        ])) for category, field_infos
        in fields_by_category
    ])


