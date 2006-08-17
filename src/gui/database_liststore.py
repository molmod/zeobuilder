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
        self.column_types = column_types
        self.cursor = connection.cursor()
        self.query = query

        self.last_rowref = None
        self.last_rowvalues = None

    def __del__(self):
        gtk.GenericTreeModel.__del__(self)
        if cursor is not None:
            self.cursor.close()

    def on_get_flags(self):
        #print "on_get_flags"
        return gtk.TREE_MODEL_LIST_ONLY|gtk.TREE_MODEL_ITERS_PERSIST

    def on_get_n_columns(self):
        #print "on_get_n_columns", len(self.column_types)
        return len(self.column_types)

    def on_get_column_type(self, n):
        #print "on_get_column_type", n, self.column_types[n]
        return self.column_types[n]

    def on_get_iter(self, path):
        #print "on_get_iter", path
        return path[0]

    def on_get_path(self, rowref):
        #print "on_get_path", rowref
        return (rowref, )

    def on_get_value(self, rowref, column):
        #print "on_get_value", rowref, column
        numrows = self.cursor.execute(self.query)
        if (rowref < numrows):
            if rowref != self.last_rowref:
                self.cursor.scroll(rowref, mode='absolute')
                self.last_rowvalues = self.cursor.fetchone()
                self.last_rowref = rowref
            #print self.last_rowvalues[column]
            return self.last_rowvalues[column]

    def on_iter_next(self, rowref):
        #print "on_iter_next", rowref
        if rowref >= self.cursor.execute(self.query) - 1:
            return None
        else:
            return rowref + 1

    def on_iter_children(self, rowref):
        #print "on_iter_children", rowref
        #if rowref is None: return 0
        #else: return None
        return 0

    def on_iter_has_child(self, rowref):
        #print "on_iter_has_child", rowref
        return False

    def on_iter_n_children(self, rowref):
        #print "on_iter_n_children", rowref
        #if rowref is None:
            #print self.numrows
            return self.cursor.execute(self.query)
        #else:
        #    return 0

    def on_iter_nth_child(self, rowref, n):
        #print "on_iter_nth_child", rowref, n
        #if (rowref is None) and n < self.numrows: return n
        #else: return None
        return n

    def on_iter_parent(self, child):
        #print "on_iter_parent", child
        return None
