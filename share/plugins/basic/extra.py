# -*- coding: utf-8 -*-
# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 - 2012 Toon Verstraelen <Toon.Verstraelen@UGent.be>, Center
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


from zeobuilder import context
from zeobuilder.actions.composed import Immediate
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.undefined import Undefined
from zeobuilder.gui.simple import ok_error
import zeobuilder.actions.primitive as primitive
import zeobuilder.authors as authors

import gtk


EXTRA_EXISTING = 0
EXTRA_REMOVED = 1
EXTRA_NEW = 2

class ExtraDialog(object):
    def create_dialog(self):
        self.dialog = gtk.Dialog("Edit extra attributes", context.parent_window)
        for action_button in [(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK)]:
            button = self.dialog.add_button(action_button[0], action_button[1])
            if action_button[1] == gtk.RESPONSE_OK:
                button.set_property("can-default", True)
                button.set_property("has-default", True)

        self.list_store = gtk.ListStore(str, object, object, int)
        self.tree_view = gtk.TreeView(self.list_store)

        cell_renderer = gtk.CellRendererText()
        cell_renderer.connect("edited", self.on_key_edited)
        column = gtk.TreeViewColumn("Key", cell_renderer)
        column.set_min_width(100)
        def get_value(column, cell, model, iter):
            key = model.get_value(iter, 0)
            status = model.get_value(iter, 3)
            cell.set_property("text", key)
            if status == 2:
                cell.set_property("editable", True)
        column.set_cell_data_func(cell_renderer, get_value)
        self.tree_view.append_column(column)

        cell_renderer = gtk.CellRendererText()
        cell_renderer.connect("edited", self.on_value_edited)
        column = gtk.TreeViewColumn("Value", cell_renderer)
        column.set_min_width(100)
        def get_value(column, cell, model, iter):
            value = model.get_value(iter, 1)
            if isinstance(value, Undefined):
                cell.set_property("markup", "<span foreground='#AAAAAA'>Mixed</span>")
            else:
                cell.set_property("markup", str(value))
            cell.set_property("editable", True)
        column.set_cell_data_func(cell_renderer, get_value)
        self.tree_view.append_column(column)

        cell_renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Data type", cell_renderer)
        column.set_min_width(50)
        def get_type(column, cell, model, iter):
            value = model.get_value(iter, 1)
            if isinstance(value, str):
                cell.set_property("text", "str")
            elif isinstance(value, int):
                cell.set_property("text", "int")
            elif isinstance(value, float):
                cell.set_property("text", "float")
            else:
                cell.set_property("markup", "<span foreground='#AAAAAA'>NA</span>")
        column.set_cell_data_func(cell_renderer, get_type)
        self.tree_view.append_column(column)

        cell_renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Status", cell_renderer)
        column.set_min_width(50)
        def get_status(column, cell, model, iter):
            status = model.get_value(iter, 3)
            if status == EXTRA_EXISTING:
                if model.get_value(iter, 1) == model.get_value(iter, 2):
                    cell.set_property("text", "")
                else:
                    cell.set_property("markup", "<span foreground='#0000AA'>Modified</span>")
            elif status == EXTRA_REMOVED:
                cell.set_property("markup", "<span foreground='#AA0000'>Removed</span>")
            elif status == EXTRA_NEW:
                cell.set_property("markup", "<span foreground='#00AA00'>Added</span>")
        column.set_cell_data_func(cell_renderer, get_status)
        self.tree_view.append_column(column)

        sw = gtk.ScrolledWindow()
        sw.add(self.tree_view)
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        sw.set_size_request(-1, 200)
        sw.set_shadow_type(gtk.SHADOW_IN)
        sw.set_border_width(6)

        add_button = gtk.Button(stock=gtk.STOCK_ADD)
        add_button.connect("clicked", self.on_add_clicked)
        remove_button = gtk.Button(stock=gtk.STOCK_REMOVE)
        remove_button.connect("clicked", self.on_remove_clicked)
        revert_button = gtk.Button(label="_Revert")
        revert_image = gtk.Image()
        revert_image.set_from_stock(gtk.STOCK_UNDO, gtk.ICON_SIZE_BUTTON)
        revert_button.set_image(revert_image)
        revert_button.connect("clicked", self.on_revert_clicked)

        hbox = gtk.HBox(spacing=6, homogeneous=True)
        hbox.set_border_width(6)
        hbox.pack_start(add_button)
        hbox.pack_start(remove_button)
        hbox.pack_start(revert_button)

        self.dialog.vbox.set_spacing(0)
        self.dialog.vbox.pack_start(sw)
        self.dialog.vbox.pack_start(hbox, expand=False)

    def destroy_dialog(self):
        self.dialog.destroy()

    def run(self, extra_attrs):
        self.create_dialog()
        self.list_store.clear()
        for key, value in sorted(extra_attrs.iteritems()):
            self.list_store.append([key,value,value,EXTRA_EXISTING])

        self.dialog.show_all()
        response_id = self.dialog.run()
        modified_extra_attrs = {}
        remove_keys = []
        if response_id == gtk.RESPONSE_OK:
            for key, value, orig, status in self.list_store:
                if status == EXTRA_NEW or (value != orig and status == EXTRA_EXISTING):
                    modified_extra_attrs[key] = value
                elif status == EXTRA_REMOVED:
                    remove_keys.append(key)
            modified_extra_attrs
        self.destroy_dialog()
        return modified_extra_attrs, remove_keys

    def on_add_clicked(self, button):
        i = 1
        iter_test = self.list_store.get_iter_first()
        prefix = "No name "
        while iter_test is not None:
            key_test = self.list_store.get_value(iter_test, 0)
            if key_test.startswith(prefix):
                try:
                    j = int(key_test[len(prefix):])
                    if i <= j:
                        i = j+1
                except ValueError:
                    pass
            iter_test = self.list_store.iter_next(iter_test)

        iter = self.list_store.append(["%s%i" % (prefix, i), "", "", 2])
        self.tree_view.grab_focus()
        self.tree_view.get_selection().select_iter(iter)

    def on_remove_clicked(self, button):
        model, iter = self.tree_view.get_selection().get_selected()
        status = model.get_value(iter, 3)
        if status == EXTRA_EXISTING:
            model.set_value(iter, 3, EXTRA_REMOVED)
        else:
            model.remove(iter)

    def on_revert_clicked(self, button):
        model, iter = self.tree_view.get_selection().get_selected()
        status = model.get_value(iter, 3)
        if status == EXTRA_EXISTING or status == EXTRA_REMOVED:
            model.set_value(iter, 3, EXTRA_EXISTING)
            model.set_value(iter, 1, model.get_value(iter, 2))

    def on_key_edited(self, cell, path, new_text):
        iter = self.list_store.get_iter_from_string(path)
        iter_test = self.list_store.get_iter_first()
        while iter_test is not None:
            path_test = self.list_store.get_string_from_iter(iter_test)
            if path != path_test and self.list_store.get_value(iter_test, 0) == new_text:
                ok_error("The keys must be unique.")
                return
            iter_test = self.list_store.iter_next(iter_test)
        self.list_store.set_value(iter, 0, new_text)

    def on_value_edited(self, cell, path, new_text):
        iter = self.list_store.get_iter_from_string(path)
        new_text = new_text.strip()
        try:
            self.list_store.set_value(iter, 1, int(new_text))
            return
        except ValueError:
            pass
        try:
            self.list_store.set_value(iter, 1, float(new_text))
            return
        except ValueError:
            pass
        self.list_store.set_value(iter, 1, new_text)


