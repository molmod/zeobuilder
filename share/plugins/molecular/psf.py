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
from zeobuilder.filters import DumpFilter, FilterError
from zeobuilder.moltools import create_graph_bonds
import zeobuilder.authors as authors

from molmod.data import periodic
from molmod.units import unified


class DumpPSF(DumpFilter):
    authors = [authors.toon_verstraelen]

    def __init__(self):
        DumpFilter.__init__(self, "The PSF format (*.psf)")

    def __call__(self, f, universe, folder, nodes=None):
        atom_counter = 0
        if nodes is None:
            nodes = [universe]

        graph, bonds = create_graph_bonds([universe])
        
        indices = dict((atom,index) for index,atom in enumerate(graph.nodes))
        
        def print_section(count, name):
            print >> f
            print >> f, "% 7i !N%s" % (count, name)

        print >> f, "PSF"
        print_section(1, "TITLE")
        print >> f, universe.name
        
        print_section(len(graph.nodes), "ATOM")
        for index, atom in enumerate(graph.nodes):
            atom_info = periodic[atom.number]
            print >> f, "% 7i NAME 1 NAME % 5s % 5s 0.0 %12.6f 0" % (index+1,atom_info.symbol,atom_info.symbol,atom_info.mass/unified)
        
        print_section(len(graph.pairs), "BOND")
        for counter, (atom1, atom2) in enumerate(graph.pairs):
            print >> f, "% 7i" % (indices[atom1]+1),
            print >> f, "% 7i" % (indices[atom2]+1),
            if (counter) % 4 == 3:
                print >> f
        if (counter) % 4 != 3:
            print >> f
        
        
        # collect all angles
        angles = []
        graph.init_neighbors()
        for atom in graph.nodes:
            neighbors = list(graph.neighbors[atom])
            for index1, neighbor1 in enumerate(neighbors):
                for neighbor2 in neighbors[:index1]:
                    angles.append((
                        indices[neighbor1], 
                        indices[atom], 
                        indices[neighbor2]
                    ))
                    
        print_section(len(angles), "THETA")
        for counter, (index1, index2, index3) in enumerate(angles):
            print >> f, "% 7i% 7i% 7i" % (index1+1, index2+1, index3+1),
            if counter % 3 == 2:
                print >> f
        if counter % 3 != 2:
            print >> f
        
        print_section(0, "PHI")
        print_section(0, "IMPHI")
        print_section(0, "DON")
        print_section(0, "ACC")
        print_section(0, "NB")
        print_section(0, "GRP")        
        print >> f
        print >> f


dump_filters = {
    "psf": DumpPSF(),
}

