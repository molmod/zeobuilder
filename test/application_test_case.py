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
from zeobuilder.application import TestApplication

import gtk

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
