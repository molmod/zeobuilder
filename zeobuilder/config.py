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

# This file contains a configuration window_class and window. The
# class holds the data that is used in other parts of the program
# and the gui allows the user to change the configuration


from zeobuilder.conversion import measures, units_by_measure

import os.path


__all__ = ["Configuration"]

class Configuration(object):
    def __init__(self, filename):
        self.redirecting = False
        self.filename = filename
        self.dialog_fields = []
        self.settings = {}
        self.load_from_file()
        self.redirecting = True

        # register some general settings
        from zeobuilder.gui import fields
        from zeobuilder.gui.fields_dialogs import DialogFieldInfo

        # 1) Default units
        def corrector_default_units(value):
            for measure, units in units_by_measure.iteritems():
                if (measure not in value) or (value[measure] not in units):
                    value[measure] = units[0]
            return dict(
                (measure, unit)
                for measure, unit in
                value.iteritems()
                if measure in measures
            )
        self.register_setting(
            "default_units",
            dict((measure, units[0]) for measure, units in units_by_measure.iteritems()),
            DialogFieldInfo("General", (0, 0), fields.composed.Units(
                label_text="Default units",
                attribute_name="default_units",
            )),
            corrector_default_units
        )

        # 2) history stuff
        self.register_setting("saved_representations", {})
        self.register_setting("history_representations", {})
        self.register_setting(
            "max_history_length",
            6,
            DialogFieldInfo("General", (0, 1), fields.faulty.Int(
                label_text="Maximum history length for dialog fields",
                attribute_name="max_history_length",
                minimum=1
            )),
        )

    def load_from_file(self):
        if os.path.isfile(self.filename):
            from zeobuilder.zml import load_from_file
            f = file(self.filename, "r")
            self.settings = load_from_file(f)
            f.close()

    def save_to_file(self):
        from zeobuilder.zml import dump_to_file
        dirname = os.path.dirname(self.filename)
        if not os.path.isdir(dirname):
            os.mkdir(dirname)
        f = file(self.filename, "w")
        dump_to_file(f, self.settings)
        f.close()

    def __getattr__(self, name):
        if len(self.settings) > 0 and name not in self.settings:
            raise AttributeError("Setting '%s' has not been registered." % name)
        else:
            return self.settings[name]

    def __setattr__(self, name, value):
        if name == "redirecting" or not self.redirecting:
            object.__setattr__(self, name, value)
        elif name in self.settings:# and name in self.settings:
            self.settings[name] = value
        else:
            object.__setattr__(self, name, value)

    def register_setting(self, name, default, dialog_field_info=None, corrector=None):
        if name not in self.settings:
            self.settings[name] =  default
        elif corrector is not None:
            # the corrector is a function that validates the initial value
            # of a setting (that has been loaded from the configuration file),
            # and silently corrects it if required
            self.settings[name] = corrector(self.settings[name])
        if dialog_field_info is not None:
            self.dialog_fields.append(dialog_field_info)

    def create_main_field(self):
        from zeobuilder.gui.fields_dialogs import create_tabbed_main_field
        return create_tabbed_main_field(self.dialog_fields)

    def get_saved_representations(self, history_name):
        result = self.saved_representations.get(history_name)
        if result is None:
            result = {}
            self.saved_representations[history_name] = result
        return result

    def get_history_representations(self, history_name):
        result = self.history_representations.get(history_name)
        if result is None:
            result = []
            self.history_representations[history_name] = result
        return result

    def add_to_history(self, history_name, representation):
        history_representations = self.get_history_representations(history_name)
        if representation in history_representations:
            history_representations.remove(representation)
        while len(history_representations) > self.max_history_length:
            del history_representations[-1]
        history_representations.insert(0, representation)


