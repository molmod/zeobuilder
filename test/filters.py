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


from application_test_case import ApplicationTestCase

from zeobuilder import context
from zeobuilder.actions.composed import Parameters

import gtk, numpy


__all__ = ["LoadFilters", "DumpFilters"]


class LoadFilters(ApplicationTestCase):
    def helper_file_open(self, filename):
        def fn():
            context.application.model.file_open("input/%s" % filename)
        self.run_test_application(fn)

    def test_zml(self):
        self.helper_file_open("core_objects.zml")
        # old file formats
        self.helper_file_open("format1_0.1.zml")
        self.helper_file_open("format2_0.1.zml")
        self.helper_file_open("format3_0.1.zml")

    def test_xyz(self):
        self.helper_file_open("tpa.xyz")
        self.helper_file_open("ethane-ethane-pos.xyz")

    def test_g03xyz(self):
        self.helper_file_open("oniom.g03xyz")

    def test_pdb(self):
        self.helper_file_open("lau.pdb")
        self.helper_file_open("pept.pdb")

    def test_g03zmat(self):
        self.helper_file_open("1LJL_Cys10.g03zmat")

    def test_cml(self):
        self.helper_file_open("diethylene_glycol.cml")


class DumpFilters(ApplicationTestCase):
    def helper_file_save(self, in_filename, out_filename):
        def fn():
            context.application.model.file_open("input/%s" % in_filename)
            context.application.model.file_save("output/%s" % out_filename)
        self.run_test_application(fn)

    def test_zml(self):
        self.helper_file_save("core_objects.zml", "core_objects.zml")

    def test_xyz(self):
        self.helper_file_save("tpa.zml", "tpa.xyz")

    def test_g03xyz(self):
        self.helper_file_save("oniom.zml", "oniom.g03xyz")

    def test_psf(self):
        self.helper_file_save("precursor.zml", "precursor.psf")
        self.helper_file_save("azaallyl_thf_mm.zml", "azaallyl_thf_mm.psf")

    def test_pdb(self):
        self.helper_file_save("lau.zml", "lau.pdb")

    def test_cml(self):
        self.helper_file_save("precursor.zml", "precursor.cml")


