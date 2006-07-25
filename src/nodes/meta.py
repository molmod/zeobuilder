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

import gobject

import copy

__all__ = ["NodeClass", "Property", "PublishedProperties", "DialogFieldInfo"]


class NodeClass(gobject.GObjectMeta):
    def __init__(cls, name, bases, dict):
        type.__init__(name, bases, dict)
        # create an attribute published_properties if it doesn't exist yet
        if "published_properties" not in dict:
            cls.published_properties = PublishedProperties()
        for pname, published_property in cls.published_properties.iteritems():
            if published_property.signal:
                signal_name = "on-%s-changed" % pname
                published_property.signal_name = signal_name
                gobject.signal_new(signal_name, cls, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
        # inherit all the properties from the base classes
        for base in bases:
            if hasattr(base, "published_properties"):
                for name, published_property in base.published_properties.iteritems():
                   cls.published_properties[name] = copy.copy(published_property)
        # assign the derived default, get and set functions
        for published_property in cls.published_properties.itervalues():
           if callable(published_property.default) and published_property.default.__name__ in dict:
               published_property.set_default(dict[published_property.default.__name__])
           if published_property.get.__name__ in dict:
               published_property.get = dict[published_property.get.__name__]
           if published_property.set is not None and published_property.set.__name__ in dict:
               published_property.set = dict[published_property.set.__name__]
        # merge the edit fields with those from the ancestors
        if not hasattr(cls, "dialog_fields"):
            cls.dialog_fields = set([])
        for base in bases:
            if hasattr(base, "dialog_fields"):
                cls.dialog_fields |= base.dialog_fields


class Property(object):
    def __init__(self, default, get, set, signal=False):
        self.set_default(default)
        self.get = get
        if signal:
            self.set_function = set
            self.set = self.set_wrapper
        else:
            self.set = set
        self.signal = signal
        self.signal_name = None

    def set_wrapper(self, node, value):
        node.emit(self.signal_name)
        self.set_function(node, value)

    def set_default(self, default):
        self.default = default
        if callable(self.default):
            self.get_default = self.get_default_callable
        else:
            self.get_default = self.get_default_variable

    def get_default_callable(self, object):
        return self.default(object)

    def get_default_variable(self, object):
        return copy.deepcopy(self.default)


class PublishedProperties(dict):
    def get_name_value_dict(self, node):
        return dict(
            (name, published_property.get(node))
            for name, published_property
            in self.iteritems()
        )


class DialogFieldInfo(object):
    def __init__(self, category, order, field):
        self.category = category
        self.order = order
        self.field = field
