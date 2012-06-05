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


from molmod.periodic import periodic
from molmod.bonds import bonds, BOND_SINGLE, BOND_DOUBLE, BOND_TRIPLE
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


