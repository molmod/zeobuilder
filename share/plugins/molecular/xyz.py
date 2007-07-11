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


from ccio.xyz import XYZReader
from molmod.data import periodic
from molmod.units import angstrom


class LoadXYZ(LoadFilter):
    authors = [authors.toon_verstraelen]

    def __init__(self):
        LoadFilter.__init__(self, "The XYZ format (*.xyz)")

    def __call__(self, f):
        xyz_reader = XYZReader(f)
        molecule = xyz_reader.get_first_molecule()

        Universe = context.application.plugins.get_node("Universe")
        universe = Universe()
        Folder = context.application.plugins.get_node("Folder")
        folder = Folder()

        if len(molecule.title) > 0:
            universe.name = molecule.title

        Atom = context.application.plugins.get_node("Atom")
        Point = context.application.plugins.get_node("Point")

        for number, symbol, coordinate in zip(molecule.numbers, xyz_reader.symbols, molecule.coordinates):
            if number == 0:
                atom = Point(name=symbol)
            else:
                atom = Atom(name=symbol, number=number)
            atom.transformation.t = coordinate
            universe.add(atom)

        geometries = []
        for title, coordinates in xyz_reader:
            geometries.append(coordinates)
        if len(geometries) > 1:
            geometries = numpy.array(geometries)
            Trajectory = context.application.plugins.get_node("Trajectory")
            trajectory = Trajectory(targets=universe.children, frames=geometries)
            folder.add(trajectory)

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
    "geom": LoadXYZ(),
}

dump_filters = {
    "xyz": DumpXYZ(),
    "geom": DumpXYZ(),
}

