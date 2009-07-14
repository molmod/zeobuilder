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
from zeobuilder.moltools import create_molecular_graph, create_molecule
import zeobuilder.actions.primitive as primitive
import zeobuilder.authors as authors

from molmod.transformations import Translation, superpose
from molmod.toyff import guess_geometry, tune_geometry
from molmod.data.periodic import periodic
from molmod.units import angstrom

import numpy, gtk, tempfile, os


def coords_to_zeobuilder(org_coords, opt_coords, graph, parent):
    for group in graph.independent_nodes:
        group_org = numpy.array([org_coords[i] for i in group])
        group_opt = numpy.array([opt_coords[i] for i in group])
        # Transform the guessed geometry as to overlap with the original geometry
        transf = superpose(group_org, group_opt)
        group_opt = numpy.dot(group_opt, transf.r.transpose()) + transf.t

        # Put coordinates of guess geometry back into Zeobuilder model
        for i,atomindex in enumerate(group):
            translation = Translation()
            atom = graph.molecule.atoms[atomindex]
            # Make sure atoms in subframes are treated properly
            transf = atom.parent.get_frame_relative_to(parent)
            org_pos = atom.transformation.t
            opt_pos = transf.vector_apply_inverse(group_opt[i]) #
            translation.t = opt_pos - org_pos
            primitive.Transform(atom, translation)

class GuessGeometry(Immediate):
    """Guess the geometry of the selected molecule based on the molecular graph"""
    description = "Guess the molecular geometry"
    menu_info = MenuInfo("default/_Object:tools/_Molecular:geometry","_Guess geometry", ord("g"), False, order=(0, 4, 1, 5, 4, 0))
    authors = [authors.wouter_smet, authors.toon_verstraelen]

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
        opt_coords = guess_geometry(graph).coordinates
        org_coords = graph.molecule.coordinates

        coords_to_zeobuilder(org_coords, opt_coords, graph, parent)

class TuneGeometry(Immediate):
    """Tune the geometry of the selected molecule based on the molecular graph"""
    description = "Tune the molecular geometry"
    menu_info = MenuInfo("default/_Object:tools/_Molecular:geometry","_Tune geometry", ord("t"), False, order=(0, 4, 1, 5, 4, 1))
    authors = [authors.wouter_smet, authors.toon_verstraelen]

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
        opt_coords = tune_geometry(graph, graph.molecule).coordinates
        org_coords = graph.molecule.coordinates

        coords_to_zeobuilder(org_coords, opt_coords, graph.molecule.atoms, parent)


class OptimizeMopacPM3(Immediate):
    """Plugin that calls Mopac to optimize the geometry at PM3 level"""
    description = "Optimize geometry at PM3 level with Mopac"
    menu_info = MenuInfo("default/_Object:tools/_Molecular:geometry","Optimize geometry (PM3, Mopac)", ord("p"), False, order=(0, 4, 1, 5, 4, 2))
    authors = [authors.wouter_smet, authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        if not isinstance(context.application.cache.node, GLContainerMixin): return False
        if len(context.application.cache.node.children) == 0: return False
        # C) passed all tests:
        return True

    def write_mopac_input(self, molecule, prefix):
        f = open('%s.dat' % prefix, 'w')
        print >> f, 'PM3 GNORM=0.01 XYZ'
        print >> f, 'comment1'
        print >> f, 'comment2'
        for i in xrange(molecule.size):
            symbol = periodic[molecule.numbers[i]].symbol
            c = molecule.coordinates[i]/angstrom
            print >> f, "% 2s % 8.5f 1 % 8.5f 1 % 8.5f 1" % (symbol, c[0], c[1], c[2])
        f.close()

    def read_mopac_output(self, filename, num_atoms):
        if not os.path.isfile(filename):
            raise UserError("Could not find Mopac output file.", "Expected location of output file: %s" % filename)
        f = open(filename,'r')
        coordinates = numpy.zeros((num_atoms, 3), float)
        success = False
        for line in f:
            if line == "          CARTESIAN COORDINATES \n":
                break
        for line in f:
            if line == "          CARTESIAN COORDINATES \n":
                success = True
                break
        if success:
            for i in xrange(3):
                f.next()
            i = 0
            for line in f:
                if i < num_atoms:
                    words = line.split()
                    coordinates[i,0] = float(words[2])
                    coordinates[i,1] = float(words[3])
                    coordinates[i,2] = float(words[4])
                    i +=1
                else:
                    break
        else:
            raise UserError("Could not find optimal coordinates.", "Check the file %s for more details." % filename)

        f.close()
        return coordinates*angstrom

    def do(self):
        parent = context.application.cache.node
        org_mol = create_molecule([parent], parent)
        org_coords = org_mol.coordinates
        print type(org_coords)
        if org_mol.size == 0:
            raise UserError("Could not get molecule.", "Make sure that the selected frame contains a molecule.")
        if org_mol.size == 3:
            raise UserError("For the moment three atoms are not supported.")


        # Make temp directory
        work = tempfile.mkdtemp("_zeobuilder_mopac")

        # Create mopac input file
        self.write_mopac_input(org_mol, os.path.join(work, 'mopac'))

        # Run input file through mopac and capture output in file object
        retcode = os.system('cd %s; run_mopac7 mopac > mopac.out' % work)
        if retcode != 0:
            raise UserError("Failed to run Mopac.", "Check that the run_mopac7 binary is in the path. The input file can be found here: %s." % work)
        opt_coords = self.read_mopac_output(os.path.join(work, 'mopac.out'), org_mol.size)

        # clean up
        def safe_remove(filename):
            filename = os.path.join(work, filename)
            if os.path.isfile(filename):
                os.remove(filename)
        safe_remove("mopac.dat")
        safe_remove("mopac.log")
        safe_remove("mopac.out")
        safe_remove("mopac.arc")
        os.rmdir(work)

        coords_to_zeobuilder(org_coords, opt_coords, org_mol.atoms, parent)


actions = {
    "GuessGeometry": GuessGeometry,
    "TuneGeometry": TuneGeometry,
    "OptimizeMopacPM3": OptimizeMopacPM3
}


