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
from zeobuilder.actions.abstract import AddBase
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.nodes.meta import Property
from zeobuilder.nodes.elementary import ContainerBase
from zeobuilder.nodes.model_object import ModelObjectInfo
import zeobuilder.authors as authors


class Folder(ContainerBase):
    info = ModelObjectInfo("plugins/core/folder.svg")
    authors = [authors.toon_verstraelen]


class AddFolder(AddBase):
    description = "Add folder"
    menu_info = MenuInfo("default/_Object:tools/_Add:non3d", "_Folder", image_name="plugins/core/folder.svg", order=(0, 4, 1, 0, 1, 0))
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
