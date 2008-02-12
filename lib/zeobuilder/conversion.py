# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 Toon Verstraelen <Toon.Verstraelen@UGent.be>
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
# Contact information:
#
# Supervisors
#
# Prof. Dr. Michel Waroquier and Prof. Dr. Ir. Veronique Van Speybroeck
#
# Center for Molecular Modeling
# Ghent University
# Proeftuinstraat 86, B-9000 GENT - BELGIUM
# Tel: +32 9 264 65 59
# Fax: +32 9 264 65 60
# Email: Michel.Waroquier@UGent.be
# Email: Veronique.VanSpeybroeck@UGent.be
#
# Author
#
# Ir. Toon Verstraelen
# Center for Molecular Modeling
# Ghent University
# Proeftuinstraat 86, B-9000 GENT - BELGIUM
# Tel: +32 9 264 65 56
# Email: Toon.Verstraelen@UGent.be
#
# --


from zeobuilder import context
import molmod.units


__all__ = [
    "measures", "unit", "units_by_measure", "to_unit", "from_unit",
    "eval_measure", "express_measure", "express_data_size"
]


measures = ["Length", "Energy", "Mass", "Charge", "Angle", "Time"]

units = {
    "au": 1,
    "A": molmod.units.angstrom,
    "nm": molmod.units.nanometer,
    "kJ/mol": molmod.units.kjmol,
    "kcal/mol": molmod.units.kcalmol,
    "eV": molmod.units.ev,
    "u": molmod.units.unified,
    "rad": 1,
    "deg": molmod.units.degree,
    "ns": molmod.units.nanosecond,
    "ps": molmod.units.picosecond,
    "fs": molmod.units.femtosecond,
}

units_by_measure = {
    "Length": ["au", "A", "nm"],
    "Energy": ["au", "kJ/mol", "kcal/mol", "eV"],
    "Mass": ["au", "u"],
    "Charge": ["au"],
    "Angle": ["rad", "deg"],
    "Time": ["au", "ns", "ps", "fs"],
}

from_unit = dict((unit, eval("lambda x: x*%s" % value)) for unit, value in units.iteritems())
to_unit = dict((unit, eval("lambda x: x/%s" % value)) for unit, value in units.iteritems())

# some sanity checks
assert len(measures) == len(set(measures)), "Some measures have the same name."
assert len(measures) == len(units_by_measure), "Some measures don't have units."
assert len(units) == len(set(sum((u for u in units_by_measure.itervalues()), [])))


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



