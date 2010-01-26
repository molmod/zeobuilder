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


import numpy

from zeobuilder import context
from zeobuilder.filters import LoadFilter, DumpFilter, FilterError
from zeobuilder.nodes.glcontainermixin import GLContainerMixin
import zeobuilder.authors as authors


from molmod.periodic import periodic
from molmod import angstrom, deg, Translation


class LoadG03ZMAT(LoadFilter):
    authors = [authors.toon_verstraelen]

    def __init__(self):
        LoadFilter.__init__(self, "The Gaussian Z-Matrix format (*.g03zmat)")

    def __call__(self, f):
        Universe = context.application.plugins.get_node("Universe")
        universe = Universe()
        Folder = context.application.plugins.get_node("Folder")
        folder = Folder()

        Atom = context.application.plugins.get_node("Atom")
        Point = context.application.plugins.get_node("Point")

        # read the z-matrix
        symbols = []
        labels = []
        indices = []
        for line in f:
            words = line.split()
            if len(words) == 0:
                break
            if len(symbols) < 3 and len(words) != 2*len(symbols)+1:
                raise FilterError("The number of fields in the first three lines is incorrect.")
            if len(symbols) >= 3 and len(words) != 7:
                raise FilterError("Each line in the z-matrix must contain 7 fields, except for the first three lines.")
            symbols.append(words[0])
            try:
                indices.append(tuple(int(word)-1 for word in words[1::2]))
            except ValueError:
                raise FilterError("Indices in the z-matrix must be integers")
            labels.append(tuple(words[2::2]))

        # read the label-value map
        mapping = {}
        for line in f:
            words = line.split()
            if len(words) == 0:
                break
            if len(words) != 2:
                raise FilterError("The label-value mapping below the z-matrix must have two fields on each line.")
            try:
                mapping[words[0]] = float(words[1])
            except ValueError:
                raise FilterError("The second field in the label-value mapping below the z-matrix must be a floating point value.")

        # convert labels to values
        values = []
        for row in labels:
            tmp = []
            for label in row:
                value = mapping.get(label)
                if value is None:
                    try:
                        value = float(label)
                    except ValueError:
                        raise FilterError("Could not look up the label '%s' and could not convert it to a floating point value." % label)
                if len(tmp) == 0:
                    value *= angstrom # convert distances to atomic units
                else:
                    value *= deg # convert angles to radians
                tmp.append(value)
            values.append(tmp)


        # now turn all this into cartesian coordinates.
        coordinates = numpy.zeros((len(symbols),3),float)

        # special cases for the first coordinates
        coordinates[1,2] = values[1][0]
        delta_z = numpy.sign(coordinates[indices[2][1],2] - coordinates[indices[2][0],2])
        coordinates[2,2] = values[2][0]*delta_z*numpy.cos(values[2][1])
        coordinates[2,1] = values[2][0]*delta_z*numpy.sin(values[2][1])
        coordinates[2] += coordinates[indices[2][0]]

        for i, irow, vrow in zip(xrange(3,len(indices)), indices[3:], values[3:]):
            tmp_z = coordinates[irow[1]] - coordinates[irow[0]]
            tmp_z /= numpy.linalg.norm(tmp_z)
            tmp_x = coordinates[irow[2]] - coordinates[irow[1]]
            tmp_x -= tmp_z*numpy.dot(tmp_z, tmp_x)
            tmp_x /= numpy.linalg.norm(tmp_x)
            tmp_y = numpy.cross(tmp_z, tmp_x)

            x = vrow[0]*numpy.cos(vrow[2])*numpy.sin(vrow[1])
            y = vrow[0]*numpy.sin(vrow[2])*numpy.sin(vrow[1])
            z = vrow[0]*numpy.cos(vrow[1])
            coordinates[i] = x*tmp_x + y*tmp_y + z*tmp_z + coordinates[irow[0]]

        for i, symbol, coordinate in zip(xrange(len(symbols)), symbols, coordinates):
            extra = {"index": i}
            atom_record = periodic[symbol]
            translation = Translation(coordinate)
            if atom_record is None:
                atom = Point(name=symbol, transformation=translation, extra=extra)
            else:
                atom = Atom(name=symbol, number=atom_record.number, transformation=translation, extra=extra)
            universe.add(atom)

        return [universe, folder]


load_filters = {
    "g03zmat": LoadG03ZMAT(),
}


