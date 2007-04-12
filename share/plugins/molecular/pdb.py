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


import numpy

from zeobuilder import context
from zeobuilder.filters import LoadFilter, DumpFilter, FilterError
from zeobuilder.nodes.glcontainermixin import GLContainerMixin
import zeobuilder.authors as authors

from molmod.data import periodic
from molmod.units import to_angstrom, from_angstrom


class LoadPDB(LoadFilter):
    authors = [authors.toon_verstraelen]

    def __init__(self):
        LoadFilter.__init__(self, "The PDB format (*.pdb)")

    def __call__(self, f):
        Universe = context.application.plugins.get_node("Universe")
        universe = Universe()
        Folder = context.application.plugins.get_node("Folder")
        folder = Folder()

        Atom = context.application.plugins.get_node("Atom")
        counter = 1
        for line in f:
            if len(line) != 81:
                raise FilterError("Each line in a PDB file must counter 80 characters, error at line %i, len=%i" % (counter, len(line)-1))
            if line.startswith("ATOM"):
                atom_info = periodic[line[77:79].strip()]
                atom = Atom(name=line[13:17].strip(), number=atom_info.number)
                try:
                    atom.transformation.t = from_angstrom(
                        numpy.array([
                            float(line[31:39].strip()), 
                            float(line[39:47].strip()), 
                            float(line[47:55].strip())
                        ])
                    )
                except ValueError:
                    raise FilterError("Error while reading PDB file: could not read coordinates at line %i." % counter)
                universe.add(atom)
            counter += 1

        return [universe, folder]


load_filters = {
    "pdb": LoadPDB(),
}

