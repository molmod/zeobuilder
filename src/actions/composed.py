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
from zeobuilder.gui.simple import ok_error

import gtk

import copy, time, sys


__all__ = ["init_actions", "UserError", "CancelException", "ActionError",
           "Action", "ImmediateMixin", "Parameters", "RememberParametersMixin",
           "Immediate", "ImmediateWithMemory", "Interactive",
           "InteractiveWithMemory"]


def init_actions(actions):
    for action in actions.itervalues():
        action.last_parameters = Parameters()
        action.clear_cached_analysis_result()
        context.application.cache.connect("cache-invalidated", action.on_cache_invalidated)


#
# Exceptions
#


class UserError(Exception):
    def __init__(self, message, details = ""):
        Exception.__init__(self, message)
        self.message = message
        self.details  = details
        exc_type, exc_value, tb = sys.exc_info()
        if exc_type is not None:
            import traceback
            err_msg = "".join(traceback.format_exception(exc_type, exc_value, tb))
            err_msg = err_msg.replace("&", "&amp;")
            err_msg = err_msg.replace("<", "&lt;")
            err_msg = err_msg.replace(">", "&gt;")
            self.details += err_msg

    def show_message(self):
        ok_error(self.message, self.details)

class CancelException(Exception):
    pass

class ActionError(Exception):
    pass


#
# Action
#


class Action(object):
    "This class holds the base structure of an action."
    # --- STATIC ---

    #
    description = None
    menu_info = None
    interactive_info = None
    drag_info = None
    button_info = None
    # behaviuor description
    repeatable = True
    # a debugging variable that counts the number of action nodes
    #count = 0

    def clear_cached_analysis_result(Class):
        Class.last_analysis_result = None
    clear_cached_analysis_result = classmethod(clear_cached_analysis_result)

    def cached_analyze_selection(Class, *arguments):
        if Class.last_analysis_result is None:
            Class.last_analysis_result = Class.analyze_selection(*arguments)
        #    print Class, "NEW", Class.last_analysis_result
        #else:
        #    print Class, "CACHED", Class.last_analysis_result
        return Class.last_analysis_result
    cached_analyze_selection = classmethod(cached_analyze_selection)

    def on_cache_invalidated(Class, cache):
        Class.clear_cached_analysis_result()
    on_cache_invalidated = classmethod(on_cache_invalidated)

    def analyze_selection():
        "Checks wether the 'selected' nodes are appropriate for this action class"
        return context.application.cache is not None
    analyze_selection = staticmethod(analyze_selection)

    # --- NON STATIC ---
    def __init__(self):
        #print "ACTION", self
        self.primitives = []
        # the action manager sets this to true when a primitive changes the
        # current selection. It will require that everything is unselected
        # before the first change in selection happens. This is purely a matter
        # of usability.
        self.primitives_change_selection = False
        context.application.action_manager.begin_new_action(self)

    def redo(self):
        for primitive in self.primitives:
            primitive.redo()

    def undo(self):
        for primitive in self.primitives[::-1]:
            primitive.undo()

    def want_repeat(self):
        return self.analyze_selection()

    def repeat(self):
        # creates a new action, assumes that an analyze_selection has already
        # happened so that the context.application.cache
        # has been rebuilt.
        assert self.repeatable
        self.__class__()


#
# Mixin classes
#

class ImmediateMixin(object):
    def __init__(self):
        try:
            self.do()
            context.application.action_manager.end_current_action()
        except UserError, e:
            e.show_message()
            if context.application.action_manager is not None:
                context.application.action_manager.cancel_current_action()
        except CancelException:
            if context.application.action_manager is not None:
                context.application.action_manager.cancel_current_action()


    def do(self):
        raise NotImplementedError


class Parameters(object):
    # Holds the parameters that describe an parameterized action below
    def empty(self):
        return len(self.__dict__) == 0

    def clear(self):
        self.__dict__ = {}


class RememberParametersMixin(object):
    def analyze_selection(parameters=None):
        "Checks wether the 'selected' nodes are appropriate for this action class"
        return context.application.cache is not None
    analyze_selection = staticmethod(analyze_selection)

    # lets the user give extra parameters to an action, e.g. translation vector coordinates etc.
    def __init__(self, parameters=None):
        self.parameters = parameters

    def want_repeat(self):
        return self.analyze_selection(self.parameters)

    def repeat(self):
        assert self.repeatable
        self.__class__(self.parameters)


#
# Elementary classes
#


class Immediate(Action, ImmediateMixin):
    def __init__(self):
        Action.__init__(self)
        ImmediateMixin.__init__(self)


class ImmediateWithMemory(Immediate, RememberParametersMixin):
    last_parameters = None
    store_last_parameters = True
    parameters_dialog = None

    analyze_selection = staticmethod(RememberParametersMixin.analyze_selection)

    def __init__(self, parameters=None):
        RememberParametersMixin.__init__(self, parameters)
        if self.parameters is None:
            if self.store_last_parameters:
                self.use_last_parameters()
            else:
                self.parameters = Parameters()
                self.init_parameters()
            self.ask_parameters()
        if not self.parameters.empty():
            if self.store_last_parameters:
                self.__class__.last_parameters = self.parameters
            Immediate.__init__(self)

    def use_last_parameters(self):
        self.parameters = copy.deepcopy(self.last_parameters)
        if self.parameters.empty():
            self.init_parameters()

    def init_parameters(self):
        raise NotImplementedError

    def ask_parameters(self):
        if self.parameters_dialog is None:
            raise NotImplementedError
        else:
            if self.parameters_dialog.run(self.parameters) != gtk.RESPONSE_OK:
                self.parameters.clear()

    def want_repeat(self):
        RememberParametersMixin.want_repeat(self)

    def repeat(self):
        RememberParametersMixin.repeat(self)


class Interactive(Action):
    repeatable = False

    def __init__(self):
        Action.__init__(self)
        self.interactive_init()

    def interactive_init(self):
        pass
        #print "INTERACTIVE BEGIN", self

    def finish(self):
        #print "INTERACTIVE END", self
        context.application.action_manager.end_current_action()


class InteractiveWithMemory(Interactive, RememberParametersMixin):
    repeatable = True
    analyze_selection = staticmethod(RememberParametersMixin.analyze_selection)

    def __init__(self, parameters=None):
        RememberParametersMixin.__init__(self, parameters)
        Action.__init__(self)
        if self.parameters is None:
            self.parameters = Parameters()
            self.interactive_init()
        else:
            try:
                self.immediate_do()
                context.application.action_manager.end_current_action()
            except UserError, e:
                e.show_message()
                if context.application.action_manager is not None:
                    context.application.action_manager.cancel_current_action()
            except CancelException:
                if context.application.action_manager is not None:
                    context.application.action_manager.cancel_current_action()

    def immediate_do(self):
        raise NotImplementedError

    def want_repeat(self):
        RememberParametersMixin.want_repeat(self)

    def repeat(self):
        RememberParametersMixin.repeat(self)

    def finish(self):
        if self.parameters.empty():
            if context.application.action_manager is not None:
                context.application.action_manager.cancel_current_action()
        else:
            Interactive.finish(self)



