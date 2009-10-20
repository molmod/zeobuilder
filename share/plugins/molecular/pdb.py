# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 - 2009 Toon Verstraelen <Toon.Verstraelen@UGent.be>, Center
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


# See http://www.wwpdb.org/docs.html for details about the pdb format.
# The implementation below only supports a small fraction of the full
# pdb specification.

import numpy

from zeobuilder import context
from zeobuilder.filters import LoadFilter, DumpFilter, FilterError
from zeobuilder.nodes.glcontainermixin import GLContainerMixin
import zeobuilder.authors as authors

from molmod.periodic import periodic
from molmod.units import angstrom, angstrom


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
        atom_index =  0
        for line in f:
            #if len(line) != 81:
            #    raise FilterError("Each line in a PDB file must count 80 characters, error at line %i, len=%i" % (counter, len(line)-1))
            if line.startswith("ATOM"):
                extra = {"index": atom_index}
                atom_info = periodic[line[76:78].strip()]
                atom = Atom(name=line[12:16].strip(), number=atom_info.number, extra=extra)
                try:
                    atom.transformation.t = numpy.array([
                            float(line[30:38].strip()),
                            float(line[38:46].strip()),
                            float(line[46:54].strip())
                    ]) * angstrom
                except ValueError:
                    raise FilterError("Error while reading PDB file: could not read coordinates at line %i." % counter)
                universe.add(atom)
                atom_index += 1
            elif line.startswith("CRYST1"):
                space_group = line[55:66].strip().upper()
                if space_group != "P 1":
                    raise FilterError("Error while reading PDB file: only unit cells with space group P 1 are supported.")
                a = float(line[6:15].strip())*angstrom
                b = float(line[15:24].strip())*angstrom
                c = float(line[24:33].strip())*angstrom
                alpha = float(line[33:40].strip())*numpy.pi/180
                beta = float(line[40:47].strip())*numpy.pi/180
                gamma = float(line[47:54].strip())*numpy.pi/180
                universe.set_parameters([a, b, c], [alpha, beta, gamma])
                universe.cell_active = numpy.array([True, True, True])
            counter += 1

        return [universe, folder]


class DumpPDB(DumpFilter):
    authors = [authors.toon_verstraelen]

    def __init__(self):
        DumpFilter.__init__(self, "The PDB format (*.pdb)")

    def __call__(self, f, universe, folder, nodes=None):
        atom_counter = 0
        if nodes is None:
            nodes = [universe]

        Atom = context.application.plugins.get_node("Atom")
        if universe.cell_active.all():
            lengths, angles = universe.get_parameters()
            a, b, c = lengths/angstrom
            alpha, beta, gamma = angles/numpy.pi*180
            print >> f, "CRYST1% 9.3f% 9.3f% 9.3f% 7.2f% 7.2f% 7.2f P 1        1             " % (
                a, b, c, alpha, beta, gamma
            )
        print >> f, "MODEL        1                                                                  "
        self.counter = 1
        def write_xyz_lines(nodes):
            for node in nodes:
                if isinstance(node, Atom):
                    x, y, z = node.get_frame_relative_to(universe).t/angstrom
                    s = periodic[node.number].symbol.upper()
                    print >> f, "ATOM  % 5i % 4s FOO     1    % 8.3f% 8.3f% 8.3f  1.00  1.00          % 2s 0" % (self.counter, s, x, y, z, s)
                    self.counter += 1
                else:
                    if isinstance(node, GLContainerMixin):
                        write_xyz_lines(node.children)
        write_xyz_lines(nodes)
        print >> f, "ENDMDL                                                                          "


load_filters = {
    "pdb": LoadPDB(),
}

dump_filters = {
    "pdb": DumpPDB(),
}


