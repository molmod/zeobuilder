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
from zeobuilder.nodes.elementary import GLFrameBase
from zeobuilder.nodes.model_object import ModelObjectInfo
from zeobuilder.nodes.helpers import FrameAxes

from molmod.transformations import Complete


class Frame(GLFrameBase, FrameAxes):
    info = ModelObjectInfo("plugins/core/frame.svg")

    def initnonstate(self):
        GLFrameBase.initnonstate(self, Complete)

    #
    # Tree
    #

    @classmethod
    def check_add(Class, ModelObjectClass):
        if not GLFrameBase.check_add(ModelObjectClass): return False
        Universe = context.application.plugins.get_node("Universe")
        if issubclass(ModelObjectClass, Universe): return False
        return True

    #
    # Draw
    #

    def draw(self):
        GLFrameBase.draw(self)
        FrameAxes.draw(self, self.selected)

    def write_pov(self, indenter):
        indenter.write_line("union {", 1)
        FrameAxes.write_pov(self, indenter)
        GLFrameBase.write_pov(self, indenter)
        indenter.write_line("}", -1)

    #
    # Revalidation
    #

    def revalidate_bounding_box(self):
        GLFrameBase.revalidate_bounding_box(self)
        FrameAxes.extend_bounding_box(self, self.bounding_box)

    #
    # Signal handlers
    #

    def on_select_changed(self, foo):
        GLFrameBase.on_select_changed(self, foo)
        self.invalidate_draw_list()


class AddFrame(AddBase):
    description = "Add frame"
    menu_info = MenuInfo("default/_Object:tools/_Add:3d", "_Frame", image_name="plugins/core/frame.svg", order=(0, 4, 1, 0, 0, 3))

    @staticmethod
    def analyze_selection():
        return AddBase.analyze_selection(Frame)

    def do(self):
        AddBase.do(self, Frame)



nodes = {
    "Frame": Frame
}

actions = {
    "AddFrame": AddFrame,
}
