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

import gtk


class PluginsDialog(object):
    def __init__(self):
        # fields: succes, name, category, filename
        self.store = gtk.ListStore(bool, str, str, str)

        self.list_view = gtk.TreeView(self.store)

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
            "Plugins",
            context.parent_window,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE),
        )
        self.dialog.vbox.pack_start(self.scrolled_window, True, True)
        self.dialog.show_all()
        self.dialog.hide()


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
                    plugin.module.__file__
                ))
        # show the dialog and hide it after the user closed it.
        self.dialog.run()
        self.dialog.hide()


class ViewPlugins(Immediate):
    description = "Plugins"
    menu_info = MenuInfo("help/_Help:default", "_Plugins", order=(1, 0, 0, 1))
    plugins_dialog = PluginsDialog()

    def do(self):
        self.plugins_dialog.run()


actions = {
    "ViewPlugins": ViewPlugins,
}
