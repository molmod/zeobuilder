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
from zeobuilder.actions.composed import Immediate, ImmediateWithMemory, Parameters
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.nodes.meta import Property
from zeobuilder.nodes.model_object import ModelObject, ModelObjectInfo
from zeobuilder.plugins import PluginCategory
from zeobuilder.gui.fields_dialogs import DialogFieldInfo, FieldsDialogSimple
from zeobuilder.gui.simple import yes_no_question
from zeobuilder.database import database_widgets, DatabasePage
import zeobuilder.gui.fields as fields
import zeobuilder.actions.primitive as primitive

import gtk

import os, pwd


class DatabaseError(Exception):
    pass


class Database(ModelObject):
    info = ModelObjectInfo("plugins/core/database.svg", default_action_name="ShowDatabaseWindow")
    required_modules = ["MySQLdb"]

    #
    # State
    #

    def initnonstate(self):
        self.connection = None
        self.password = None

    #
    # Properties
    #

    def set_host(self, host):
        if not self.get_connected():
            self.host = host
        else:
            raise DatabaseError("The host can not be set while being connected.")

    def set_port(self, port):
        if not self.get_connected():
            self.port = port
        else:
            raise DatabaseError("The port can not be set while being connected.")

    def set_user(self, user):
        if not self.get_connected():
            self.user = user
        else:
            raise DatabaseError("The user can not be set while being connected.")

    def set_name(self, name):
        if not self.get_connected():
            self.name = name
        else:
            raise DatabaseError("The name can not be set while being connected.")

    properties = [
        Property("host", None, lambda self: self.host, set_host),
        Property("port", None, lambda self: self.port, set_port),
        Property("user", None, lambda self: self.user, set_user),
    ]

    #
    # Dialog fields (see action EditProperties)
    #

    dialog_fields = set([
        DialogFieldInfo("Basic", (0, 4), fields.read.Label(
            label_text="Host",
            attribute_name="host",
        )),
        DialogFieldInfo("Basic", (0, 5), fields.read.Label(
            label_text="Port",
            attribute_name="port",
        )),
        DialogFieldInfo("Basic", (0, 6), fields.read.Label(
            label_text="User",
            attribute_name="user",
        )),
        DialogFieldInfo("Basic", (0, 7), fields.read.Label(
            label_text="Connected",
            attribute_name="connected",
        )),
    ])

    #
    # Tree
    #

    def unset_model(self):
        if self.get_connected():
            self.disconnect()
        ModelObject.unset_model(self)

    #
    # Database stuff
    #

    def connect(self, password):
        assert not self.get_connected()

        import MySQLdb
        self.connection = MySQLdb.connect(
            host=self.host,
            user=self.user,
            passwd=password,
            port=self.port
        )

        database_exists = False
        cursor = self.connection.cursor()
        cursor.execute("SHOW DATABASES")
        for (existing_name,) in cursor.fetchall():
            if existing_name == self.name:
                database_exists = True
                break

        if not database_exists:
            cursor.execute("CREATE DATABASE %s" % self.name)
        cursor.execute("USE %s" % self.name)
        self.password = password

    def disconnect(self):
        assert self.get_connected()
        self.connection.close()
        self.connection = None

    def get_connected(self):
        return self.connection is not None


class DatabaseWindow(object):
    def __init__(self):
        self.window = gtk.Window()
        self.window.hide()
        self.window.set_title("Database window")
        self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.window.connect("delete-event", self.on_window_delete_event)
        self.window.set_size_request(400, 300)

        menu_bar = gtk.MenuBar()
        mi_database = gtk.MenuItem("_Database")
        menu_bar.append(mi_database)
        self.menu_database = gtk.Menu()
        mi_database.set_submenu(self.menu_database)

        self.notebook = gtk.Notebook()
        self.notebook.set_border_width(6)

        vbox = gtk.VBox()
        vbox.pack_start(menu_bar, expand=False, fill=False)
        vbox.pack_start(self.notebook, expand=True, fill=True)
        self.window.add(vbox)

        self.database = None
        self.pages = []

    def set_database(self, database):
        active_pages = 0
        for page in self.pages:
            if page.set_database(self, database):
                active_pages += 1
        if active_pages > 0:
            self.database = database
            self.window.show_all()

    def unset_database(self, hide=True):
        for page in self.pages:
            if page.active:
                page.unset_database()
        self.database = None
        if hide:
            self.window.hide()

    def on_window_delete_event(self, window, event):
        self.unset_database()
        return True

    def init_pages(self, pages):
        self.pages = pages.values()
        self.pages.sort(key=lambda p: p.order)
        for page in self.pages:
            if page.can_initialize is not None:
                mi_initialize = gtk.MenuItem("Initialize '%s' tables" % page.name)
                self.menu_database.append(mi_initialize)
                mi_initialize.connect("activate", self.on_mi_initialize_activate, page)
                mi_initialize.connect("expose-event", self.on_mi_initialize_expose, page)

    def on_mi_initialize_activate(self, mi, page):
        if self.database is not None:
            if page.active:
                if yes_no_question(
                    "Remove existing tables",
                    "The page '%s' is already active and re-initializing it will clear all data from the related tables." % page.name
                ) != gtk.RESPONSE_YES:
                    return
            page.initialize_tables(self.database)
            if not page.active:
                if not page.set_database(self, self.database):
                    raise DatabaseError("Can not create the database page after initializing the tables.")

    def on_mi_initialize_expose(self, mi, event, page):
        if event.count == 0:
            mi.set_sensitive(page.can_initialize())



database_window = DatabaseWindow()


