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



from zeobuilder import context
from zeobuilder.actions.composed import Immediate
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.gui.glade_wrapper import GladeWrapper
import zeobuilder.authors as authors

import gtk


class InfoDialog(GladeWrapper):
    def __init__(self):
        GladeWrapper.__init__(self, "plugins/core/gui.glade", "di_plugin_info", "dialog")
        self.dialog.hide()
        self.init_proxies([
            "la_category", "la_required_modules", "la_failed_modules",
            "la_file", "la_status", "vb_authors", "tv_authors",
            "bu_information", "sw_extra", "tv_extra",
        ])
        self.author_store = authors.init_widgets(self.tv_authors, self.bu_information)

    def run(self, plugin):
        self.dialog.set_title("Zeobuilder plugin information: %s" % plugin.id)
        self.la_category.set_label(plugin.category)
        self.la_required_modules.set_label(",".join(plugin.required_modules))
        self.la_failed_modules.set_label(",".join(plugin.failed_modules))
        self.la_failed_modules.set_label(",".join(plugin.failed_modules))
        self.la_status.set_label(plugin.status)
        self.la_file.set_label(plugin.module.__file__)

        if hasattr(plugin, "authors"):
            self.vb_authors.show_all()
            authors.fill_store(self.author_store, plugin.authors)
        else:
            self.author_store.clear()
            self.vb_authors.hide()

        self.sw_extra.hide()

        self.dialog.run()
        self.dialog.hide()


class PluginsDialog(object):
    def __init__(self):
        # fields: succes, name, category, filename
        self.store = gtk.ListStore(bool, str, str, str, object)

        self.list_view = gtk.TreeView(self.store)
        self.list_view.get_selection().connect("changed", self.on_selection_changed)

        renderer_pixbuf = gtk.CellRendererPixbuf()
        column = gtk.TreeViewColumn()
        column.pack_start(renderer_pixbuf, expand=False)
        def render_stock(column, cell, model, iter):
            if model.get_value(iter, 0):
                cell.set_property('stock-id', gtk.STOCK_APPLY)
            else:
                cell.set_property('stock-id', gtk.STOCK_CANCEL)
        column.set_cell_data_func(renderer_pixbuf, render_stock)
        self.list_view.append_column(column)

        column = gtk.TreeViewColumn("Name", gtk.CellRendererText(), text=1)
        column.set_sort_column_id(1)
        self.list_view.append_column(column)

        column = gtk.TreeViewColumn("Category", gtk.CellRendererText(), text=2)
        self.list_view.append_column(column)

        column = gtk.TreeViewColumn("Filename", gtk.CellRendererText(), text=3)
        self.list_view.append_column(column)


        self.scrolled_window = gtk.ScrolledWindow()
        self.scrolled_window.add(self.list_view)
        self.scrolled_window.set_border_width(6)
        self.scrolled_window.set_size_request(400, 300)
        self.scrolled_window.set_shadow_type(gtk.SHADOW_IN)

        self.dialog = gtk.Dialog(
            "Zeobuilder plugins",
            context.parent_window,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
        )
        self.dialog.vbox.pack_start(self.scrolled_window, True, True)
        self.info_button = self.dialog.add_button(gtk.STOCK_INFO, gtk.RESPONSE_OK)
        self.info_button.set_sensitive(False)
        self.dialog.add_button(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
        self.dialog.hide()

        self.info_dialog = InfoDialog()

    def on_selection_changed(self, tree_selection):
        self.info_button.set_sensitive(tree_selection.count_selected_rows() == 1)

    def run(self):
        # empty the list store
        self.store.clear()
        # fill the list store
        for category, plugins in context.application.plugins.all.iteritems():
            for plugin in plugins:
                self.store.append((
                    plugin.status.startswith("Success"),
                    plugin.id,
                    category,
                    plugin.module.__file__,
                    plugin,
                ))
        self.store.set_sort_column_id(1, gtk.SORT_ASCENDING)
        # show the dialog and hide it after the user closed it.
        response = self.dialog.run()
        while response == gtk.RESPONSE_OK:
            plugin = self.store.get_value(self.list_view.get_selection().get_selected()[1], 4)
            self.info_dialog.run(plugin)
            response = self.dialog.run()
        self.dialog.hide()


class ViewPlugins(Immediate):
    description = "Plugins"
    menu_info = MenuInfo("help/_Help:default", "_Plugins", order=(1, 0, 0, 1))
    plugins_dialog = PluginsDialog()
    authors = [authors.toon_verstraelen]

    def do(self):
        self.plugins_dialog.run()


actions = {
    "ViewPlugins": ViewPlugins,
}
