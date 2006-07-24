#!/usr/bin/env python
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

import glob
from distutils.core import setup
from distutils.extension import Extension
from Pyrex.Distutils import build_ext

version = '0.1.0'

#setup(
#    name = "Marching cube module",
#    ext_modules=[
#        Extension("marching_cube", sources=["extensions/marching_cube.pyx", "extensions/pure_c/marching_cube.c"])
#    ],
#    cmdclass = {'build_ext': build_ext}
#)

setup(
    name='zeobuilder',
    version=version,
    description='Zeobuilder is a extensible GUI application for molecular model building.',
    author='Toon Verstraelen',
    author_email='Toon.Verstraelen@UGent.be',
    url='http://molmod.ugent.be/zeobuilder/',
    package_dir = {'zeobuilder': 'src'},
    data_files=[
        ('share/zeobuilder/%s/images' % version, glob.glob('share/images/*.svg')),
        ('share/zeobuilder/%s/plugins/core' % version, glob.glob('share/plugins/core/*.py')),
        ('share/zeobuilder/%s/' % version, ['share/zeobuilder.glade'])
    ],
    packages=[
        'zeobuilder',
        'zeobuilder.actions',
        'zeobuilder.actions.collections',
        'zeobuilder.nodes',
        'zeobuilder.gui',
        'zeobuilder.gui.fields',
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
