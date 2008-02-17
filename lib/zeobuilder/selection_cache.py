# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 - 2008 Toon Verstraelen <Toon.Verstraelen@UGent.be>
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
from zeobuilder.nodes.parent_mixin import ContainerMixin, ReferentMixin
from zeobuilder.nodes.glmixin import GLTransformationMixin
from zeobuilder.nodes.reference import Reference
from zeobuilder.nodes.elementary import GLFrameBase
import zeobuilder.nodes.analysis as analysis

from molmod.transformations import Translation, Rotation

import gobject


__all__ = ["SelectionCache"]


class SelectionCache(gobject.GObject):
    analysis_functions = {}

    def __init__(self):
        gobject.GObject.__init__(self)
        self.waiting_to_emit = False
        self.clear()

    def queue_invalidate(self):
        self.clear()
        if not self.waiting_to_emit:
            self.waiting_to_emit = True
            gobject.idle_add(self.emit_invalidate)

    def emit_invalidate(self):
        self.emit("cache-invalidated")
        #print "EMIT: cache-invalidated"
        self.waiting_to_emit = False

    def clear(self):
        self.items = {}

    def __getattr__(self, name):
        if name not in self.items:
            function = self.analysis_functions.get(name)
            if function is None:
                raise AttributeError, "Cached variables %s does not exist." % name
            else:
                result = function(self)
            #print "GET %s: %s" % (name, result)
            self.items[name] = result
            return result
        else:
            return self.items[name]

    #
    # Elementary cached values
    #

    # nodes
    def get_nodes(self):
        return context.application.model.selection

    def get_last(self):
        if len(self.nodes) > 0:
            return self.nodes[-1]
        else:
            return None

    def get_next_to_last(self):
        if len(self.nodes) > 1:
            return self.nodes[-2]
        else:
            return None

    def get_some_nodes_fixed(self):
        return analysis.some_fixed(self.nodes)

    def get_node(self):
        # This one is tricky. Use it when you only want one model object to be selected
        if len(self.nodes) == 1:
            return self.nodes[0]
        else:
            return None

    def get_containers(self):
        return [node for node in self.nodes if isinstance(node, ContainerMixin)]

    def get_containers_with_children(self):
        return [container for container in self.containers if len(container.children) > 0]

    def get_referents(self):
        return [node for node in self.nodes if isinstance(node, ReferentMixin)]

    def get_referents_with_children(self):
        return [referent for referent in self.referents if len(referent.children) > 0]

    def get_classes(self):
        return analysis.list_classes(self.nodes)

    # parents
    def get_parents(self):
        return analysis.list_parents(self.nodes)

    def get_parent(self):
        if len(self.parents) == 1:
            return self.parents[0]
        else:
            return None

    # children
    def get_children(self):
        return analysis.list_children(self.containers_with_children) + analysis.list_children(self.referents_with_children)

    def get_some_children_fixed(self):
        return analysis.some_fixed(self.children)

    def get_child_classes(self):
        return analysis.list_classes(self.children)

    # neighbours (the children of the parents of the selected nodes)
    def get_neighbours(self):
        return analysis.list_children(self.parents)

    def get_some_neighbours_fixed(self):
        return analysis.some_fixed(self.neighbours)


    #
    # Transformation related
    #

    # nodes
    def get_transformed_nodes(self):
        return [node for node in self.nodes if isinstance(node, GLTransformationMixin)]

    def get_translated_nodes(self):
        return [node for node in self.transformed_nodes if isinstance(node.transformation, Translation)]

    def get_rotated_nodes(self):
        return [node for node in self.transformed_nodes if isinstance(node.transformation, Rotation)]

    def get_translations(self):
        return [node.transformation for node in self.translated_nodes]

    # children
    def get_transformed_children(self):
        return [child for child in self.children if isinstance(child, GLTransformationMixin)]

    def get_translated_children(self):
        return [child for child in self.transformed_children if isinstance(child.transformation, Translation)]

    def get_rotated_children(self):
        return [child for child in self.transformed_children if isinstance(child.transformation, Rotation)]

    def get_child_translations(self):
        return [child.transformation for child in self.translated_children]

    # neighbours
    def get_transformed_neighbours(self):
        return [neighbour for neighbour in self.neighbours if isinstance(neighbour, GLTransformationMixin)]

    def get_translated_neighbours(self):
        return [neighbour for neighbour in self.transformed_neighbours if isinstance(neighbour.transformation, Translation)]

    def get_rotated_neighbours(self):
        return [neighbour for neighbour in self.transformed_neighbours if isinstance(neighbour.transformation, Rotation)]

    def get_neighbour_translations(self):
        return [neighbour.transformation for neighbour in self.translated_neighbours]

    #
    # Drag related
    #

    def get_recursive_drag(self):
        return len(set(self.drag_destination.trace()) & set(self.nodes)) > 0

    #
    # Index related
    #

    def get_indices(self):
        return [node.get_index() for node in self.nodes]

    def get_lowest_index(self):
        return min(self.indices)

    def get_highest_index(self):
        return max(self.indices)

    #
    # Advanced
    #

    def get_traces_by_parent(self):
        return analysis.list_traces_by(self.parents)

    def get_nodes_by_parent(self):
        return analysis.list_by_parent(self.nodes)

    def get_nodes_without_children(self):
        #print "DEBUG self.nodes_by_parent:", self.nodes_by_parent
        #print "DEBUG self.traces_by_parent:", self.traces_by_parent
        return analysis.list_without_children(self.nodes_by_parent, self.traces_by_parent)

    def get_some_nodes_without_children_fixed(self):
        #print "DEBUG self.nodes_without_children:", self.nodes_without_children
        return analysis.some_fixed(self.nodes_without_children)

    def get_common_parent(self):
        return analysis.common_parent(self.parents)

    def get_common_root(self):
        return analysis.common_parent(self.nodes)


for name, method in SelectionCache.__dict__.iteritems():
    if name.startswith("get"):
        SelectionCache.analysis_functions[name[4:]] = method


def init_cache_plugins(cache_plugins):
    SelectionCache.analysis_functions.update(cache_plugins)


gobject.signal_new("cache-invalidated", SelectionCache, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())




