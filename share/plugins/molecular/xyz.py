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


import numpy

from zeobuilder import context
from zeobuilder.filters import LoadFilter, DumpFilter, FilterError
from zeobuilder.nodes.glcontainermixin import GLContainerMixin
import zeobuilder.authors as authors


from molmod.io import XYZReader
from molmod.periodic import periodic
from molmod import angstrom, Translation


class LoadXYZ(LoadFilter):
    authors = [authors.toon_verstraelen]

    def __init__(self):
        LoadFilter.__init__(self, "The XYZ format (*.xyz)")

    def __call__(self, f):
        try:
            xyz_reader = XYZReader(f)
            molecule = xyz_reader.get_first_molecule()
        except XYZError:
            raise FilterError("Could not read the first frame from the XYZ file. Incorrect file format.")

        Universe = context.application.plugins.get_node("Universe")
        universe = Universe()
        Folder = context.application.plugins.get_node("Folder")
        folder = Folder()

        title = molecule.title.strip()
        if len(title) > 0:
            universe.name = title

        Atom = context.application.plugins.get_node("Atom")
        Point = context.application.plugins.get_node("Point")

        for index, number, symbol, coordinate in zip(xrange(molecule.size), molecule.numbers, xyz_reader.symbols, molecule.coordinates):
            extra = {"index": index}
            transl = Translation(coordinate)
            if number == 0:
                atom = Point(name=symbol, extra=extra, transformation=transl)
            else:
                atom = Atom(name=symbol, number=number, extra=extra, transformation=transl)
            universe.add(atom)

        geometries = []
        for title, coordinates in xyz_reader:
            geometries.append(coordinates)

        return [universe, folder]


class DumpXYZ(DumpFilter):
    authors = [authors.toon_verstraelen]

    def __init__(self):
        DumpFilter.__init__(self, "The XYZ format (*.xyz)")

    def __call__(self, f, universe, folder, nodes=None):
        atom_counter = 0
        if nodes is None:
            nodes = [universe]

        Atom = context.application.plugins.get_node("Atom")
        Point = context.application.plugins.get_node("Point")

        def count_xyz_lines(nodes):
            result = 0
            for node in nodes:
                if isinstance(node, Atom):
                    result += 1
                if isinstance(node, Point):
                    result += 1
                else:
                    if isinstance(node, GLContainerMixin):
                        result += count_xyz_lines(node.children)
            return result

        def atom_line(atom):
            coordinate = atom.get_frame_relative_to(universe).t
            print >> f, "% 2s % 13.6f% 13.6f% 13.6f" % (
                (periodic[atom.number].symbol,) + tuple(coordinate/angstrom)
            )

        def point_line(atom):
            coordinate = atom.get_frame_relative_to(universe).t
            print >> f, " X % 13.6f% 13.6f% 13.6f" % (
                tuple(coordinate/angstrom)
            )

        def write_xyz_lines(nodes):
            for node in nodes:
                if isinstance(node, Atom):
                    atom_line(node)
                if isinstance(node, Point):
                    point_line(node)
                else:
                    if isinstance(node, GLContainerMixin):
                        write_xyz_lines(node.children)

        print >> f, ("% 5u" % count_xyz_lines(nodes))
        print >> f, nodes[0].name
        write_xyz_lines(nodes)


load_filters = {
    "xyz": LoadXYZ(),
}

dump_filters = {
    "xyz": DumpXYZ(),
}


