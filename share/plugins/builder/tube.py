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


from zeobuilder import context
from zeobuilder.actions.composed import ImmediateWithMemory, Parameters
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.moltools import yield_atoms
from zeobuilder.gui.fields_dialogs import FieldsDialogSimple
import zeobuilder.actions.primitive as primitive
import zeobuilder.gui.fields as fields
import zeobuilder.authors as authors

from molmod.transformations import Translation
from molmod.units import angstrom
from molmod.unit_cell import UnitCell

import numpy, gtk, copy


class CreateTube(ImmediateWithMemory):
    description = "Create Tube"
    menu_info = MenuInfo("default/_Object:tools/_Builder:generate", "_Create tube", order=(0, 4, 1, 6, 1, 0))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection(parameters=None):
        if not ImmediateWithMemory.analyze_selection(parameters): return False
        if context.application.model.universe.cell_active.sum() != 2: return False
        return True

    parameters_dialog = FieldsDialogSimple(
        "Connection scanner parameters",
        fields.group.Table(fields=[
            fields.faulty.Int(
                label_text="n",
                attribute_name="n",
                minimum=0,
                maximum=100,
            ),
            fields.faulty.Int(
                label_text="m",
                attribute_name="m",
                minimum=0,
                maximum=100,
            ),
        ], cols=2),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK)),
    )

    @classmethod
    def default_parameters(cls):
        result = Parameters()
        result.n = 5
        result.m = 1
        return result

    def do(self):
        n = self.parameters.n
        m = self.parameters.m
        ratio = float(m)/n

        universe = context.application.model.universe

        active, inactive = universe.get_active_inactive()
        lengths, angles = universe.get_parameters()
        a = lengths[active[0]]
        b = lengths[active[1]]
        theta = angles[inactive[0]]
        flat_a = numpy.array([a, 0], float)
        flat_b = numpy.array([b*numpy.cos(theta), b*numpy.sin(theta)], float)

        tmp_cell = UnitCell()
        tmp_cell.add_cell_vector(universe.cell[:,active[0]])
        tmp_cell.add_cell_vector(universe.cell[:,active[1]])
        r = tmp_cell.calc_align_rotation_matrix()

        pattern = [
            (atom.number, numpy.dot(r, atom.get_absolute_frame().t))
            for atom in yield_atoms([universe])
        ]

        def yield_pattern():
            for number, coordinate in pattern:
                yield number, coordinate.copy()

        def yield_cells():
            "Yields the indices of the periodic images that are part of the tube."
            for row in xrange(-m-1, n+m):
                col_start = int(numpy.ceil(ratio*row))
                for col in xrange(col_start, col_start+n+1):
                    if -col*ratio <= row and -(col-m)*ratio > (row-n):
                        yield col, row

        newa = n*flat_a - m*flat_b
        newb = m*flat_a + n*flat_b
        radius = numpy.linalg.norm(newa)/(2*numpy.pi)
        newx = newa/numpy.linalg.norm(newa)
        newy = numpy.array([-newx[1], newx[0]], float)
        rotation = numpy.array([newx, newy], float)

        # first delete everything the universe:
        for child in copy.copy(universe.children):
            primitive.Delete(child)

        Atom = context.application.plugins.get_node("Atom")
        # add the new atoms
        if False:
            new_cell = numpy.array([
                [newa[0], newb[0], 0],
                [newa[1], newb[1], 0],
                [0, 0, 10],
            ], float)
            primitive.SetProperty(universe, "cell", new_cell)
            primitive.SetProperty(universe, "cell_active", numpy.array([True, True, False], bool))
            for i,j in yield_cells():
                for number, coordinate in yield_pattern():
                    coordinate[:2] += i*flat_a + j*flat_b
                    translation = Translation()
                    translation.t[:] = coordinate
                    primitive.Add(Atom(number=number, transformation=translation), universe)
        else:
            tube_length = numpy.dot(rotation, newb)[1]
            print tube_length
            primitive.SetProperty(universe, "cell", numpy.identity(3, float)*tube_length)
            primitive.SetProperty(universe, "cell_active", numpy.array([False, False, True], bool))
            for i,j in yield_cells():
                for number, coordinate in yield_pattern():
                    coordinate[:2] += i*flat_a + j*flat_b
                    coordinate[:2] = numpy.dot(rotation, coordinate[:2])
                    translation = Translation()
                    translation.t[0] = (radius+coordinate[2])*numpy.cos(coordinate[0]/radius)
                    translation.t[1] = (radius+coordinate[2])*numpy.sin(coordinate[0]/radius)
                    translation.t[2] = coordinate[1]
                    primitive.Add(Atom(number=number, transformation=translation), universe)




actions = {
    "CreateTube": CreateTube,
}
