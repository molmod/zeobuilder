# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 - 2008 Toon Verstraelen <Toon.Verstraelen@UGent.be>
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
# --


import numpy

from molmod.io.psf import PSFFile

from zeobuilder import context
from zeobuilder.filters import DumpFilter, FilterError
from zeobuilder.moltools import create_molecular_graph
import zeobuilder.authors as authors


class DumpPSF(DumpFilter):
    authors = [authors.toon_verstraelen]

    def __init__(self):
        DumpFilter.__init__(self, "The PSF format (*.psf)")

    def __call__(self, f, universe, folder, nodes=None):
        atom_counter = 0
        if nodes is None:
            nodes = [universe]

        graph = create_molecular_graph([universe])
        symbols = [atom.name for atom in graph.molecule.atoms]
        psf_file = PSFFile()
        psf_file.add_molecular_graph(graph, symbols=symbols)
        psf_file.dump(f)


dump_filters = {
    "psf": DumpPSF(),
}





