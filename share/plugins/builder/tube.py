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
from zeobuilder.gui.fields_dialogs import FieldsDialogSimple
import zeobuilder.actions.primitive as primitive
import zeobuilder.gui.fields as fields
import zeobuilder.authors as authors

from molmod.transformations import Translation
from molmod.units import angstrom

import numpy, gtk


class CreateTube(ImmediateWithMemory):
    description = "Create Tube"
    menu_info = MenuInfo("default/_Object:tools/_Builder:generate", "_Create tube", order=(0, 4, 1, 6, 1, 0))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection(parameters=None):
        if not ImmediateWithMemory.analyze_selection(parameters): return False
        cache = context.application.cache
        Universe = context.application.plugins.get_node("Universe")
        if not (len(cache.nodes)==0 or isinstance(cache.node, Universe)): return False
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
        r = 1.4210*angstrom
        ratio = float(m)/n

        flat_a = numpy.array([2*r*numpy.sin(60*numpy.pi/180), 0], float)
        flat_b = numpy.array([  r*numpy.cos(30*numpy.pi/180), r*(1+numpy.sin(30*numpy.pi/180))], float)

        def pattern():
            yield 6, numpy.zeros(2, float)
            yield 6, (flat_a + flat_b)*(2.0/3.0)

        def yield_cells():
            """Yields the indices of the unit cells of the graphene sheet"""
            for row in xrange(-m, n+m):
                col_start = int(numpy.ceil(ratio*row))
                for col in xrange(col_start, col_start+n):
                    if -col*ratio <= row and -(col-m)*ratio > (row-n):
                        yield row, col

        newx = n*flat_a + m*flat_b
        radius = numpy.linalg.norm(newx)/(2*numpy.pi)
        newx /= numpy.linalg.norm(newx)
        newy = numpy.array([-newx[1], newx[0]], float)
        rotation = numpy.array([newx, newy], float)


        Atom = context.application.plugins.get_node("Atom")
        universe = context.application.cache.node
        if universe is None:
            universe = context.application.model.universe
        for i,j in yield_cells():
            for number, coordinate in pattern():
                coordinate += i*flat_a + j*flat_b
                coordinate = numpy.dot(rotation, coordinate)
                translation = Translation()
                translation.t[0] = radius*numpy.cos(coordinate[0]/radius)
                translation.t[1] = radius*numpy.sin(coordinate[0]/radius)
                translation.t[2] = coordinate[1]
                primitive.Add(Atom(number=number, transformation=translation), universe)



actions = {
    "CreateTube": CreateTube,
}
