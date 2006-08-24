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
from molmod.units import from_unit, to_unit, units_by_measure


__all__ = ["eval_measure", "express_measure", "express_data_size"]


# * evaluation routines (from string to value)

def eval_measure(s, measure):
    s = s.lower().strip()
    suffix = None
    for unit_name in units_by_measure[measure]:
        if s.endswith(unit_name.lower()):
            s = s[:-len(unit_name)]
            suffix = unit_name
            break
    if suffix is None:
        suffix = context.application.configuration.default_units[measure]

    return from_unit[suffix](float(s))

# * expression routines (from value to string)

def express_measure(val, measure, decimals=3, scientific=False, unit_name=None):
    if unit_name is None:
        unit_name = context.application.configuration.default_units[measure]

    printf_character = {True: "E", False: "F"}[scientific]
    return ("%.*" + printf_character + " %s") % (decimals, to_unit[unit_name](val), unit_name)

def express_data_size(val):
    if val < 1024:
        return str(val) + " b"
    elif val < 1024 * 1024:
        return str(val/1024) + " Kb"
    else:# val < 1024 * 1024 * 1024:
        return str(val/(1024*1024)) + " Mb"

