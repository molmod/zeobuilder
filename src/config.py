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

# This file contains a configuration window_class and window. The
# class holds the data that is used in other parts of the program
# and the gui allows the user to change the configuration


from molmod.units import measures, units_by_measure

import os.path


__all__ = ["Configuration"]


class Settings(object):
    def __setattr__(self, name, value, registered=False):
        if (name != "__dict__") and (not registered) and (name not in self.__dict__):
            raise AttributeError("Setting '%s' has not been registered." % name)
        else:
            object.__setattr__(self, name, value)


class Configuration(object):
    def __init__(self, filename):
        self.filename = filename
        self.dialog_fields = []
        self.settings = Settings()
        self.load_from_file()

        # register some general settings
        from zeobuilder.gui import fields
        from zeobuilder.gui.fields_dialogs import DialogFieldInfo

        # 1) Default units
        def corrector_default_units(value):
            for measure, units in units_by_measure.iteritems():
                if measure not in value or value[measure] not in units:
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
            "max_histroy_length",
            6,
            DialogFieldInfo("General", (0, 1), fields.faulty.Int(
                label_text="Maximum history length for dialog fields",
                attribute_name="max_histroy_length",
                minimum=1
            )),
        )

    def load_from_file(self):
        if os.path.isfile(self.filename):
            f = file(self.filename, "r")
            try:
                self.settings.__dict__ = eval(f.read())
            except Exception:
                pass
            f.close()

    def save_to_file(self):
        f = file(self.filename, "w")
        f.write(str(self.settings.__dict__))
        f.close()

    def __getattr__(self, name):
        if name not in self.settings.__dict__:
            raise AttributeError("Setting '%s' has not been registered." % name)
        else:
            return self.settings.__dict__[name]

    def __setattr__(self, name, value):
        if hasattr(self, "settings") and not hasattr(self, name):
            self.settings.__setattr__(name, value)
        else:
            object.__setattr__(self, name, value)

    def register_setting(self, name, default, dialog_field_info=None, corrector=None):
        if name not in self.settings.__dict__:
            self.settings.__setattr__(name, default, True)
        elif corrector is not None:
            # the corrector is a function that validates the initial value
            # of a setting (that has been loaded from the configuration file),
            # and silently corrects it if required
            self.settings.__setattr__(name, corrector(self.settings.__dict__[name]))
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


