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


from zeobuilder import context
from zeobuilder.actions.composed import ImmediateWithMemory, Parameters, UserError
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.moltools import yield_atoms
from zeobuilder.undefined import Undefined
from zeobuilder.gui.fields_dialogs import FieldsDialogSimple
import zeobuilder.actions.primitive as primitive
import zeobuilder.gui.fields as fields
import zeobuilder.authors as authors

from molmod import Translation, angstrom, UnitCell

import numpy, gtk


class CreateTube(ImmediateWithMemory):
    description = "Create Tube"
    menu_info = MenuInfo("default/_Object:tools/_Builder:generate", "_Create tube", order=(0, 4, 1, 6, 1, 0))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection(parameters=None):
        if not ImmediateWithMemory.analyze_selection(parameters): return False
        if context.application.model.universe.cell.active.sum() != 2: return False
        return True

    parameters_dialog = FieldsDialogSimple(
        "Tube parameters",
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
            fields.edit.CheckButton(
                label_text="Flat",
                attribute_name="flat",
            ),
            fields.optional.RadioOptional(
                fields.group.Table(
                    label_text="Periodic (along tube axis)",
                    fields=[
                        fields.faulty.Length(
                            label_text="Maximum tube length",
                            attribute_name="max_length",
                            low=0.0,
                            low_inclusive=False,
                        ),
                        fields.faulty.Length(
                            label_text="Maximum mismatch",
                            attribute_name="max_error",
                            low=0.0,
                            low_inclusive=False,
                        ),
                    ]
                )
            ),
            fields.optional.RadioOptional(
                fields.group.Table(
                    label_text="Not periodic",
                    fields=[
                        fields.faulty.Length(
                            label_text="Tube length",
                            attribute_name="tube_length",
                            low=0.0,
                            low_inclusive=False,
                        ),
                    ]
                )
            ),
        ]),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK)),
    )

    @classmethod
    def default_parameters(cls):
        result = Parameters()
        result.n = 5
        result.m = 1
        result.flat = False
        result.max_length = 50*angstrom
        result.max_error = 0.01*angstrom
        result.tube_length = Undefined(50*angstrom)
        return result

    def do(self):
        # the indices (n,m) that define the tube, see e.g. the wikipedia page
        # about nanotubes for the interpretation of these indices:
        # http://en.wikipedia.org/wiki/Carbon_nanotube
        n = self.parameters.n
        m = self.parameters.m

        periodic_tube = isinstance(self.parameters.tube_length, Undefined)

        universe = context.application.model.universe

        def define_flat():
            "Reads and converts the unit cell vectors from the current model."
            # some parts of the algorithm have been arranged sub functions like
            # these, to reduce the number of local variables in self.do. This
            # should also clarify the code.
            active, inactive = universe.cell.active_inactive
            lengths, angles = universe.cell.parameters
            a = lengths[active[0]]
            b = lengths[active[1]]
            theta = angles[inactive[0]]
            return (
                numpy.array([a, 0], float),
                numpy.array([b*numpy.cos(theta), b*numpy.sin(theta)], float)
            )

        flat_a, flat_b = define_flat()

        def create_pattern():
            "Read the atom positions and transform them to the flat coordinates"
            active, inactive = universe.cell.active_inactive
            a = universe.cell.matrix[:,active[0]]
            b = universe.cell.matrix[:,active[1]]
            c = numpy.cross(a,b)
            tmp_cell = UnitCell(numpy.array([a,b,c]).transpose())
            rotation = tmp_cell.alignment_a

            return [
                (atom.number, rotation*atom.get_absolute_frame().t)
                for atom in yield_atoms([universe])
            ]

        pattern = create_pattern()

        def define_big_periodic():
            "Based on (n,m) calculate the size of the periodic sheet (that will be folded into a tube)."
            big_a = n*flat_a - m*flat_b
            norm_a = numpy.linalg.norm(big_a)
            radius = norm_a/(2*numpy.pi)
            big_x = big_a/norm_a
            big_y = numpy.array([-big_x[1], big_x[0]], float)

            big_b = None
            stack_vector = flat_b - flat_a*numpy.dot(big_x, flat_b)/numpy.dot(big_x, flat_a)
            stack_length = numpy.linalg.norm(stack_vector)
            nominator = numpy.linalg.norm(stack_vector - flat_b)
            denominator = numpy.linalg.norm(flat_a)
            fraction = nominator/denominator
            stack_size = 1
            while True:
                repeat = fraction*stack_size
                if stack_length*stack_size > self.parameters.max_length:
                    break
                if abs(repeat - round(repeat))*denominator < self.parameters.max_error:
                    big_b = stack_vector*stack_size
                    break
                stack_size += 1
            if big_b is None:
                raise UserError("Could not create a periodic tube shorter than the given maximum length.")
            rotation = numpy.array([big_x, big_y], float)
            return big_a, big_b, rotation, stack_vector, stack_size, radius

        def define_big_not_periodic():
            "Based on (n,m) calculate the size of the non-periodic sheet (that will be folded into a tube)."
            big_a = n*flat_a - m*flat_b
            norm_a = numpy.linalg.norm(big_a)
            radius = norm_a/(2*numpy.pi)
            big_x = big_a/norm_a
            big_y = numpy.array([-big_x[1], big_x[0]], float)

            stack_vector = flat_b - flat_a*numpy.dot(big_x, flat_b)/numpy.dot(big_x, flat_a)
            stack_length = numpy.linalg.norm(stack_vector)
            stack_size = int(self.parameters.tube_length/stack_length)
            big_b = stack_vector*stack_size
            rotation = numpy.array([big_x, big_y], float)
            return big_a, big_b, rotation, stack_vector, stack_size, radius


        if periodic_tube:
            big_a, big_b, rotation, stack_vector, stack_size, radius = define_big_periodic()
        else:
            big_a, big_b, rotation, stack_vector, stack_size, radius = define_big_not_periodic()

        def yield_translations():
            "Yields the indices of the periodic images that are part of the tube."
            to_fractional = numpy.linalg.inv(numpy.array([big_a, big_b]).transpose())
            col_len = int(numpy.linalg.norm(big_a + m*stack_vector)/numpy.linalg.norm(flat_a))+4
            shift = numpy.dot(stack_vector - flat_b, flat_a)/numpy.linalg.norm(flat_a)**2
            for row in xrange(-m-1, stack_size+1):
                col_start = int(numpy.floor(row*shift))-1
                for col in xrange(col_start, col_start+col_len):
                    p = col*flat_a + row*flat_b
                    i = numpy.dot(to_fractional, p)
                    if (i >= 0).all() and (i < 1-1e-15).all():
                        yield p
                    #yield p, (i >= 0).all() and (i < 1).all()

        def yield_pattern():
            for number, coordinate in pattern:
                yield number, coordinate.copy()

        # first delete everything the universe:
        while len(universe.children) > 0:
            primitive.Delete(universe.children[0])

        # add the new atoms
        Atom = context.application.plugins.get_node("Atom")
        if self.parameters.flat:
            rot_a = numpy.dot(rotation, big_a)
            rot_b = numpy.dot(rotation, big_b)
            big_matrix = numpy.array([
                [rot_a[0], rot_b[0], 0],
                [rot_a[1], rot_b[1], 0],
                [0, 0, 10*angstrom],
            ], float)
            big_cell = UnitCell(big_cell, numpy.array([True, periodic_tube, False], bool))
            primitive.SetProperty(universe, "cell", big_cell)
            for p in yield_translations():
                for number, coordinate in yield_pattern():
                    coordinate[:2] += p
                    coordinate[:2] = numpy.dot(rotation, coordinate[:2])
                    translation = Translation(coordinate)
                    primitive.Add(Atom(number=number, transformation=translation), universe)
        else:
            tube_length = numpy.linalg.norm(big_b)
            big_matrix = numpy.diag([radius*2, radius*2, tube_length])
            big_cell = UnitCell(big_matrix, numpy.array([False, False, periodic_tube], bool))
            primitive.SetProperty(universe, "cell", big_cell)
            for p in yield_translations():
                for number, coordinate in yield_pattern():
                    coordinate[:2] += p
                    coordinate[:2] = numpy.dot(rotation, coordinate[:2])
                    translation = Translation(numpy.array([
                        (radius+coordinate[2])*numpy.cos(coordinate[0]/radius),
                        (radius+coordinate[2])*numpy.sin(coordinate[0]/radius),
                        coordinate[1],
                    ]))
                    primitive.Add(Atom(number=number, transformation=translation), universe)




actions = {
    "CreateTube": CreateTube,
}


