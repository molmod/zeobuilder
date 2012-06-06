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
# --


from zeobuilder import context
from zeobuilder.actions.abstract import AddBase
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.nodes.elementary import GLFrameBase
from zeobuilder.nodes.model_object import ModelObjectInfo
from zeobuilder.nodes.helpers import FrameAxes
import zeobuilder.authors as authors

from molmod import Complete


class Frame(GLFrameBase, FrameAxes):
    info = ModelObjectInfo("plugins/basic/frame.svg")
    authors = [authors.toon_verstraelen]

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
        FrameAxes.draw(self, self.selected)
        GLFrameBase.draw(self)

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
    menu_info = MenuInfo("default/_Object:tools/_Add:3d", "_Frame", image_name="plugins/basic/frame.svg", order=(0, 4, 1, 0, 0, 3))
    authors = [authors.toon_verstraelen]

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


