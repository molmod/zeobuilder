# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 - 2010 Toon Verstraelen <Toon.Verstraelen@UGent.be>, Center
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
from zeobuilder.gui.simple import ok_error

import gtk

import time, sys


__all__ = ["init_actions", "UserError", "CancelException", "ActionError",
           "Action", "ImmediateMixin", "Parameters", "RememberParametersMixin",
           "Immediate", "ImmediateWithMemory", "Interactive",
           "InteractiveWithMemory"]


def init_actions(actions):
    for action in actions.itervalues():
        action.clear_cached_analysis_result()
        context.application.cache.connect("cache-invalidated", action.on_cache_invalidated)
        if issubclass(action, ImmediateWithMemory):
            action.register_settings()



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
            self.details += err_msg

    def show_message(self):
        ok_error(self.message, self.details, line_wrap=False)

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

    @classmethod
    def clear_cached_analysis_result(Class):
        Class.last_analysis_result = None

    @classmethod
    def cached_analyze_selection(Class, **arguments):
        if Class.last_analysis_result is None:
            Class.last_analysis_result = Class.analyze_selection(**arguments)
        #    print Class, "NEW", Class.last_analysis_result
        #else:
        #    print Class, "CACHED", Class.last_analysis_result
        return Class.last_analysis_result

    @classmethod
    def on_cache_invalidated(Class, cache):
        Class.clear_cached_analysis_result()

    @staticmethod
    def analyze_selection():
        "Checks wether the 'selected' nodes are appropriate for this action class"
        return context.application.action_manager.current_action is None

    # --- NON STATIC ---
    def __init__(self, selection=None):
        #print "ACTION", self
        self.primitives = []
        if selection is not None:
            context.application.cache.items = {"nodes": selection}
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


class CustomAction(Action):
    def __init__(self, description):
        self.description = description
        Action.__init__(self)

    def finish(self):
        context.application.action_manager.end_current_action()


class Immediate(Action, ImmediateMixin):
    def __init__(self, selection=None):
        Action.__init__(self, selection)
        ImmediateMixin.__init__(self)
        if selection is not None:
            context.application.cache.clear()

class ImmediateWithMemory(Immediate, RememberParametersMixin):
    store_last_parameters = True
    parameters_dialog = None

    @staticmethod
    def analyze_selection(parameters=None):
        return Immediate.analyze_selection()

    def __init__(self, parameters=None, selection=None):
        RememberParametersMixin.__init__(self, parameters)
        if self.parameters is None:
            if self.store_last_parameters:
                self.parameters = self.last_parameters()
            else:
                self.parameters = self.default_parameters()
            self.ask_parameters()
        if not self.parameters.empty():
            if self.store_last_parameters:
                self.store_parameters(self.parameters)
            Immediate.__init__(self, selection)

    @classmethod
    def config_name(cls):
        temp = str(cls)
        temp = temp[temp.rfind(".")+1:-2]
        return temp + "_parameters"

    @classmethod
    def register_settings(cls):
        def default_parameters():
            return cls.default_parameters().__dict__

        if cls.store_last_parameters:
            context.application.configuration.register_setting(
                cls.config_name(),
                default_parameters(),
                None,
                cls.corrector_parameters,
            )

    @classmethod
    def corrector_parameters(cls, config_parameters):
        default_parameters = cls.default_parameters().__dict__
        for key, value in config_parameters.items():
            if key not in default_parameters:
                del config_parameters[key]
        for key, value in default_parameters.iteritems():
            if key not in config_parameters:
                config_parameters[key] = value
        return config_parameters

    @classmethod
    def last_parameters(cls):
        result = Parameters()
        result.__dict__ = getattr(context.application.configuration, cls.config_name())
        return result

    @classmethod
    def default_parameters(cls):
        raise NotImplementedError

    @classmethod
    def store_parameters(cls, parameters):
        setattr(context.application.configuration, cls.config_name(), parameters.__dict__)

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

    @staticmethod
    def analyze_selection(parameters):
        return Immediate.analyze_selection()

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


