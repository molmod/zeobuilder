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


import numpy


def common_parent(parents):
    if None in parents: return None
    if len(parents) == 1: return parents[0]
    parent_traces = [parent.trace() for parent in parents]
    common_position = min([len(x) for x in parent_traces])-1
    former_trace = parent_traces[0]
    for trace in parent_traces[1:]:
        while trace[common_position] != former_trace[common_position]:
            common_position -= 1
        if common_position == 0: return None
        former_trace = trace
    return former_trace[common_position]

def bridge(reference, target):
    # bridge = [reference_parent, reference_upper_parent, ..., common_parent[ +
    #          ]common_parent, ... target_upper_parent, target_parent, target]
    # this means that the common parent and the reference are not included!
    reference_trace = reference.trace()
    target_trace = target.trace()
    split_position = min(len(target_trace), len(reference_trace)) - 1
    while (split_position > 0) and (target_trace[split_position] != reference_trace[split_position]):
        split_position -= 1
    split_position += 1
    assert split_position != 1, "Bridge can only made to a target with the same root object."
    reference_trace.reverse()
    return reference_trace[1: -split_position] + target_trace[split_position:]

def some_fixed(nodes):
    for node in nodes:
        if node.get_fixed(): return True
    return False

def list_classes(nodes):
    result = []
    for node in nodes:
        if node.__class__ not in result:
            result.append(node.__class__)
    return result

def list_children(parents):
    result = []
    for parent in parents:
        result.extend(parent.children)
    return result

def list_parents(nodes):
    result = []
    for node in nodes:
        if node.parent not in result:
            result.append(node.parent)
    return result

def list_without_indirect_children(nodes_by_parent, traces_by_parent):
    for parent, trace in traces_by_parent.iteritems():
        for other_parent in nodes_by_parent.keys():
            if other_parent != parent and (other_parent in trace):
                del nodes_by_parent[parent]
                break
    result = []
    for nodes in nodes_by_parent.itervalues():
        result.extend(nodes)
    return result

def list_by_parent(nodes):
    result = {}
    for node in nodes:
        if node.parent in result:
            result[node.parent].append(node)
        else:
            result[node.parent] = [node]
    return result

def list_traces_by(nodes):
    return dict([(node, node.trace()) for node in nodes if node is not None])

def calculate_center(translations):
    center = numpy.zeros(3, float)
    counter = 0
    for t in translations:
        center += t.translation_vector
        counter += 1
    if counter > 0:
        center /= counter
    return center
