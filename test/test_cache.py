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


from common import *

from zeobuilder import context
import zeobuilder.actions.primitive as primitive


def test_add_box():
    def fn():
        FileNew = context.application.plugins.get_action("FileNew")
        FileNew()
        universe = context.application.model.root[0]
        context.application.action_manager.record_primitives = False
        # add some test objects
        Box = context.application.plugins.get_node("Box")
        Frame = context.application.plugins.get_node("Frame")
        box1 = Box()
        primitive.Add(box1, universe)
        frame = Frame()
        primitive.Add(frame, universe)
        box2 = Box()
        primitive.Add(box2, frame)
        # test nodes_without_children
        context.application.main.select_nodes([box1, box2])
        assert context.application.cache.nodes_without_children == [box1, box2]
    run_application(fn)


