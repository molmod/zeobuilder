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
from zeobuilder.nodes.parent_mixin import ContainerMixin

from molmod.data.periodic import periodic
from molmod.graphs import Graph
from molmod.molecules import Molecule
from molmod.molecular_graphs import MolecularGraph


__all__ = [
    "yield_atoms", "yield_bonds", "chemical_formula",
    "create_molecule", "create_molecular_graph"
]


def yield_atoms(nodes):
    Atom = context.application.plugins.get_node("Atom")
    for node in nodes:
        if isinstance(node, Atom):
            yield node
        elif isinstance(node, ContainerMixin):
            for atom in yield_atoms(node.children):
                yield atom


def yield_bonds(nodes):
    Bond = context.application.plugins.get_node("Bond")
    for node in nodes:
        if isinstance(node, Bond):
            yield node
        elif isinstance(node, ContainerMixin):
            for bond in yield_bonds(node.children):
                yield bond


def chemical_formula(atoms, markup=False):
    atom_counts = {}
    total = 0
    for atom in atoms:
        if atom.number in atom_counts:
            atom_counts[atom.number] += 1
        else:
            atom_counts[atom.number] = 1
        total += 1
    items = atom_counts.items()
    items.sort()
    items.reverse()
    if markup:
        formula = "".join(
            "%s<sub>%i</sub>" % (periodic[atom_number].symbol, count)
            for atom_number, count in items
        )
    else:
        formula = " ".join(
            "%s%i" % (periodic[atom_number].symbol, count)
            for atom_number, count in items
        )
    return total, formula


def create_molecule(selected_nodes):
    numbers = []
    coordinates = []
    atoms = list(yield_atoms(selected_nodes))
    for atom in atoms:
        numbers.append(atom.number)
        coordinates.append(atom.get_absolute_frame().t)
    result = Molecule()
    result.atoms = atoms
    result.numbers = numpy.array(numbers)
    result.coordinates = numpy.array(coordinates)
    return result


def create_molecular_graph(selected_nodes):
    molecule = create_molecule(selected_nodes)

    atom_indexes = dict((atom,i) for i,atom in enumerate(molecule.atoms))
    bonds = list(
        bond for bond in yield_bonds(selected_nodes)
        if bond.children[0].target in atom_indexes and
           bond.children[1].target in atom_indexes
    )
    pairs = [(
        atom_indexes[bond.children[0].target],
        atom_indexes[bond.children[1].target],
    ) for bond in bonds]

    graph = MolecularGraph(pairs, molecule.numbers)
    graph.bonds = bonds
    graph.molecule = molecule
    return graph


