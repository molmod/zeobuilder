# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 Toon Verstraelen <Toon.Verstraelen@UGent.be>
#
# This file is part of Zeobuilder.
#
# Zeobuilder is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
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
from zeobuilder.models import Model
from zeobuilder.filters import run_file_dialog
import zeobuilder.authors as authors

import gtk, os, copy


class FileNew(Immediate):
    description = "Create a new file"
    menu_info = MenuInfo("default/_File:default", "_New", ord("n"), image_name=gtk.STOCK_NEW, order=(0, 0, 0, 0))
    repeatable = False
    authors = [authors.toon_verstraelen]

    def do(self):
        Universe = context.application.plugins.get_node("Universe")
        universe = Universe(axes_visible=False)
        Folder = context.application.plugins.get_node("Folder")
        folder = Folder()
        context.application.main.file_new(universe, folder)


class FileOpen(Immediate):
    description = "Open a file"
    menu_info = MenuInfo("default/_File:default", "_Open", ord("o"), image_name=gtk.STOCK_OPEN, order=(0, 0, 0, 1))
    repeatable = False
    authors = [authors.toon_verstraelen]

    def do(self):
        context.application.main.file_open()


class FileSave(Immediate):
    description = "Save the current file"
    menu_info = MenuInfo("default/_File:default", "_Save", ord("s"), image_name=gtk.STOCK_SAVE, order=(0, 0, 0, 2))
    repeatable = False
    authors = [authors.toon_verstraelen]

    def do(self):
        context.application.main.file_save()


class FileSaveAs(Immediate):
    description = "Save the current file under a new name"
    menu_info = MenuInfo("default/_File:default", "Save _as", ord("s"), True, True, image_name=gtk.STOCK_SAVE_AS, order=(0, 0, 0, 3))
    repeatable = False
    authors = [authors.toon_verstraelen]

    def do(self):
        context.application.main.file_save_as()


class FileImport(Immediate):
    description = "Import a file in the current model"
    menu_info = MenuInfo("default/_File:impexp", "_Import", order=(0, 0, 1, 0))
    repeatable = False
    authors = [authors.toon_verstraelen]

    def do(self):
        def file_import(filename):
            tmp_model = Model()
            tmp_model.file_open(filename)

            if len(tmp_model.universe.children) > 0:
                Frame = context.application.plugins.get_node("Frame")
                root_frame = Frame(name=os.path.basename(filename))
                tmp = copy.copy(tmp_model.universe.children)
                while len(tmp_model.universe.children) > 0:
                    tmp_model.universe.remove(tmp_model.universe.children[0])
                for node in tmp:
                    root_frame.add(node)
                del tmp
                context.application.model.universe.add(root_frame)

            if len(tmp_model.folder.children) > 0:
                Folder = context.application.plugins.get_node("Folder")
                root_folder = Folder(name=os.path.basename(filename))
                tmp = copy.copy(tmp_model.folder.children)
                while len(tmp_model.folder.children) > 0:
                    tmp_model.universe.remove(tmp_model.folder.children[0])
                for node in tmp:
                    root_folder.add(node)
                del tmp
                context.application.model.folder.add(root_folder)
                tmp_model.file_close()

        run_file_dialog(context.application.file_import_dialog, file_import)


class FileExport(Immediate):
    description = "Export the selection to a file"
    menu_info = MenuInfo("default/_File:impexp", "_Export", order=(0, 0, 1, 1))
    repeatable = False
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        if not Immediate.analyze_selection(): return False
        if len(context.application.cache.nodes) == 0: return False
        return True

    def do(self):
        run_file_dialog(
            context.application.file_export_dialog,
            context.application.model.file_save,
            context.application.cache.nodes
        )


class FileQuit(Immediate):
    description = "Quit zeobuilder"
    menu_info = MenuInfo("default/_File:quit", "_Quit", ord("q"), image_name=gtk.STOCK_QUIT, order=(0, 0, 2, 0))
    repeatable = False
    authors = [authors.toon_verstraelen]

    def do(self):
        context.application.main.file_quit()


actions = {
    "FileNew": FileNew,
    "FileOpen": FileOpen,
    "FileSave": FileSave,
    "FileSaveAs": FileSaveAs,
    "FileImport": FileImport,
    "FileExport": FileExport,
    "FileQuit": FileQuit,
}