class StatusDatabasePage(DatabasePage):
    order = 0
    name = "Status"
    required_modules = ["MySQLdb"]

    def __init__(self):
        DatabasePage.__init__(self)
        self.name_label = gtk.Label()
        self.name_label.set_alignment(0.0, 0.5)

        (
            self.list_store,
            self.list_view,
            self.bu_refresh,
            self.bu_drop,
            self.scrolled_window
        ) = database_widgets(
            connection=None,
            query="SHOW TABLES",
            column_headers=["Table"],
            drop_query_expr=None#(lambda row: "DROP TABLE %s" % row[0]),
        )

        self.button_box = gtk.HBox()
        self.button_box.pack_end(self.bu_refresh, expand=False, fill=True)
        self.button_box.set_spacing(6)

        self.container = gtk.VBox()
        self.container.pack_start(self.name_label, expand=False, fill=False)
        self.container.pack_start(self.scrolled_window, expand=True, fill=True)
        self.container.pack_start(self.button_box, expand=False, fill=False)
        self.container.set_border_width(6)
        self.container.set_spacing(6)

    def set_database(self, window, database):
        self.name_label.set_markup("<b>Database name:</b> %s" % database.name)
        self.list_view.set_model(None) # TODO: UGLY HACK
        self.list_store.refresh(connection=database.connection)
        self.list_view.set_model(self.list_store) # TODO: UGLY HACK
        DatabasePage.set_database(self, window, database)
        return True

    def unset_database(self):
        self.list_store.clear()
        DatabasePage.unset_database(self)


class NewDatabase(ImmediateWithMemory):
    description = "Create a new database"
    menu_info = MenuInfo("default/_Object:tools/_Database:default", "_New database connection", image_name="plugins/core/database.svg", order=(0, 4, 1, 8, 0, 0))
    required_modules = ["MySQLdb"]

    parameters_dialog = FieldsDialogSimple(
        "Database connection",
        fields.group.Table(fields=[
            fields.faulty.Name(
                label_text="Hostname",
                attribute_name="host",
            ),
            fields.faulty.Int(
                label_text="Port",
                attribute_name="port",
                minimum=0,
                maximum=65535,
            ),
            fields.faulty.Name(
                label_text="User",
                attribute_name="user",
            ),
            fields.faulty.Name(
                label_text="Database name",
                attribute_name="name",
            ),
            fields.optional.CheckOptional(fields.faulty.Password(
                label_text="Immediatly login with password",
                attribute_name="password",
            )),
        ]),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK))
    )

    @classmethod
    def default_parameters(cls):
        parameters = Parameters()
        parameters.host = ""
        parameters.port = 3306
        parameters.user = pwd.getpwuid(os.getuid()).pw_name
        parameters.name = "zeobuilder"
        parameters.password = ""
        return parameters

    def do(self):
        connection = Database(
            host=self.parameters.host,
            port=self.parameters.port,
            user=self.parameters.user,
            name=self.parameters.name,
        )
        if self.parameters.password is not None:
            connection.connect(self.parameters.password)
        parent = context.application.cache.node
        Folder = context.application.plugins.get_node("Folder")
        if parent is None or not isinstance(parent, Folder):
            parent = context.application.model.folder
        primitive.Add(connection, parent)


class ConnectToDatabase(ImmediateWithMemory):
    description = "Connect to the selected database"
    menu_info = MenuInfo("default/_Object:tools/_Database:default", "_Connect", order=(0, 4, 1, 8, 0, 1))
    store_last_parameters = False
    required_modules = ["MySQLdb"]

    parameters_dialog = FieldsDialogSimple(
        "Connect to database",
        fields.faulty.Password(
                label_text="Login with password",
                attribute_name="password",
                show_popup=False,
        ),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK))
    )

    @staticmethod
    def analyze_selection(parameters=None):
        # A) calling ancestor
        if not ImmediateWithMemory.analyze_selection(parameters): return False
        # B) validating
        connection = context.application.cache.node
        if not isinstance(connection, Database): return False
        if connection.get_connected(): return False
        # C) passed all tests:
        return True

    @classmethod
    def default_parameters(cls):
        parameters = Parameters()
        parameters.password = ""
        return parameters

    def ask_parameters(self):
        connection = context.application.cache.node
        if connection.password is not None:
            self.parameters.password = connection.password
        ImmediateWithMemory.ask_parameters(self)

    def do(self):
        context.application.cache.node.connect(self.parameters.password)


class DisconnectFromDatabase(Immediate):
    description = "Disconnect from the selected database"
    menu_info = MenuInfo("default/_Object:tools/_Database:default", "_Disconnect", order=(0, 4, 1, 8, 0, 2))
    required_modules = ["MySQLdb"]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        connection = context.application.cache.node
        if not isinstance(connection, Database): return False
        if not connection.get_connected(): return False
        # C) passed all tests:
        return True

    def do(self):
        context.application.cache.node.disconnect()


class ShowDatabaseWindow(Immediate):
    description = "Show the database window of the selected database"
    menu_info = MenuInfo("default/_Object:tools/_Database:default", "_Show database window", order=(0, 4, 1, 8, 0, 3))
    required_modules = ["MySQLdb"]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        if not isinstance(context.application.cache.node, Database): return False
        # C) passed all tests:
        return True

    def do(self):
        database_window.unset_database(hide=False)
        database = context.application.cache.node
        if not database.get_connected():
            ConnectToDatabase()
        database_window.set_database(context.application.cache.node)


plugin_categories = {
    "database_page": PluginCategory("database_page", "database_pages", database_window.init_pages)
}


database_pages = {
    "StatusDatabasePage": StatusDatabasePage(),
}


nodes = {
    "Database": Database
}


actions = {
    "NewDatabase": NewDatabase,
    "ConnectToDatabase": ConnectToDatabase,
    "DisconnectFromDatabase": DisconnectFromDatabase,
    "ShowDatabaseWindow": ShowDatabaseWindow,
}
