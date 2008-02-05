#! /usr/bin/env python
# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 Toon Verstraelen <Toon.Verstraelen@UGent.be>
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

import sys, glob, os
retcode = os.system("(cd ..; python setup.py build)")
if retcode != 0: sys.exit(retcode)
sys.path.insert(0, glob.glob("../build/lib*")[0])

from zeobuilder import context
context.share_dirs = ["../share"]

import pygtk, optparse


def init_fn_new():
    from zeobuilder import context
    FileNew = context.application.plugins.get_action("FileNew")
    FileNew()

class InitFnOpen:
    def __init__(self, filename):
        self.filename = filename

    def __call__(self):
        from zeobuilder import context
        from zeobuilder.models import FilenameError
        from zeobuilder.filters import FilterError
        import gtk
        try:
            context.application.model.file_open(self.filename)
        except (FilenameError, FilterError), e:
            print str(e)
            gtk.main_quit()
            sys.exit(2)



usage="""Usage: zeobuilder [filename]
Zeobuilder is an extensible GUI-toolkit for molecular model construction.
The filename argument is optional."""

parser = optparse.OptionParser(usage)
(options, args) = parser.parse_args()


if len(args) == 0:
    init_fn = init_fn_new
elif len(args) == 1:
    filename = args[0]
    if os.path.isfile(filename):
        init_fn = InitFnOpen(filename)
    else:
        parser.error("File %s does not exist." % filename)
else:
    parser.error("Expecting at most one argument.")

from zeobuilder.application import Application
Application(init_fn)



