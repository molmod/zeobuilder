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


class LoadG03XYZ(LoadFilter):
    authors = [authors.toon_verstraelen]

    def __init__(self):
        LoadFilter.__init__(self, "The G03XYZ format (*.g03xyz)")

    def __call__(self, f):
        Universe = context.application.plugins.get_node("Universe")
        universe = Universe()
        Folder = context.application.plugins.get_node("Folder")
        folder = Folder()


        Atom = context.application.plugins.get_node("Atom")
        Point = context.application.plugins.get_node("Point")

        counter = 0
        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue
            words = line.split()
            if len(words) < 4:
                continue

            extra = {}
            symbol = words[0]
            if symbol[-3:].lower()=="-bq":
                symbol = symbol[:-3]
                extra["ghost"] = 1
            else:
                extra["ghost"] = 0
            extra["fixed"] = int(words[1] == "-1")
            try:
                if extra["fixed"]:
                    xyz = [float(words[2]), float(words[3]), float(words[4])]
                    extra["oniom"] = " ".join(words[5:])
                else:
                    xyz = [float(words[1]), float(words[2]), float(words[3])]
                    extra["oniom"] = " ".join(words[4:])
            except ValueError:
                raise FilterError("Could not read coordinates. Incorrect floating point format.")
            extra["order"] = counter
            atom_record = periodic[symbol]
            if atom_record is None:
                atom = Point(name=symbol, extra=extra)
            else:
                atom = Atom(name=symbol, number=atom_record.number, extra=extra)
            atom.transformation.t[:] = xyz
            atom.transformation.t *= angstrom
            universe.add(atom)
            counter += 1

        return [universe, folder]


class DumpG03XYZ(DumpFilter):
    authors = [authors.toon_verstraelen]

    def __init__(self):
        DumpFilter.__init__(self, "The G03XYZ format (*.g03xyz)")

    def __call__(self, f, universe, folder, nodes=None):
        atom_counter = 0
        if nodes is None:
            nodes = [universe]

        Atom = context.application.plugins.get_node("Atom")
        Point = context.application.plugins.get_node("Point")

        def atom_line(atom):
            coordinate = atom.get_frame_relative_to(universe).t/angstrom
            if isinstance(atom, Point):
                symbol = "X"
            else:
                symbol = periodic[atom.number].symbol
            if atom.extra.get("ghost", 0):
                symbol += "-Bq"
            if atom.extra.get("fixed", 0):
                symbol += " -1"
            oniom = str(atom.extra.get("oniom", ""))
            print >> f, "  %s % 13.6f% 13.6f% 13.6f %s" % (
                symbol.ljust(7), coordinate[0], coordinate[1], coordinate[2], oniom
            )

        def write_xyz_lines(nodes):
            for node in nodes:
                if isinstance(node, Atom) or isinstance(node, Point):
                    atom_line(node)
                else:
                    if isinstance(node, GLContainerMixin):
                        write_xyz_lines(node.children)

        write_xyz_lines(nodes)


load_filters = {
    "g03xyz": LoadG03XYZ(),
}

dump_filters = {
    "g03xyz": DumpG03XYZ(),
}





