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

from zeobuilder import context
from zeobuilder.filters import LoadFilter, DumpFilter, FilterError
from zeobuilder.nodes.glcontainermixin import GLContainerMixin
import zeobuilder.authors as authors


from molmod.data.periodic import periodic
from molmod.units import angstrom
from molmod.io.cml import load_cml, dump_cml
from molmod.molecules import Molecule
from molmod.molecular_graphs import MolecularGraph


class LoadCML(LoadFilter):
    authors = [authors.toon_verstraelen]

    def __init__(self):
        LoadFilter.__init__(self, "The CML format (*.cml)")

    def __call__(self, f):
        Universe = context.application.plugins.get_node("Universe")
        universe = Universe()
        Folder = context.application.plugins.get_node("Folder")
        folder = Folder()

        Frame = context.application.plugins.get_node("Frame")

        molecules = load_cml(f)

        if len(molecules) == 1:
            name, molecule = molecules.items()[0]
            universe.name = name
            self.load_molecule(universe, molecule)
        else:
            for name, molecule in molecules.iteritems():
                parent = Frame(name=name)
                universe.add(parent)
                self.load_molecule(parent, molecule)

        return [universe, folder]

    def load_molecule(self, parent, molecule):
        Atom = context.application.plugins.get_node("Atom")
        for counter, number, coordinate in zip(xrange(molecule.size), molecule.numbers, molecule.coordinates):
            extra = {"order": counter}
            atom_record = periodic[number]
            atom = Atom(name=atom_record.symbol, number=number, extra=extra)
            atom.transformation.t[:] = coordinate
            parent.add(atom)
            counter += 1
        if molecule.graph is not None:
            Bond = context.application.plugins.get_node("Bond")
            for counter, (i,j) in enumerate(molecule.graph.pairs):
                name = "Bond %i" % counter
                bond = Bond(name=name, targets=[parent.children[i],parent.children[j]])
                parent.add(bond)


class DumpCML(DumpFilter):
    authors = [authors.toon_verstraelen]

    def __init__(self):
        DumpFilter.__init__(self, "The CML format (*.cml)")

    def __call__(self, f, universe, folder, nodes=None):
        atom_counter = 0
        if nodes is None:
            nodes = [universe]

        molecules = self.collect_molecules(universe)

        dump_cml(f, molecules)


    def collect_molecules(self, parent, universe=None):
        Atom = context.application.plugins.get_node("Atom")
        Bond = context.application.plugins.get_node("Bond")
        Frame = context.application.plugins.get_node("Frame")


        if universe==None:
            universe = parent

        atom_to_index = {}
        counter = 0
        numbers = []
        coordinates = []
        for child in parent.children:
            if isinstance(child, Atom):
                atom_to_index[child] = counter
                counter += 1
                numbers.append(child.number)
                coordinates.append(child.get_frame_relative_to(universe).t)
        if len(numbers) > 0:
            molecule = Molecule()
            molecule.title = parent.name
            molecule.numbers = numpy.array(numbers)
            molecule.coordinates = numpy.array(coordinates)

            pairs = set([])
            for child in parent.children:
                if isinstance(child, Bond):
                    atoms = child.get_targets()
                    pairs.add(frozenset([
                        atom_to_index[atoms[0]],
                        atom_to_index[atoms[1]]
                    ]))
            if len(pairs) > 0:
                molecule.graph = MolecularGraph(pairs, molecule.numbers)
            else:
                molecule.graph = None

            result = {molecule.title: molecule}
        else:
            result = {}

        for child in parent.children:
            if isinstance(child, Frame):
                molecules = self.collect_molecules(child, universe)
                for name, molecule in molecules.iteritems():
                    if name in result:
                        counter = 0
                        while name + str(counter) in result:
                            counter += 1
                        name += str(counter)
                    result[name] = molecule

        return result


load_filters = {
    "cml": LoadCML(),
}

dump_filters = {
    "cml": DumpCML(),
}





