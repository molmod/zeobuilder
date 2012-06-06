# -*- coding: utf-8 -*-
# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 - 2012 Toon Verstraelen <Toon.Verstraelen@UGent.be>, Center
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
#--


from zeobuilder import context
from zeobuilder.filters import LoadFilter, DumpFilter, FilterError
from zeobuilder.zml import load_from_file, dump_to_file
from zeobuilder.plugins import PluginNotFoundError
import zeobuilder.authors as authors


class LoadZML(LoadFilter):
    authors = [authors.toon_verstraelen]

    def __init__(self):
        LoadFilter.__init__(self, "Zeobuilder Markup Language (*.zml)")

    def __call__(self, f):
        try:
            root = load_from_file(f)
            return root[0], root[1]
        except PluginNotFoundError, e:
            raise FilterError("The file contains a node Class (%s) for which no appropriate plugin can be found." % e.name)
        except ValueError, e:
            raise FilterError("A ValueError occured when reading the file: %s" % str(e))


class DumpZML(DumpFilter):
    authors = [authors.toon_verstraelen]

    def __init__(self):
        DumpFilter.__init__(self, "Zeobuilder Markup Language (*.zml)")

    def __call__(self, f, universe, folder, nodes=None):
        if nodes is None:
            dump_to_file(f, [universe, folder])
        else:
            Universe = context.application.plugins.get_node(name="Universe")
            new_universe = Universe()
            new_universe.children = [node for node in nodes if node.is_indirect_child_of(universe)]
            Folder = context.application.plugins.get_node("Folder")
            new_folder = Folder(name="Root folder")
            new_folder.children = [node for node in nodes if node.is_indirect_child_of(folder)]
            dump_to_file(f, [new_universe, new_folder])


load_filters = {
    "zml": LoadZML(),
}

dump_filters = {
    "zml": DumpZML(),
}