class EditExtraAttributes(Immediate):
    description = "Add bonds (parameters)"
    menu_info = MenuInfo("default/_Object:basic", "_Extra attributes", order=(0, 4, 0, 2))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) own tests
        if len(context.application.cache.nodes) == 0: return False
        # C) passed all tests:
        return True

    def do(self):
        # A) collect all extra attributes of the selected nodes
        extra_attrs = {}
        for node in context.application.cache.nodes:
            for key, value in node.extra.iteritems():
                other_value = extra_attrs.get(key)
                if other_value is None:
                    extra_attrs[key] = value
                elif isinstance(other_value, Undefined):
                    continue
                elif other_value != value:
                    extra_attrs[key] = Undefined()
        for key, value in extra_attrs.items():
            if isinstance(value, Undefined):
                continue
            for node in context.application.cache.nodes:
                other_value = node.extra.get(key)
                if other_value != value:
                    extra_attrs[key] = Undefined()
                    break

        # B) present the extra attributes in a popup window with editing features
        extra_dialog = ExtraDialog()
        modified_extra_attrs, remove_keys = extra_dialog.run(extra_attrs)
        if len(modified_extra_attrs) > 0 or len(remove_keys) > 0:
            # C) the modified extra attributes are applied to the select objects
            for node in context.application.cache.nodes:
                new_value = node.extra.copy()
                new_value.update(modified_extra_attrs)
                for remove_key in remove_keys:
                    new_value.pop(remove_key, None)
                primitive.SetProperty(node, "extra", new_value)


actions = {
    "EditExtraAttributes": EditExtraAttributes,
}


