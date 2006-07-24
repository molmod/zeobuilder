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

# this file contains a base class for all the objects that represent
# a gtk window, dialog, or anything else you can load from a glade file


from zeobuilder import context

import new, types, os
import gtk, gtk.glade


__all__ = ["GladeWrapper", "GladeWrapperError"]


class GladeWrapperError(Exception):
    pass


class GladeWrapper(object):
    def __init__(self, glade_file, widget, widget_dict_name=None):
        "This method loads the widget from the glade XML file"
        # widget_dict_name is the name of the attribute to which the widget
        # will be assigned. if left to none the widget name will be used

        # load the glade file
        for directory in context.share_dirs:
            if os.path.isdir(directory):
                self.widgets = gtk.glade.XML(os.path.join(directory, glade_file), widget)
                break

        # load the requested widget as widget_dict_name
        if widget_dict_name == None:
            widget_dict_name = widget
        widget = self.widgets.get_widget(widget)
        if widget is None:
            raise GladeWrapperError, "The widget (" + widget + ") passed to the constructor does not exist."
        else:
            self.__dict__[widget_dict_name] = widget

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
            if self.widgets.get_widget(widget_name) == None:
                raise GladeWrapperError, "The widget (" + widget_name + ") in the widgets_list parameter does not exist."
            else:
                self.__dict__[widget_name] = self.widgets.get_widget(widget_name)

