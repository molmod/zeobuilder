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


from molmod.data.periodic import periodic
from molmod.data.bonds import bonds, BOND_SINGLE, BOND_DOUBLE, BOND_TRIPLE
import molmod.units


class Expression(object):
    l = {
        "periodic": periodic,
        "bonds": bonds,
        "BOND_SINGLE": BOND_SINGLE,
        "BOND_DOUBLE": BOND_DOUBLE,
        "BOND_TRIPLE": BOND_TRIPLE,
    }
    for key, val in molmod.units.__dict__.iteritems():
        if isinstance(val, float):
            l[key] = val

    def __init__(self, code="True"):
        self.compiled = compile("(%s)" % code, "<string>", 'eval')
        self.code = code
        self.variables = ("node",)

    def compile_as(self, name):
        self.compiled = compile("(%s)" % self.code, name, 'eval')

    def __call__(self, *variables):
        g = {"__builtins__": __builtins__}
        g.update(self.l)
        for name, variable in zip(self.variables, variables):
            g[name] = variable
        return eval(self.compiled, g)


def add_locals(l):
    Expression.l.update(l)


