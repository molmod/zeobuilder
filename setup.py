#!/usr/bin/env python
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

import glob
from distutils.core import setup
#from distutils.extension import Extension
#from Pyrex.Distutils import build_ext


#setup(
#    name = "Marching cube module",
#    ext_modules=[
#        Extension("marching_cube", sources=["extensions/marching_cube.pyx", "extensions/pure_c/marching_cube.c"])
#    ],
#    cmdclass = {'build_ext': build_ext}
#)

setup(
    name='Zeobuilder',
    version='0.001',
    description='Zeobuilder is a extensible GUI application for molecular model building.',
    author='Toon Verstraelen',
    author_email='Toon.Verstraelen@UGent.be',
    url='https://molmod.ugent.be/zeobuilder/',
    package_dir = {'zeobuilder': 'lib/zeobuilder'},
    data_files=[
        ('share/mime/packages/', ["share/mime/zeobuilder.xml"]),
        ('share/applications/', ["share/desktop/zeobuilder.desktop"]),
        ('share/zeobuilder/', [
            "share/zeobuilder.glade", "share/zeobuilder.svg",
            "share/no_action.svg", "share/reference.svg"
        ]),
        ('share/zeobuilder/helpers', glob.glob("share/helpers/*")),
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
    scripts=['scripts/zeobuilder', 'scripts/zb-convert'],
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




