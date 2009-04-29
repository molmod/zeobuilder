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


import os, sys

class Context(object):
    def __init__(self):
        self.title = "Zeobuilder"
        self.user_dir = os.path.expanduser("~/.zeobuilder")
        self.config_filename = os.path.join(self.user_dir, "settings")
        fn_datadir = os.path.join(os.path.dirname(__file__), "datadir.txt")
        if os.path.isfile(fn_datadir):
            f = file(fn_datadir)
            datadir = f.readline().strip()
            f.close()
            self.share_dir = os.path.join(datadir, "share", "zeobuilder")
        else:
            self.share_dir = "../share" # When running from the build directory for the tests.

    def get_share_filename(self, filename):
        result = os.path.join(self.share_dir, filename)
        if not os.path.isfile(result):
            raise ValueError("Data file '%s' not found." % result)
        return result


context = Context()




