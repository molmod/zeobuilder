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
            molecule = molecules[0]
            universe.name = molecule.title
            self.load_molecule(universe, molecule)
        else:
            for molecule in molecules:
                parent = Frame(name=molecule.title)
                universe.add(parent)
                self.load_molecule(parent, molecule)

        return [universe, folder]

    def load_molecule(self, parent, molecule):
        parent.extra.update(self.load_extra(molecule.extra))
        Atom = context.application.plugins.get_node("Atom")
        for counter, number, coordinate in zip(xrange(molecule.size), molecule.numbers, molecule.coordinates):
            extra = self.load_extra(molecule.atoms_extra.get(counter, {}))
            extra["index"] = counter
            atom_record = periodic[number]
            atom = Atom(name=atom_record.symbol, number=number, extra=extra)
            atom.transformation.t[:] = coordinate
            parent.add(atom)
            counter += 1
        if molecule.graph is not None:
            Bond = context.application.plugins.get_node("Bond")
            for counter, pair in enumerate(molecule.graph.pairs):
                extra = self.load_extra(molecule.bonds_extra.get(pair, {}))
                name = "Bond %i" % counter
                i,j = pair
                bond = Bond(name=name, targets=[parent.children[i],parent.children[j]], extra=extra)
                parent.add(bond)

    def load_extra(self, extra):
        result = {}
        for key, value in extra.iteritems():
            value = value.strip()
            try:
                result[key] = int(value)
                continue
            except ValueError:
                pass
            try:
                result[key] = float(value)
                continue
            except ValueError:
                pass
            result[key] = str(value)
        return result


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
        atoms_extra = {}
        counter = 0
        numbers = []
        coordinates = []
        for child in parent.children:
            if isinstance(child, Atom):
                atom_to_index[child] = counter
                if len(child.extra) > 0:
                    atoms_extra[counter] = child.extra
                counter += 1
                numbers.append(child.number)
                coordinates.append(child.get_frame_relative_to(universe).t)

        if len(numbers) > 0:
            molecule = Molecule(numbers, coordinates, parent.name)
            molecule.extra = parent.extra
            molecule.atoms_extra = atoms_extra
            molecule.bonds_extra = {}

            pairs = set([])
            for child in parent.children:
                if isinstance(child, Bond):
                    atoms = child.get_targets()
                    pair = frozenset([atom_to_index[atoms[0]], atom_to_index[atoms[1]]])
                    if len(child.extra) > 0:
                        molecule.bonds_extra[pair] = child.extra
                    pairs.add(pair)
            if len(pairs) > 0:
                molecule.graph = MolecularGraph(pairs, molecule.numbers)
            else:
                molecule.graph = None

            result = [molecule]
        else:
            result = []

        for child in parent.children:
            if isinstance(child, Frame):
                result.extend(self.collect_molecules(child, universe))

        return result


load_filters = {
    "cml": LoadCML(),
}

dump_filters = {
    "cml": DumpCML(),
}





