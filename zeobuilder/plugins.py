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

import os, imp


class PluginCategory(object):
    def __init__(self, singular, plural, init, authors=[]):
        self.singular = singular
        self.plural = plural
        self.init = init
        self.authors = authors


def init_nodes(nodes):
    from zeobuilder.nodes import init_nodes
    init_nodes(nodes)
    from zeobuilder.expressions import add_locals
    add_locals(nodes)

def init_actions(actions):
    from zeobuilder.actions.composed import init_actions
    init_actions(actions)

def init_load_filters(load_filters):
    from zeobuilder.filters import init_load_filters
    init_load_filters(load_filters)

def init_dump_filters(dump_filters):
    from zeobuilder.filters import init_dump_filters
    init_dump_filters(dump_filters)

def init_cache_plugins(cache_plugins):
    from zeobuilder.selection_cache import init_cache_plugins
    init_cache_plugins(cache_plugins)

def init_utility_functions(utility_functions):
    from zeobuilder.expressions import add_locals
    add_locals(utility_functions)


builtin_categories = [
    PluginCategory("plugin_category", "plugin_categories", None),
    PluginCategory("node", "nodes", init_nodes),
    PluginCategory("action", "actions", init_actions),
    PluginCategory("load_filter", "load_filters", init_load_filters),
    PluginCategory("dump_filter", "dump_filters", init_dump_filters),
    PluginCategory("interactive_group", "interactive_groups", None),
    PluginCategory("cache_plugin", "cache_plugins", init_cache_plugins),
    PluginCategory("utility_function", "utility_functions", init_utility_functions)
]



class PluginNotFoundError(Exception):
    def __init__(self, name):
        self.name = name
        Exception.__init__(self, "Plugin %s not found" % name)


class PluginsCollection(object):
    def __init__(self):
        self.module_descriptions = set([])
        for directory in context.share_dir, context.user_dir:
            self.find_modules(os.path.join(directory, "plugins"))
        #self.module_descriptions = list(sorted(self.module_descriptions))
        self.load_modules()
        self.all = {}
        self.load_plugins()

    def find_modules(self, directory):
        if not os.path.isdir(directory):
            return
        for filename in os.listdir(directory):
            fullname = os.path.join(directory, filename)
            if os.path.isdir(fullname) and not fullname.endswith(".skip"):
                self.find_modules(fullname)
            elif filename.endswith(".py"):
                self.module_descriptions.add((directory, filename[:-3]))

    def load_modules(self):
        self.modules = []
        for directory, name in self.module_descriptions:
            #print name, directory
            (f, pathname, description) = imp.find_module(name, [directory])
            try:
                self.modules.append(imp.load_module(name, f, pathname, description))
            finally:
                f.close()

    def load_plugins(self):
        for category in builtin_categories:
            self.load_category(category)

        for category in self.plugin_categories.itervalues():
            self.load_category(category)

        for category in builtin_categories:
            self.plugin_categories[category.plural] = category

    def load_category(self, category):
        d = {}
        all = []

        def check_required_modules(plugin):
            if not hasattr(plugin, "required_modules"):
                plugin.required_modules = []
                plugin.failed_modules = []
                return True
            all_success = True
            plugin.failed_modules = []
            for module_name in plugin.required_modules:
                try:
                    f, filename, description = imp.find_module(module_name)
                    if f is not None:
                        f.close()
                except ImportError:
                    plugin.failed_modules.append(module_name)
                    all_success = False
            return all_success


        #print category.plural
        for module in self.modules:
            #print "  %s.py" % module.__name__
            plugins = module.__dict__.get(category.plural)
            if plugins is not None:
                for id, plugin in plugins.iteritems():
                    #print "    %s" % id
                    plugin.module = module
                    plugin.category = category.plural
                    plugin.id = id
                    if id in d:
                        plugin.status = "Failed: A plugin with id '%s' already exists in this category." % id
                    elif not check_required_modules(plugin):
                        plugin.status = "Failed: Some required modules could not be found: %s." % plugin.failed_modules
                    else:
                        plugin.status = "Success"
                        d[id] = plugin
                    all.append(plugin)

        self.all[category.plural] = all

        if category.init is not None:
            category.init(d)

        self.__dict__[category.plural] = d

        def get_plugin(name):
            plugin = d.get(name)
            if plugin is None:
                raise PluginNotFoundError(name)
            else:
                return plugin
        self.__dict__["get_%s" % category.singular] = get_plugin


