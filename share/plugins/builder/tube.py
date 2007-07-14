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
from zeobuilder.actions.composed import ImmediateWithMemory, Parameters, UserError
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
                minimum=1,
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
        result.max_length = 50*angstrom
        result.max_error = 0.01*angstrom
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

        new_a = n*flat_a - m*flat_b
        radius = numpy.linalg.norm(new_a)/(2*numpy.pi)
        new_x = new_a/numpy.linalg.norm(new_a)
        new_y = numpy.array([-new_x[1], new_x[0]], float)

        new_b = None
        stack_size = 1
        #nominator = numpy.dot(new_x, flat_b)
        stack_vector = flat_b - flat_a*numpy.dot(new_x, flat_b)/numpy.dot(new_x, flat_a)
        stack_length = numpy.linalg.norm(stack_vector)
        nominator = numpy.linalg.norm(stack_vector - flat_b)
        denominator = numpy.linalg.norm(flat_a)
        #print "nominator", nominator
        #print "denominator", denominator
        fraction = nominator/denominator
        while True:
            repeat = fraction*stack_size
            if stack_length*stack_size > self.parameters.max_length:
                break
            #print repeat, round(repeat)
            #print abs(repeat - round(repeat))*denominator, " < ", self.parameters.max_error
            if abs(repeat - round(repeat))*denominator < self.parameters.max_error:
                new_b = stack_vector*stack_size
                break
            stack_size += 1
        if new_b is None:
            raise UserError("Could not create a periodic tube shorter than the given maximum length.")
        rotation = numpy.array([new_x, new_y], float)

        def yield_cells():
            "Yields the indices of the periodic images that are part of the tube."
            to_fractional = numpy.linalg.inv(numpy.array([new_a, new_b]).transpose())
            col_len = int(numpy.linalg.norm(new_a + m*stack_vector)/numpy.linalg.norm(flat_a))+4
            #print "col_len", col_len
            #print "flat_b", flat_b
            #print "stack_vector", stack_vector
            shift = numpy.linalg.norm(flat_b - stack_vector)/numpy.linalg.norm(flat_a)
            #print "shift", shift
            for row in xrange(-m-1, stack_size+1):
                col_start = int(numpy.floor(row*shift))-1
                #print "col_start", col_start, "at", row, row*shift
                for col in xrange(col_start, col_start+col_len):
                    p = col*flat_a + row*flat_b
                    i = numpy.dot(to_fractional, p)
                    #if (i >= 0).all() and (i < 1).all():
                    #if i[1] >= 0 and i[1] < 1:
                    #if ((-row*n <= col*m) and ((stack_size-row)*n > col*m)):
                    #    yield p
                    yield p, (i >= 0).all() and (i < 1).all()


        # first delete everything the universe:
        for child in copy.copy(universe.children):
            primitive.Delete(child)

        Atom = context.application.plugins.get_node("Atom")
        # add the new atoms
        if False:
            rot_a = numpy.dot(rotation, new_a)
            rot_b = numpy.dot(rotation, new_b)
            new_cell = numpy.array([
                [rot_a[0], rot_b[0], 0],
                [rot_a[1], rot_b[1], 0],
                [0, 0, 10],
            ], float)
            primitive.SetProperty(universe, "cell", new_cell)
            primitive.SetProperty(universe, "cell_active", numpy.array([True, True, False], bool))
            primitive.SetProperty(universe, "repetitions", numpy.array([2, 2, 1], int))
            #primitive.SetProperty(universe, "cell_active", numpy.array([False, False, False], bool))
            for p, accept in yield_cells():
                if not accept: continue
                for number, coordinate in yield_pattern():
                    coordinate[:2] += p
                    coordinate[:2] = numpy.dot(rotation, coordinate[:2])
                    translation = Translation()
                    translation.t[:] = coordinate
                    primitive.Add(Atom(number=number, transformation=translation), universe)
        else:
            tube_length = numpy.linalg.norm(new_b)
            #print stack_size, tube_length
            primitive.SetProperty(universe, "cell", numpy.identity(3, float)*tube_length)
            primitive.SetProperty(universe, "cell_active", numpy.array([False, False, True], bool))
            primitive.SetProperty(universe, "repetitions", numpy.array([1, 1, 2], int))
            for p, accept in yield_cells():
                if not accept: continue
                for number, coordinate in yield_pattern():
                    coordinate[:2] += p
                    coordinate[:2] = numpy.dot(rotation, coordinate[:2])
                    translation = Translation()
                    translation.t[0] = (radius+coordinate[2])*numpy.cos(coordinate[0]/radius)
                    translation.t[1] = (radius+coordinate[2])*numpy.sin(coordinate[0]/radius)
                    translation.t[2] = coordinate[1]
                    primitive.Add(Atom(number=number, transformation=translation), universe)




actions = {
    "CreateTube": CreateTube,
}
