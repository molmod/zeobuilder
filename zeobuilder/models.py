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
#--


from zeobuilder.filters import FilterError
from zeobuilder.plugins import PluginNotFoundError
from zeobuilder import context

import gzip, bz2, gobject, os


__all__ = ["Model", "FilenameError"]


class FilenameError(Exception):
    def __init__(self, about, msg):
        self.about = about
        self.msg = msg

    def __str__(self):
        return "%s:\n%s" % (self.about, self.msg)


class Model(gobject.GObject):
    def __init__(self):
        gobject.GObject.__init__(self)
        self.root = []
        self.universe = None
        self.folder = None
        self.filename = None

        self.selection = []

    # selection stuff

    def add_to_selection(self, node):
        self.selection.append(node)
        context.application.cache.queue_invalidate()

    def remove_from_selection(self, node):
        self.selection.remove(node)
        context.application.cache.queue_invalidate()

    # internal functions

    def add_to_root(self, model_object):
        assert model_object.parent is None
        self.root.append(model_object)
        model_object.set_model(self, None, len(self.root)-1)

    def remove_from_root(self, model_object):
        model_object.unset_model()
        self.root.remove(model_object)

    def add_node(self, node, parent, index):
        pass

    def remove_node(self, node):
        pass

    def clear(self):
        while len(self.root) > 0:
            victim = self.root[0]
            self.remove_from_root(victim)
            victim.unparent()

    # file functions

    def file_new(self, universe, folder):
        self.file_close()
        self.add_to_root(universe)
        self.add_to_root(folder)
        self.universe = universe
        self.folder = folder
        self.emit("file-new")

    def file_open(self, filename):
        self.emit("file-opening")
        about = "Could not open file '%s'" % filename
        # first determine the extension
        last_dot = filename.rfind(".")
        if last_dot == -1:
            raise FilenameError(about, "Filename does not have an extension. Could not determine fileformat.")
        extension = filename[last_dot+1:]
        compression = ""
        if extension in ["gz", "bz2"]:
            compression = extension
            next_to_last_dot = filename[:last_dot].rfind(".")
            extension = filename[next_to_last_dot+1:last_dot]
        try:
            load_filter = context.application.plugins.get_load_filter(extension)
        except PluginNotFoundError:
            raise FilenameError(about, "Extension " + extension + " not recognized. Could not determine fileformat.")
        # then, depending on the extension, open the file with the correct function and compression
        if compression == "": file_object = file(filename, "r")
        elif compression == "gz": file_object = gzip.GzipFile(filename, "r", 9)
        elif compression == "bz2": file_object = bz2.BZ2File(filename, "r", 9)
        try:
            universe, folder = load_filter(file_object)
        except FilterError, e:
            file_object.close()
            e.about = about
            raise e
        file_object.close()
        # now we are (almost) sure the the opening of the file was a success
        self.file_close()
        # put the nodes in the tree
        self.add_to_root(universe)
        self.add_to_root(folder)
        self.universe = universe
        self.folder = folder
        self.filename = filename
        if not os.path.isabs(self.filename):
            self.filename = os.path.join(os.getcwd(), self.filename)
        self.filename = os.path.normpath(os.path.realpath(self.filename))
        self.emit("file-opened")

    def file_save(self, filename=None, nodes=None):
        self.emit("file-saving")
        about = "Could not save to file '%s'" % filename
        if filename is None:
            if self.filename is None:
                raise FilenameError(about, "One needs a filename to save to.")
            filename = self.filename
        # first determine the extension
        last_dot = filename.rfind(".")
        if last_dot == -1:
            raise FilenameError(about, "Filename does not have an extension. Could not determine fileformat.")
        extension = filename[last_dot+1:]
        compression = ""
        if extension in ["gz", "bz2"]:
            compression = extension
            next_to_last_dot = filename[:last_dot].rfind(".")
            extension = filename[next_to_last_dot+1:last_dot]
        try:
            dump_filter = context.application.plugins.get_dump_filter(extension)
        except PluginNotFoundError:
            raise FilenameError(about, "Extension " + extension + " not recognized. Could not determine fileformat.")

        # then, depending on the extension, create the file with the correct function and compression
        if compression == "": file_object = file(filename, "w")
        elif compression == "gz": file_object = gzip.GzipFile(filename, "w", 9)
        elif compression == "bz2": file_object = bz2.BZ2File(filename, "w", 9)
        try:
            dump_filter(file_object, self.universe, self.folder, nodes)
        except FilterError, e:
            file_object.close()
            e.about = about
            raise e
        file_object.close()
        self.filename = filename
        self.emit("file-saved")

    def file_close(self):
        self.universe = None
        self.folder = None
        self.filename = None
        self.clear()
        self.emit("file-closed")


gobject.signal_new("file-new", Model, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
gobject.signal_new("file-opened", Model, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
gobject.signal_new("file-opening", Model, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
gobject.signal_new("file-closed", Model, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
gobject.signal_new("file-saved", Model, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
gobject.signal_new("file-saving", Model, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())


