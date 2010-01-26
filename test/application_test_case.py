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


from zeobuilder import context
from zeobuilder.application import TestApplication

import gtk, numpy

import unittest


__all__ = ["ApplicationTestCase"]


class ApplicationTestCase(unittest.TestCase):
    def run_test_application(self, fn, quit=True):
        application = TestApplication(fn, quit)
        error_message = application.error_message
        del context.application
        del context.parent_window
        del application
        if error_message is not None:
            self.assert_(
                False,
                "An Error occured while running the test application:\n%s" % (
                    error_message,
                )
            )

    def assertArraysAlmostEqual(self, a, b, err_threshold=1e-5, do_abserr=False, verbose=False):
        def log(s):
            if verbose: print s
        if a.shape != b.shape:
            self.fail("Array shapes do not match: %s!=%s" % (a.shape, b.shape))
        if do_abserr:
            abserr = abs(a-b).max()
            log("both")
            log(numpy.hstack([a,b]))
            log("difference")
            log(a-b)
            log("abserr: %s" % abserr)
            if abserr > err_threshold:
                self.fail("The absolute error is too large: %.3e > %.3e" % (abserr, err_threshold))
        else:
            relerr = abs(a-b).max()*2/(abs(a).max()+abs(b).max())
            log("both")
            log(numpy.hstack([a,b]))
            #log(a)
            #log(b)
            log("difference")
            log(a-b)
            log("relerr: %s" % relerr)
            if relerr > err_threshold:
                self.fail("The relative error is too large: %.3e > %.3e" % (relerr, err_threshold))
            if numpy.isnan(relerr):
                self.fail("The relative error is nan.")
        if numpy.isnan(a).any():
            self.fail("The first argument contains nan's.")
        if numpy.isnan(b).any():
            self.fail("The second argument contains nan's.")


