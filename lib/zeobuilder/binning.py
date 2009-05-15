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


from molmod.transformations import Translation
from molmod.binning import PositionedObject
from zeobuilder.nodes.parent_mixin import ContainerMixin
from zeobuilder.nodes.glmixin import GLTransformationMixin


class YieldPositionedChildren(object):
    def __init__(self, nodes, parent, recursive=False, node_filter=None, container_filter=None):
        self.nodes = nodes
        self.parent = parent
        self.recursive = recursive
        if node_filter == None:
            self.node_filter = lambda node: True
        else:
            self.node_filter = node_filter
        if container_filter == None:
            self.container_filter = lambda container: True
        else:
            self.container_filter = container_filter

    def __call__(self, node=None):
        if node == None:
            for node in self.nodes:
                #print "IN", node
                for positioned_object in self.__call__(node):
                    yield positioned_object
            return
        if isinstance(node, GLTransformationMixin) and \
           isinstance(node.transformation, Translation) and \
           self.node_filter(node):
            #print "PO", node, node.parent#, node.get_frame_up_to(self.parent).t
            yield PositionedObject(node, node.get_frame_up_to(self.parent).t)
        elif self.recursive and isinstance(node, ContainerMixin) and self.container_filter(node):
            for child in node.children:
                #print "RECUR", node, child
                for positioned_object in self.__call__(child):
                    yield positioned_object


