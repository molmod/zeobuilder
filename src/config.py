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

from molmod.units import measures

import os.path

__all__ = ["Configuration"]

class Configuration(object):
    def __init__(self, filename):
        self.default_units = dict((measure, units[0]) for measure, units in measures.iteritems())
        self.load_from_file(filename)

    def load_from_file(self, filename):
        # load settings from file
        if os.path.isfile(filename):
            f = file(filename, "r")
            self.__dict__.update(eval(f.read()))
            f.close()
        # validate and correct them
        for measure, units in measures.iteritems():
            if measure not in self.default_units or self.default_units[measure] not in units:
                self.default_units[measure] = units[0]
        self.default_units = dict((measure, unit) for measure, unit in self.default_units.iteritems() if measure in measures)

    def save_to_file(self, filename):
        f = file(filename, "w")
        f.write(str(self.__dict__))
        f.close()
