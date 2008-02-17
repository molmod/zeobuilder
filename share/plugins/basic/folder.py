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


from zeobuilder import context
from zeobuilder.actions.abstract import AddBase
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.nodes.meta import Property
from zeobuilder.nodes.elementary import ContainerBase
from zeobuilder.nodes.model_object import ModelObjectInfo
import zeobuilder.authors as authors


class Folder(ContainerBase):
    info = ModelObjectInfo("plugins/basic/folder.svg")
    authors = [authors.toon_verstraelen]


class AddFolder(AddBase):
    description = "Add folder"
    menu_info = MenuInfo("default/_Object:tools/_Add:non3d", "_Folder", image_name="plugins/basic/folder.svg", order=(0, 4, 1, 0, 1, 0))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        return AddBase.analyze_selection(Folder)

    def do(self):
        AddBase.do(self, Folder)


nodes = {
    "Folder": Folder
}

actions = {
    "AddFolder": AddFolder,
}




