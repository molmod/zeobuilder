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

import os, imp


class PluginNotFoundError(Exception):
    def __init__(self, name):
        self.name = name
        Exception.__init__(self, "Plugin %s not found" % name)


class PluginsCollection(object):
    def __init__(self):
        self.actions = {}
        self.nodes = {}
        self.load_filters = {}
        self.dump_filters = {}
        self.interactive_groups = {}
        self.cache_plugins = {}

        self.modules = set([])
        for directory in context.share_dirs:
            self.find_modules(os.path.join(directory, "plugins"))
        self.modules = list(sorted(self.modules))
        self.load_modules()
        self.init_plugins()

    def find_modules(self, directory):
        if not os.path.isdir(directory):
            return
        for filename in os.listdir(directory):
            fullname = os.path.join(directory, filename)
            if os.path.isdir(fullname) and not fullname.endswith(".skip"):
                self.find_modules(fullname)
            elif filename.endswith(".py"):
                self.modules.add((directory, filename[:-3]))

    def load_modules(self):
        for directory, name in self.modules:
            #print name, directory
            (f, pathname, description) = imp.find_module(name, [directory])
            try:
                module = imp.load_module(name, f, pathname, description)
                self.load_plugins(module)
            finally:
                f.close()

    def load_plugins(self, module):
        def load(name, d):
            #print " ", name
            plugins = module.__dict__.get(name)
            if plugins is not None:
                for id, plugin in plugins.iteritems():
                    #print "   ", id
                    assert id not in d, "A plugin with id '%s' is already loaded (%s)" % (id, name)
                    d[id] = plugin

        load("actions", self.actions)
        load("nodes", self.nodes)
        load("load_filters", self.load_filters)
        load("dump_filters", self.dump_filters)
        load("interactive_groups", self.interactive_groups)
        load("cache_plugins", self.cache_plugins)

    def init_plugins(self):
        from zeobuilder.actions.composed import init_actions
        init_actions(self.actions)

        from zeobuilder.nodes import init_nodes
        init_nodes(self.nodes)

        from zeobuilder.filters import init_filters
        init_filters(self.load_filters, self.dump_filters)

        from zeobuilder.selection_cache import init_cache_plugins
        init_cache_plugins(self.cache_plugins)

        from zeobuilder.expressions import init_locals
        init_locals(self.nodes)

    def get_plugin(self, name, plugins):
        plugin = plugins.get(name)
        if plugin is None:
            raise PluginNotFoundError(name)
        else:
            return plugin

    def get_action(self, name):
        return self.get_plugin(name, self.actions)

    def get_node(self, name):
        return self.get_plugin(name, self.nodes)

    def get_load_filter(self, name):
        return self.get_plugin(name, self.load_filters)

    def get_dump_filter(self, name):
        return self.get_plugin(name, self.dump_filters)

    def get_interactive_group(self, name):
        return self.get_plugin(name, self.interactive_groups)
