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

# this file contains a base class for all the objects that represent
# a gtk window, dialog, or anything else you can load from a glade file


from zeobuilder import context
from zeobuilder.application import TestApplication

import new, types
import gtk, gtk.glade, gobject


__all__ = ["GladeWrapper", "GladeWrapperError"]


class GladeWrapperError(Exception):
    pass


class GladeWrapper(object):
    def __init__(self, glade_file, widget_name, widget_dict_name=None):
        "This method loads the widget from the glade XML file"
        # widget_dict_name is the name of the attribute to which the widget
        # will be assigned. if left to none the widget name will be used

        # load the glade file
        self.widgets = gtk.glade.XML(context.get_share_filename(glade_file), widget_name)
        if self.widgets is None:
            raise GladeWrapperError("Could not find glade file %s in the share directory %s." % (glade_file, context.share_dir))

        # load the requested widget as widget_dict_name
        if widget_dict_name is None:
            widget_dict_name = widget_name
        widget = self.widgets.get_widget(widget_name)
        if widget is None:
            raise GladeWrapperError, "The widget '%s' passed to the constructor does not exist." % widget_name
        else:
            self.__dict__[widget_dict_name] = widget

        # In case of a dialog in a test application, connect to a signal to
        # close immedeately.
        if widget_dict_name == "dialog":
            widget.connect("show", self.on_dialog_show)

    def on_dialog_show(self, dialog):
        def response():
            dialog.response(gtk.RESPONSE_CLOSE)
        if isinstance(context.application, TestApplication):
            gobject.idle_add(response)

    def init_callbacks(self, descendant_class):
        "This method connects the events automatically, based on descendant_class.__dict__"
        callbacks = {}

        # find and store methods as bound callbacks
        class_methods = descendant_class.__dict__
        for method_name in class_methods.keys():
            method = class_methods[method_name]
            if type(method) == types.FunctionType:
                callbacks[method_name] = new.instancemethod(method, self, descendant_class)
        # connect signal
        self.widgets.signal_autoconnect(callbacks)

    def init_proxies(self, widgets_list):
        "This method will create the atributes in self that refer to the widgets passed in the wedgets_list as as list of strings."
        for widget_name in widgets_list:
            if self.widgets.get_widget(widget_name) is None:
                raise GladeWrapperError, "The widget (" + widget_name + ") in the widgets_list parameter does not exist."
            else:
                self.__dict__[widget_name] = self.widgets.get_widget(widget_name)


