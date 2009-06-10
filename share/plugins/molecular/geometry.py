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
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.actions.composed import Immediate, UserError
from zeobuilder.nodes.glcontainermixin import GLContainerMixin
from zeobuilder.moltools import create_molecular_graph
import zeobuilder.actions.primitive as primitive
import zeobuilder.authors as authors

from molmod.transformations import Translation, coincide

import numpy, gtk


class GuessGeometry(Immediate):
    """Guess the geometry of the selected molecule based on the molecular graph"""
    description = "Guess the molecular geometry"
    menu_info = MenuInfo("default/_Object:tools/_Molecular:geometry","_Guess geometry", ord("g"), False, order=(0, 4, 1, 5, 4, 0))
    authors = [authors.wouter_smet]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        if not isinstance(context.application.cache.node, GLContainerMixin): return False
        if len(context.application.cache.node.children) == 0: return False
        # C) passed all tests:
        return True

    def do(self):
        # Get the molecular graph of the molecule in the selection
        parent = context.application.cache.node
        graph = create_molecular_graph([parent], parent)
        if graph.molecule.size == 0:
            raise UserError("Could not get molecular graph.", "Make sure that the selected frame contains a molecule.")

        # Guessed and original geometry
        opt_cor = graph.guess_geometry().coordinates
        org_cor = graph.molecule.coordinates

        # Transform the guessed geometry as to overlap with the original geometry
        transf = coincide(org_cor, opt_cor)
        print numpy.linalg.eigvalsh(transf.r)
        opt_cor = numpy.dot(opt_cor, transf.r.transpose()) + transf.t
        print org_cor
        print opt_cor

        # Put coordinates of guess geometry back into Zeobuilder model
        for i in xrange(graph.molecule.size):
            translation = Translation()
            atom = graph.molecule.atoms[i]
            # make sure atoms in subframes are treated properly
            transf = atom.parent.get_frame_relative_to(parent)
            org_pos = atom.transformation.t
            opt_pos = transf.vector_apply_inverse(opt_cor[i])
            translation.t = opt_pos - org_pos
            primitive.Transform(graph.molecule.atoms[i], translation)


actions = {
    "GuessGeometry": GuessGeometry,
}


