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


from zeobuilder.database import DatabasePage, database_widgets
import zeobuilder.authors as authors

from molmod.descriptors import MolecularDescriptorTV1

import gtk


sql_create_table_objects = """
CREATE TABLE objects (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    zml LONGBLOB,
    size VARCHAR(10),
    geom_descr_int_id BIGINT UNSIGNED NOT NULL,
        INDEX (geom_descr_int_id),
    geom_descr_ext_id BIGINT UNSIGNED NOT NULL,
        INDEX (geom_descr_ext_id),
    graph_descr_int_id BIGINT UNSIGNED NOT NULL,
        INDEX (graph_descr_int_id),
    graph_descr_ext_id BIGINT UNSIGNED NOT NULL,
        INDEX (graph_descr_ext_id)
)
"""

class ObjectsDatabasePage(DatabasePage):
    order = 1
    name = "Objects"
    authors = [authors.toon_verstraelen]
    required_tables = set(["objects",
        MolecularDescriptorTV1.internal_table_name,
        MolecularDescriptorTV1.external_table_name,
    ])

    def __init__(self):
        DatabasePage.__init__(self)

        (
            self.list_store,
            self.list_view,
            self.bu_refresh,
            self.bu_drop,
            self.scrolled_window
        ) = database_widgets(
            connection=None,
            query="SELECT id, name, size FROM objects",
            column_headers=["Id", "Object", "Size"],
            drop_query_expr=(lambda row: "DROP FROM TABLE objects WHERE id==%i" % row[0]),
        )

        self.bu_add = gtk.Button(stock=gtk.STOCK_ADD)
        self.bu_open = gtk.Button(stock=gtk.STOCK_OPEN)

        self.button_box = gtk.HBox()
        self.button_box.pack_end(self.bu_refresh, expand=False, fill=True)
        self.button_box.pack_end(self.bu_drop, expand=False, fill=True)
        self.button_box.pack_end(self.bu_add, expand=False, fill=True)
        self.button_box.pack_end(self.bu_open, expand=False, fill=True)
        self.button_box.set_spacing(6)

        self.container = gtk.VBox()
        self.container.pack_start(self.scrolled_window, expand=True, fill=True)
        self.container.pack_start(self.button_box, expand=False, fill=False)
        self.container.set_border_width(6)
        self.container.set_spacing(6)

    def can_initialize(self):
        return True

    def initialize_tables(self, database):
        cursor = database.connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS objects")
        cursor.execute(sql_create_table_objects)
        cursor.execute("DROP TABLE IF EXISTS %s" % MolecularDescriptorTV1.internal_table_name)
        cursor.execute(MolecularDescriptorTV1.sql_create_internal_descriptor_table)
        cursor.execute("DROP TABLE IF EXISTS %s" % MolecularDescriptorTV1.external_table_name)
        cursor.execute(MolecularDescriptorTV1.sql_create_external_descriptor_table)
        cursor.close()

    def set_database(self, window, database):
        cursor = database.connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        if not self.required_tables.issubset(tables):
            return False
        else:
            self.list_store.refresh(connection=database.connection)
            DatabasePage.set_database(self, window, database)
            return True

    def unset_database(self):
        self.list_store.clear()
        self.bu_drop.set_sensitive(False)
        # TODO clean up unused descriptors
        DatabasePage.unset_database(self)

database_pages = {
    "objects": ObjectsDatabasePage()
}
