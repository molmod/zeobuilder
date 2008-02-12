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
# Contact information:
#
# Supervisors
#
# Prof. Dr. Michel Waroquier and Prof. Dr. Ir. Veronique Van Speybroeck
#
# Center for Molecular Modeling
# Ghent University
# Proeftuinstraat 86, B-9000 GENT - BELGIUM
# Tel: +32 9 264 65 59
# Fax: +32 9 264 65 60
# Email: Michel.Waroquier@UGent.be
# Email: Veronique.VanSpeybroeck@UGent.be
#
# Author
#
# Ir. Toon Verstraelen
# Center for Molecular Modeling
# Ghent University
# Proeftuinstraat 86, B-9000 GENT - BELGIUM
# Tel: +32 9 264 65 56
# Email: Toon.Verstraelen@UGent.be
#
# --


import gobject

import copy


__all__ = ["NodeClass", "Property", "DialogFieldInfo"]


class NodeClass(gobject.GObjectMeta):
    def __init__(cls, name, bases, dict):
        gobject.GObjectMeta.__init__(cls, name, bases, dict)

        # merge all the properties from the base classes
        properties = []
        properties_by_name = {}
        for base in bases + (cls,):
            if hasattr(base, "properties"):
                for p in base.properties:
                    existing_p = properties_by_name.get(p.name)
                    if existing_p is None:
                        tmp = copy.copy(p)
                        properties.append(tmp)
                        properties_by_name[p.name] = tmp
                    else:
                        if existing_p.default is not None:
                            p.default = existing_p.default
                        if existing_p.fset is not None:
                            p.fset = existing_p.fset
                        if existing_p.fget is not None:
                            p.fget = existing_p.fget
        for p in properties:
            p.signal = False
            p.signal_name = None
        if "properties" in dict:
            for p in cls.properties:
                properties_by_name[p.name].signal = p.signal
        cls.properties = properties
        cls.properties_by_name = properties_by_name

        # create signals
        for p in cls.properties:
            if p.signal:
                # a signal is only created when explicitly mentioned in the
                # class itself (and not when it is inherited).
                p.signal_name = ("on-%s-changed" % p.name).replace("_", "-")
                # avoid signals to be created twice. This happes when a plugin
                # is loaded twice. (for example in the unittests)
                if gobject.signal_lookup(p.signal_name, cls) == 0:
                    gobject.signal_new(p.signal_name, cls, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())

        # assign the derived default, get and set functions
        for p in cls.properties:
            # default
            if p.fdefault is not None:
                derived_fdefault = dict.get(p.fdefault.__name__)
                if derived_fdefault is not None:
                    p.fdefault = derived_fdefault
            # get
            derived_fget = dict.get(p.fget.__name__)
            if derived_fget is not None:
                p.fget = derived_fget
            # set
            derived_fset = dict.get(p.fset.__name__)
            if derived_fset is not None:
                p.fset = derived_fset

        # merge the edit fields with those from the ancestors
        if not hasattr(cls, "dialog_fields"):
            cls.dialog_fields = set([])
        for base in bases:
            if hasattr(base, "dialog_fields"):
                cls.dialog_fields |= base.dialog_fields

        # create a nodeinfo if needed
        if not hasattr(cls, "info"):
            from node import NodeInfo
            cls.info = NodeInfo()
        # merge the node info with that from the ancestors
        d = {}
        for base in bases:
            if hasattr(base, "info"):
                d.update(base.info.__dict__)
        d.update(cls.info.__dict__)
        cls.info.__dict__ = d


class Property(object):
    def __init__(self, name, default, fget, fset, signal=False):
        self.name = name
        if callable(default):
            self.fdefault = default
            self.vdefault = None
        else:
            self.fdefault = None
            self.vdefault = default
        self.fget = fget
        self.fset = fset
        self.signal = signal

    def default(self, node):
        if self.fdefault is None:
            return copy.deepcopy(self.vdefault)
        else:
            return self.fdefault(node)

    def get(self, node):
        return self.fget(node)

    def set(self, node, value):
        if self.signal:
            node.emit(self.signal_name)
        self.fset(node, value)



