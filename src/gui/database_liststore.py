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


class DatabaseListStore(gtk.GenericTreeModel):
    def __init__(self, connection, query, column_types):
        gtk.GenericTreeModel.__init__(self)
        self.last_rowref = None
        self.last_rowvalues = None
        self.column_types = column_types

        self.connection = None
        self.cursor = None
        self.num_rows = 0
        self.refresh(connection, query)

    def __del__(self):
        gtk.GenericTreeModel.__del__(self)
        if cursor is not None:
            self.cursor.close()

    def refresh(self, connection=None, query=None):
        #for index in xrange(self.num_rows-1, -1, -1):
        #    self.row_deleted((index,))

        if self.cursor is not None:
            self.cursor.close()
        if query is not None:
            self.query = query
        if connection is not None:
            self.connection = connection

        if self.connection is not None:
            self.cursor = self.connection.cursor()
            self.numrows = self.cursor.execute(self.query)
        else:
            self.numrows = 0

        #for index in xrange(self.num_rows):
        #    path = (index, )
        #    iter = self.get_iter(path)
        #    self.row_inserted(path, iter)

    def clear(self):
        self.connection = None
        self.cursor.close()
        self.cursor = None
        self.numrows = 0

    def on_get_flags(self):
        #print "on_get_flags"
        return gtk.TREE_MODEL_LIST_ONLY|gtk.TREE_MODEL_ITERS_PERSIST

    def on_get_n_columns(self):
        #print "on_get_n_columns:", len(self.column_types)
        return len(self.column_types)

    def on_get_column_type(self, n):
        #print "on_get_column_types:", self.column_types[n]
        return self.column_types[n]

    def on_get_iter(self, path):
        if path[0] < self.numrows:
            #print "on_get_iter:", path[0]
            return path[0]
        else:
            #print "on_get_iter:", None
            return None

    def on_get_path(self, rowref):
        if rowref < self.numrows:
            #print "on_get_path:", (rowref, )
            return (rowref, )
        else:
            #print "on_get_path:", None
            return None

    def on_get_value(self, rowref, column):
        if (rowref < self.numrows) and (column < len(self.column_types)):
            if rowref != self.last_rowref:
                self.cursor.scroll(rowref, mode='absolute')
                self.last_rowvalues = self.cursor.fetchone()
                self.last_rowref = rowref
            #print "on_get_value:", self.last_rowvalues[column]
            return self.last_rowvalues[column]
        #print "on_get_value:", None

    def on_iter_next(self, rowref):
        if rowref < self.numrows - 1:
            #print "on_iter_next:", rowref + 1
            return rowref + 1
        else:
            #print "on_iter_next:", None
            return None

    def on_iter_children(self, rowref):
        if rowref is None:
            #print "on_iter_children:", 0
            return 0
        else:
            #print "on_iter_children:", None
            return None

    def on_iter_has_child(self, rowref):
        #print "on_iter_has_child:", False
        return False

    def on_iter_n_children(self, rowref):
        if rowref is None:
            #print "rowref is None:", self.numrows
            return self.numrows
        else:
            #print "rowref is not None:", 0
            return 0

    def on_iter_nth_child(self, rowref, n):
        if (rowref is None) and n < self.numrows:
            #print "on_iter_nth_child:", n
            return n
        else:
            #print "on_iter_nth_child:", None
            return None

    def on_iter_parent(self, child):
        #print "on_iter_parent:", None
        return None


def database_widgets(connection, query, column_headers, drop_query_expr):
    list_store = DatabaseListStore(connection, query, [str]*len(column_headers))

    list_view = gtk.TreeView(list_store)
    list_selection = list_view.get_selection()

    for index, column_header in enumerate(column_headers):
        column = gtk.TreeViewColumn(column_header)
        renderer_text = gtk.CellRendererText()
        column.pack_start(renderer_text, expand=True)
        column.add_attribute(renderer_text, "text", index)
        list_view.append_column(column)

    def on_refresh_clicked(button):
        list_store.refresh()
        list_view.set_model(None) # TODO: UGLY HACK
        list_view.set_model(list_store) # TODO: UGLY HACK

    bu_refresh = gtk.Button(stock=gtk.STOCK_REFRESH)
    bu_refresh.connect("clicked", on_refresh_clicked)

    def on_drop_clicked(button):
        model, iter = list_selection.get_selected()
        if iter is not None:
            list_view.set_model(None) # TODO: UGLY HACK
            cursor = model.connection.cursor()
            cursor.execute(drop_query_expr(model[iter]))
            cursor.close()
            list_store.refresh()
            list_view.set_model(list_store) # TODO: UGLY HACK

    bu_drop = gtk.Button(stock=gtk.STOCK_REMOVE)
    bu_drop.connect("clicked", on_drop_clicked)

    def on_selection_changed(foo):
        model, iter = list_selection.get_selected()
        bu_drop.set_sensitive(iter is not None)

    list_selection.connect("changed", on_selection_changed)

    scrolled_window = gtk.ScrolledWindow()
    scrolled_window.set_shadow_type(gtk.SHADOW_IN)
    scrolled_window.set_shadow_type(gtk.SHADOW_IN)
    scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    scrolled_window.add(list_view)

    return list_store, list_view, bu_refresh, bu_drop, scrolled_window
