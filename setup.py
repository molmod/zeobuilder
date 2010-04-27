#!/usr/bin/env python
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

import glob, os
from distutils.core import setup
from distutils.command.install_data import install_data


class MyInstallData(install_data):
    """Add a datadir.txt file that points to the root for the data files. It is
       otherwise impossible to figure out the location of these data files at
       runtime.
    """
    def run(self):
        # Do the normal install_data
        install_data.run(self)
        # Create the file datadir.txt. It's exact content is only known
        # at installation time.
        dist = self.distribution
        libdir = dist.command_obj["install_lib"].install_dir
        for name in dist.packages:
            if '.' not in name:
                destination = os.path.join(libdir, name, "datadir.txt")
                print "Creating %s" % destination
                if not self.dry_run:
                    f = file(destination, "w")
                    print >> f, self.install_dir
                    f.close()


setup(
    name='Zeobuilder',
    version='0.004',
    description='Zeobuilder is a extensible GUI application for molecular model building.',
    author='Toon Verstraelen',
    author_email='Toon.Verstraelen@UGent.be',
    url='http://molmod.ugent.be/code/',
    cmdclass={'install_data': MyInstallData},
    package_dir = {'zeobuilder': 'lib'},
    data_files=[
        ('share/mime/packages/', ["share/mime/zeobuilder.xml"]),
        ('share/applications/', ["share/desktop/zeobuilder.desktop"]),
        ('share/zeobuilder/', [
            "share/zeobuilder.glade", "share/zeobuilder.svg",
            "share/no_action.svg", "share/reference.svg"
        ]),
        ('share/zeobuilder/helpers', glob.glob("share/helpers/*")),
        ('share/zeobuilder/fragments', glob.glob("share/fragments/*")),
    ] + [
        ('share/zeobuilder/plugins/%s' % plugin,
            glob.glob('share/plugins/%s/*.py' % plugin) +
            glob.glob('share/plugins/%s/*.svg' % plugin) +
            glob.glob('share/plugins/%s/*.glade' % plugin)
        ) for plugin
        in ["basic", "molecular", "builder", "sbart"]
    ],
    packages=[
        'zeobuilder',
        'zeobuilder.actions',
        'zeobuilder.actions.collections',
        'zeobuilder.nodes',
        'zeobuilder.gui',
        'zeobuilder.gui.fields',
        'zeobuilder.gui.visual',
    ],
    scripts=['scripts/zeobuilder'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: X11 Applications',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python'
    ]
)


