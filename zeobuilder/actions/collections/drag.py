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
# --


from zeobuilder import context
from zeobuilder.actions.composed import Parameters

import gtk.gdk


__all__ = ["Drag"]


class DragInfo(object):
    def __init__(self, order):
        self.order = order


class Drag(object):
    def __init__(self):
        tv = context.application.main.tree_view
        tv.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [("ModelObjects", 0, 0)], gtk.gdk.ACTION_MOVE)
        tv.enable_model_drag_dest([("ModelObjects", 0, 0)], gtk.gdk.ACTION_MOVE)
        tv.connect("drag-data-received", self.on_drag_data_received)
        self.drag_actions = [
            action
            for action
            in context.application.plugins.actions.itervalues()
            if action.drag_info is not None
        ]
        self.drag_actions.sort(key=(lambda a: a.drag_info.order))

    def on_drag_data_received(self, tree_view, drag_context, x, y, selection_data, info, timestamp):
        cache = context.application.cache
        model = context.application.model


        if len(cache.nodes) == 0:
            drag_context.finish(False, False, timestamp)
            #print "DRAG has no selected nodes"
            return

        destination_path, pos = tree_view.get_dest_row_at_pos(x, y)
        for node in cache.nodes:
            source_path = model.get_path(node.iter)
            # check for each source item wether the destination is not a child of it.
            if destination_path[0:len(source_path)] == source_path:
                drag_context.finish(False, False, timestamp)
                #print "DROP not accepted"
                return

        destination_iter = model.get_iter(destination_path)
        destination = model.get_value(destination_iter, 0)
        if (pos == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE) or (pos == gtk.TREE_VIEW_DROP_INTO_OR_AFTER):
            # We assume that the user dropped on top if the item, doesn't always work
            #print "TRY DROP Into"
            child_index = -1
        elif (pos == gtk.TREE_VIEW_DROP_BEFORE) or (pos == gtk.TREE_VIEW_DROP_AFTER):
            #print "TRY DROP Before or After"
            if destination.parent is None:
                drag_context.finish(False, False, timestamp)
                #print "DROP not accepted"
                return
            if pos == gtk.TREE_VIEW_DROP_BEFORE:
                #print "TRY DROP Before"
                child_index = destination.get_index()
            else:
                #print "TRY DROP After"
                child_index = destination.get_index()+1
            destination = destination.parent
        #print "child_index = " + str(child_index)

        if self.execute_drag(destination, child_index):
            drag_context.finish(True, False, timestamp)
            #print "DROP accepted"
        else:
            drag_context.finish(False, False, timestamp)
            #print "DROP not accepted, no approtriate drag actions found"

    def execute_drag(self, destination, child_index):
        parameters = Parameters()
        context.application.cache.drag_destination = destination
        parameters.child_index = child_index
        for drag_action in self.drag_actions:
            if drag_action.cached_analyze_selection(parameters=parameters):
                drag_action(parameters=parameters)
                return True
        return False


