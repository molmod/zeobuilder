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


from zeobuilder import context

import gtk

import os


__all__= [
    "FilterError", "LoadFilter", "DumpFilter"
]


class FilterError(Exception):
    def __init__(self, msg):
        self.msg = msg
        self.about = None
        Exception.__init__(self, msg)

    def __str__(self):
        if self.about is None:
            return self.msg
        else:
            return "%s:\n%s" % (self.about, self.msg)


class Filter(object):
    def __init__(self, description):
        self.description = description


class LoadFilter(Filter):
    def __call__(self, f):
        raise NotImplementedError()


class DumpFilter(Filter):
    def __call__(self, f, universe, folder, nodes=None):
        raise NotImplementedError()


class Indenter(object):
    def __init__(self, stream, indent_string=" "):
        self.stream = stream
        self.indent = 0
        self.indent_string = indent_string
        self.new_line = True

    def write_line(self, line, indent=0):
        if not self.new_line:
            self.stream.write("\n")
            #sys.stdout.write("\n")
        if indent >= 0:
            self.stream.write(self.indent_string*self.indent)
            #sys.stdout.write(self.indent_string*self.indent)
        self.indent += indent
        if self.indent < 0: self.indent = 0
        if indent < 0: self.stream.write(self.indent_string*self.indent)
        self.stream.write(line)
        #sys.stdout.write(line)
        self.stream.write("\n")
        #sys.stdout.write("\n")
        self.new_line = True

    def write(self, string, line_break=False):
        if self.new_line:
            self.stream.write(self.indent_string*self.indent)
            #sys.stdout.write(self.indent_string*self.indent)
        self.stream.write(string)
        if line_break:
            self.stream.write("\n")
            #sys.stdout.write("\n")
        self.new_line = line_break


def init_load_filters(load_filters):
    all_load_ff = gtk.FileFilter()
    all_load_ff.set_name("All known formats")
    load_ffs = [all_load_ff]
    for extension, load_filter in load_filters.iteritems():
        all_load_ff.add_pattern("*.%s" % extension)
        all_load_ff.add_pattern("*.%s.gz" % extension)
        all_load_ff.add_pattern("*.%s.bz2" % extension)

        ff = gtk.FileFilter()
        ff.set_name(load_filter.description)
        ff.add_pattern("*.%s" % extension)
        ff.add_pattern("*.%s.gz" % extension)
        ff.add_pattern("*.%s.bz2" % extension)
        load_ffs.append(ff)

    # create file open dialog:
    file_open_dialog = gtk.FileChooserDialog(
        "Open file",
        context.parent_window,
        gtk.FILE_CHOOSER_ACTION_OPEN,
        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK)
    )
    file_open_dialog.set_default_response(gtk.RESPONSE_OK)
    for ff in load_ffs:
        file_open_dialog.add_filter(ff)
    context.application.file_open_dialog = file_open_dialog

    # create file import dialog:
    file_import_dialog = gtk.FileChooserDialog(
        "Import file",
        context.parent_window,
        gtk.FILE_CHOOSER_ACTION_OPEN,
        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK)
    )
    file_import_dialog.set_default_response(gtk.RESPONSE_OK)
    for ff in load_ffs:
        file_import_dialog.add_filter(ff)
    context.application.file_import_dialog = file_import_dialog


def init_dump_filters(dump_filters):
    all_dump_ff = gtk.FileFilter()
    all_dump_ff.set_name("All known formats")
    dump_ffs = [all_dump_ff]
    for extension, dump_filter in dump_filters.iteritems():
        all_dump_ff.add_pattern("*.%s" % extension)
        all_dump_ff.add_pattern("*.%s.gz" % extension)
        all_dump_ff.add_pattern("*.%s.bz2" % extension)

        ff = gtk.FileFilter()
        ff.set_name(dump_filter.description)
        ff.add_pattern("*.%s" % extension)
        ff.add_pattern("*.%s.gz" % extension)
        ff.add_pattern("*.%s.bz2" % extension)
        dump_ffs.append(ff)

    # create file save dialog:
    file_save_dialog = gtk.FileChooserDialog(
        "Save file as",
        context.parent_window,
        gtk.FILE_CHOOSER_ACTION_SAVE,
        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK)
    )
    file_save_dialog.set_default_response(gtk.RESPONSE_OK)
    for ff in dump_ffs:
        file_save_dialog.add_filter(ff)
    context.application.file_save_dialog = file_save_dialog

    # create file export dialog:
    file_export_dialog = gtk.FileChooserDialog(
        "Export file",
        context.parent_window,
        gtk.FILE_CHOOSER_ACTION_SAVE,
        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK)
    )
    file_export_dialog.set_default_response(gtk.RESPONSE_OK)
    for ff in dump_ffs:
        file_export_dialog.add_filter(ff)
    context.application.file_export_dialog = file_export_dialog


def run_file_dialog(file_dialog, file_function, *args):
    from zeobuilder.models import FilenameError
    from zeobuilder.gui.simple import ok_error
    success = False
    current_dir = context.application.main.get_current_directory()
    if current_dir is not None:
        file_dialog.set_current_folder(current_dir)
    if file_dialog.get_property("action") == gtk.FILE_CHOOSER_ACTION_SAVE:
        current_filename = context.application.model.filename
        if current_filename is not None:
            file_dialog.set_current_name(os.path.basename(current_filename))
    while file_dialog.run() == gtk.RESPONSE_OK:
        filename = file_dialog.get_filename()
        try:
            file_function(filename, *args)
            success = True
            break
        except (FilterError, FilenameError), e:
            ok_error(str(e))
    file_dialog.hide()
    return success


