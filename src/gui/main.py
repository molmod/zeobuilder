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
from zeobuilder.gui.simple import nosave_cancel_save_question
from zeobuilder.gui.glade_wrapper import GladeWrapper
from zeobuilder.gui.drawing_area import DrawingArea
from zeobuilder.filters import run_file_dialog

import gtk, os


__all__ = ["Main"]


class Main(GladeWrapper):
    def __init__(self):
        model = context.application.model
        model.connect("file-new", self.on_filename_changed)
        model.connect("file-opened", self.on_filename_changed)
        model.connect("file-saved", self.on_filename_changed)

        context.application.action_manager.connect("model-changed", self.on_model_changed)

        GladeWrapper.__init__(self, "zeobuilder.glade", "wi_main", "window")
        self.init_callbacks(self.__class__)
        self.init_proxies(["sw_nodes", "hp_main", "vb_main", "menubar"])

        # add model gui:
        self.init_tree_view()
        self.init_drawing_area()

    def init_tree_view(self):
        self.filter_active = False
        self.filter_expression = "True"

        # tree related widgets:
        self.tree_view = gtk.TreeView(context.application.model)
        self.sw_nodes.add(self.tree_view)
        self.tree_view.set_headers_visible(False)
        self.tree_view.connect("row-collapsed", self.on_row_collapsed)
        self.tree_view.connect("row-expanded", self.on_row_expanded)
        self.tree_view.connect("button-press-event", self.on_tree_view_button_press_event)

        self.tree_selection = self.tree_view.get_selection()
        self.tree_selection.set_mode(gtk.SELECTION_MULTIPLE)
        self.tree_selection.set_select_function(self.select_path)

        renderer_pixbuf = gtk.CellRendererPixbuf()
        self.column = gtk.TreeViewColumn()
        self.column.pack_start(renderer_pixbuf, expand=False)
        def render_icon(column, cell, model, iter):
            cell.set_property('pixbuf', model.get_value(iter, 0).icon)
        self.column.set_cell_data_func(renderer_pixbuf, render_icon)

        renderer_text = gtk.CellRendererText()
        self.column.pack_start(renderer_text, expand=False)
        def render_name(column, cell, model, iter):
            cell.set_property('text', model.get_value(iter, 0).get_name())
        self.column.set_cell_data_func(renderer_text, render_name)
        self.tree_view.append_column(self.column)

    def init_drawing_area(self):
        self.drawing_area = DrawingArea()
        self.hp_main.pack2(self.drawing_area, resize=True, shrink=False)

    # internal functions
    def update_window_title(self):
        temp = "%s %s: " % (context.title, context.version)
        filename = context.application.model.filename
        if filename is None:
            temp = temp + "(no file)"
        else:
            temp = temp + "[%s]" % filename
        if context.application.action_manager.model_changed():
            temp = temp + " *"
        self.window.set_title(temp)

    def file_close_check(self):
        if context.application.action_manager.model_changed():
            result = nosave_cancel_save_question("The current file has not been saved. If you don't save the file, all changes will be lost. Do you want to save the file?")
            if (result == gtk.RESPONSE_CANCEL) or (result == gtk.RESPONSE_DELETE_EVENT):
                # No close
                return False
            elif result == gtk.RESPONSE_OK:
                # Try to save, but if not saved, no close
                return self.file_save()
        # Close is accepted, no need to save
        return True

    def get_current_directory(self):
        name = context.application.model.filename
        if name is not None:
            return os.path.dirname(name)

    # high level gui functions
    def file_new(self, universe, folder):
        if self.file_close_check():
            context.application.model.file_close()
            context.application.model.file_new(universe, folder)
            self.drawing_area.scene.reset_view()

    def file_open(self):
        if self.file_close_check():
            if run_file_dialog(
                context.application.file_open_dialog,
                context.application.model.file_open
            ):
                self.drawing_area.scene.reset_view()

    def file_save(self):
        if context.application.model.filename is None:
            return self.file_save_as()
        else:
            context.application.model.file_save()
            return True

    def file_save_as(self):
        run_file_dialog(
            context.application.file_save_dialog,
            context.application.model.file_save
        )

    def file_close(self):
        if self.file_close_check():
            context.application.model.file_close()
            return True
        else:
            return False

    def file_quit(self):
        "The user stops the program with the close item in the menu."
        if self.file_close():
            gtk.main_quit()

    def on_window_delete_event(self, widget, event):
        "The user closes the window."
        if self.file_close():
            gtk.main_quit()
        else:
            return True

    # INTERNAL handlers

    def on_filename_changed(self, model):
        self.update_window_title()

    def on_model_changed(self, action_manager):
        self.update_window_title()

    # selection stuff

    def select_path(self, path):
        node = context.application.model[path][0]
        is_selected = self.tree_selection.path_is_selected(path)
        try:
            if not (
                is_selected or
                (not self.filter_active) or
                eval(self.filter_expression)
            ): return False
        except Exception, e:
            ok_error("An error occured while evaluating the filter expression. This is probably due to a mistake in the expression you entered. The selection filter will be deactivated.\n\n" + str(e.__class__) + ": " + str(e))
            self.filter_active = False
        node.set_selected(not is_selected)
        return True

    def toggle_selection(self, node, on=None):
        if on is None: on = not node.selected
        if on:
            if not self.filter_active or eval(self.filter_expression):
                if node.parent is not None:
                    self.tree_view.expand_to_path(
                        context.application.model.get_path(node.parent.iter)
                    )
                self.tree_selection.select_iter(node.iter)
        else:
            self.tree_selection.unselect_iter(node.iter)

    def select_nodes(self, nodes):
        self.tree_selection.unselect_all()
        for node in nodes:
            self.toggle_selection(node, on=True)

    def on_row_collapsed(self, tree_view, iter, path):
        context.application.model[iter][0].set_expanded(False)

    def on_row_expanded(self, tree_view, iter, path):
        context.application.model[iter][0].set_expanded(True)

    # popup menu with actions

    def on_tree_view_button_press_event(self, tree_view, event):
        # Only do something with the right mouse button.
        tree_view.grab_focus()
        temp = tree_view.get_path_at_pos(int(event.x), int(event.y))
        if temp is None: return False
        path, col, cellx, celly = temp
        if event.button == 3:
            if not self.tree_selection.path_is_selected(path):
                tree_view.set_cursor(path, col, 0)
                context.application.cache.emit_invalidate()
            context.application.menu.popup(event.button, gtk.get_current_event_time())
            return True
        elif event.button == 1:
            if event.type == gtk.gdk._2BUTTON_PRESS:
                if self.tree_view.row_expanded(path):
                    self.tree_view.collapse_row(path)
                else:
                    self.tree_view.expand_row(path, False)
                return True
        return False
