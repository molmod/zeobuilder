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


from zeobuilder.filters import DumpFilter
from zeobuilder.moltools import create_molecular_graph
import zeobuilder.authors as authors

from molmod.io import PSFFile


class DumpPSF(DumpFilter):
    authors = [authors.toon_verstraelen]

    def __init__(self):
        DumpFilter.__init__(self, "The PSF format (*.psf)")

    def __call__(self, f, universe, folder, nodes=None):
        atom_counter = 0
        if nodes is None:
            nodes = [universe]

        graph = create_molecular_graph([universe])
        names = [atom.name for atom in graph.molecule.atoms]
        charges = [atom.extra.get("charge", 0.0) for atom in graph.molecule.atoms]
        psf_file = PSFFile()
        psf_file.add_molecular_graph(graph, atom_types=names, charges=charges)
        psf_file.dump(f)


dump_filters = {
    "psf": DumpPSF(),
}


