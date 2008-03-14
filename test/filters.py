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

    def test_xyz(self):
        self.helper_file_open("tpa.xyz")
        self.helper_file_open("ethane-ethane-pos.xyz")

    def test_pdb(self):
        self.helper_file_open("lau.pdb")
        self.helper_file_open("pept.pdb")


class DumpFilters(ApplicationTestCase):
    def helper_file_save(self, in_filename, out_filename):
        def fn():
            context.application.model.file_open("input/%s" % in_filename)
            context.application.model.file_save("output/%s" % out_filename)
        self.run_test_application(fn)

    def test_zml(self):
        self.helper_file_save("core_objects.zml", "test.zml")

    def test_xyz(self):
        self.helper_file_save("tpa.zml", "test.xyz")

    def test_psf(self):
        self.helper_file_save("precursor.zml", "test.psf")

    def test_pdb(self):
        self.helper_file_save("lau.zml", "test.pdb")





