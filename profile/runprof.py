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


import os.path
if not os.path.exists("init_files.py"):
    os.symlink("../debug/init_files.py", "init_files.py")
from init_files import init_files
init_files()


from zeobuilder.application import TestApplication
from zeobuilder import context




def preparation_fn():
    context.application.model.file_open("input/precursor.zml")
    context.application.main.select_nodes(context.application.model.universe.children)
    Duplicate = context.application.plugins.get_action("Duplicate")
    for i in xrange(10):
        Duplicate()
    print len(context.application.model.universe.children[0].children)
    context.application.main.select_nodes(context.application.model.universe.children)


def measure_fn():
    Frame = context.application.plugins.get_action("Frame")
    Frame()


if __name__ == "__main__":
    def profile_fn():
        preparation_fn()
        import profile
        profile.runctx('fn()', {"fn": measure_fn}, {}, 'test.prof')

    application = TestApplication(profile_fn)
    error_message = application.error_message
    del context.application
    del context.parent_window
    del application
    if error_message is not None:
        print "An Error occured while running the test application:"
        print error_message
    else:
        import pstats
        p = pstats.Stats('test.prof')
        p.strip_dirs().sort_stats('time').print_stats()
        p.print_callers()


