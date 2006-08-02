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


from zeobuilder import context
from zeobuilder.actions.composed import CancelException

import gtk, gobject, profile, pstats
import copy


__all__ = ["ActionManager"]

class LimitedList(list):
    limit = 100

    def __init__(self):
        list.__init__(self)
        self.saturated = False

    def append(self, x):
        list.append(self, x)
        if len(self) > self.limit:
            self.pop(0)
            self.saturated = True;

    def extend(self, x):
        list.extend(self, x)
        while len(self) > self.limit:
            self.pop(0)
            self.saturated = True;


class ActionManager(gobject.GObject):
    def __init__(self):
        gobject.GObject.__init__(self)
        # connect signals
        assert context.application.model is not None
        self.model = context.application.model
        self.model.connect("file-new", self.on_new_file)
        self.model.connect("file-opened", self.on_new_file)
        self.model.connect("file-opening", self.on_busy_file)
        self.model.connect("file-closed", self.on_closed_file)
        self.model.connect("file-saved", self.on_saved_file)
        self.model.connect("file-saving", self.on_busy_file)
        # history
        self.undo_stack = LimitedList()
        self.redo_stack = []
        self.last_action = None
        # now
        self.current_action = None
        self.sub_action_counter = 0
        self.current_primitive = None
        self.consequences = []
        # flag
        self.record_primitives = False

    def begin_new_action(self, action):
        if self.current_action is not None:
            self.sub_action_counter += 1
            #print "BEGIN SubAction %i %s of %s" % (self.sub_action_counter, action, self.current_action)
            return
        self.current_action = action
        if self.sub_action_counter == 0:
            self.emit("action-started")

    def append_primitive_to_current_action(self, primitive):
        assert (
            (self.current_action is not None) or
            not self.record_primitives
        ), "Can only add primitives when there is a current_action."
        if self.current_primitive is None:
            if not primitive.done:
                if primitive.changes_selection and \
                   not self.current_action.primitives_change_selection:
                    self.current_action.primitives_change_selection = True
                    context.application.main.tree_selection.unselect_all()
                primitive.init()
                self.current_primitive = primitive
                primitive.redo()
                self.current_primitive = None
                if self.record_primitives:
                    self.current_action.primitives.append(primitive)
            while len(self.consequences) > 0:
                self.current_primitive = self.consequences.pop(0)
                self.current_primitive.redo()
                if self.record_primitives:
                    self.current_action.primitives.append(self.current_primitive)
                self.current_primitive = None
        else:
            self.consequences.append(primitive)

    def cancel_current_action(self):
        assert self.current_action is not None, "Need a current action to cancel."
        if self.sub_action_counter > 0:
            self.sub_action_counter -= 1
            #print "CANCEL SubAction %i of %s" % (self.sub_action_counter, self.current_action)
            raise CancelException
        self.emit("action-cancels")
        self.current_action.undo()
        self.current_action = None

    def end_current_action(self):
        assert self.current_action is not None, "Need a current action to end."
        if self.sub_action_counter > 0:
            self.sub_action_counter -= 1
            #print "END SubAction %i" % (self.sub_action_counter)
            return
        self.emit("action-ends")
        if len(self.current_action.primitives) > 0:
            self.undo_stack.append(self.current_action)
            self.redo_stack = []
            if self.current_action.repeatable:
                self.last_action = self.current_action
            self.emit("model-changed")
        self.current_action = None
        context.application.cache.queue_invalidate()

    def undo(self):
        assert len(self.undo_stack) > 0, "No actions available to undo."
        action = self.undo_stack.pop()
        if action.primitives_change_selection:
            context.application.main.tree_selection.unselect_all()
        self.record_primitives = False
        action.undo()
        self.record_primitives = True
        self.redo_stack.append(action)
        self.emit("model-changed")
        context.application.cache.queue_invalidate()

    def redo(self):
        assert len(self.redo_stack) > 0, "No actions available to redo."
        action = self.redo_stack.pop()
        if action.primitives_change_selection:
            context.application.main.tree_selection.unselect_all()
        self.record_primitives = False
        action.redo()
        self.record_primitives = True
        self.undo_stack.append(action)
        self.emit("model-changed")
        context.application.cache.queue_invalidate()

    def repeat(self):
        # a hack to avoid that repeat is going to be listed as a last action
        tmp = self.current_action   # hack
        self.current_action = None  # hack
        self.last_action.repeat()
        self.current_action = tmp   # hack
        context.application.cache.queue_invalidate()

    def on_new_file(self, model):
        self.record_primitives = True

    def on_closed_file(self, model):
        self.reset()
        self.record_primitives = False

    def on_busy_file(self, model):
        self.record_primitives = False

    def on_saved_file(self, model):
        self.reset()
        self.record_primitives = True

    def reset(self):
        self.undo_stack = LimitedList()
        self.redo_stack = []
        context.application.cache.queue_invalidate()

    def model_changed(self):
        return self.undo_stack.saturated or len(self.undo_stack) > 0

    def default_action(self, node):
        action = context.application.plugins.get_action(
            node.info.default_action_name
        )
        if action.analyze_selection():
            action()



gobject.signal_new("model-changed", ActionManager, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
gobject.signal_new("action-started", ActionManager, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
gobject.signal_new("action-ends", ActionManager, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
gobject.signal_new("action-cancels", ActionManager, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
