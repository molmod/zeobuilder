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
from zeobuilder.actions.composed import Immediate
from zeobuilder.actions.abstract import CenterAlignBase
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.nodes.parent_mixin import ContainerMixin
from zeobuilder.nodes.glcontainermixin import GLContainerMixin
from zeobuilder.gui.simple import ok_information
from zeobuilder.transformations import Translation, Complete
import zeobuilder.actions.primitive as primitive

from molmod.data import periodic

import numpy


class ChemicalFormula(Immediate):
    description = "Show chemical formula"
    menu_info = MenuInfo("default/_Object:tools/_Molecular:molecular", "_Chemical Formula", order=(0, 4, 1, 5, 2, 0))

    def analyze_selection():
        if not Immediate.analyze_selection(): return False
        if len(context.application.cache.nodes) == 0: return False
        return True
    analyze_selection = staticmethod(analyze_selection)

    def do(self):
        atom_counts = {}
        Atom = context.application.plugins.get_node("Atom")

        def recursive_chem_counter(node):
            if isinstance(node, Atom):
                if node.number not in atom_counts:
                    atom_counts[node.number] = 1
                else:
                    atom_counts[node.number] += 1
            if isinstance(node, ContainerMixin):
                for child in node.children:
                    recursive_chem_counter(child)

        for node in context.application.cache.nodes:
            recursive_chem_counter(node)

        total = 0
        if len(atom_counts) > 0:
            answer = "Chemical formula: "
            for atom_number, count in atom_counts.iteritems():
                answer += "%s<sub>%i</sub>" % (periodic[atom_number].symbol, count)
                total += count
            answer += "\n\nNumber of atoms: %i" % total
        else:
            answer = "No atoms found."
        ok_information(answer)


def yield_particles(node, parent=None):
    if parent is None:
        parent = node
    Atom = context.application.plugins.get_node("Atom")
    for child in node.children:
        if isinstance(child, Atom):
            yield (
                periodic[child.number].mass,
                child.get_frame_relative_to(parent).translation_vector
            )
        elif isinstance(child, GLContainerMixin):
            for particle in yield_particles(child, parent):
                yield particle

def calculate_center_of_mass(particles):
    weighted_center = numpy.zeros(3, float)
    total_mass = 0.0
    for mass, coordinate in particles:
        weighted_center += mass*coordinate
        total_mass += mass
    if total_mass == 0.0:
        return total_mass, weighted_center
    else:
        return total_mass, weighted_center/total_mass

def calculate_inertia_tensor(particles, center):
    tensor = numpy.zeros((3,3), float)
    for mass, coordinate in particles:
        delta = coordinate - center
        tensor += (
            mass*numpy.dot(delta, delta)*numpy.identity(3, float)
           -numpy.outerproduct(delta, delta)
        )
    return tensor

def default_rotation_matrix(inertia_tensor):
    if abs(inertia_tensor.ravel()).max() < 1e-6:
        return numpy.identity(3, float)
    evals, evecs = numpy.linalg.eig(inertia_tensor)
    result = numpy.array([evecs[:,index] for index in evals.argsort()], float).transpose()
    if numpy.linalg.det(result) < 0: result *= -1
    return result


class CenterOfMass(CenterAlignBase):
    description = "Center of mass"
    menu_info = MenuInfo("default/_Object:tools/_Transform:center", "Center of _mass frame", order=(0, 4, 1, 2, 2, 2))

    def analyze_selection():
        # A) calling ancestor
        if not CenterAlignBase.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        if not isinstance(cache.node, ContainerMixin): return False
        if len(cache.translated_children) == 0: return False
        if cache.some_children_fixed: return False
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)

    def do(self):
        cache = context.application.cache
        node = cache.node
        t = Translation()
        mass, com = calculate_center_of_mass(yield_particles(node))
        if mass == 0.0:
            raise UserError("No particles (atoms) found.")
        t.translation_vector = com
        CenterAlignBase.do(self, node, cache.translated_children, t)


class CenterOfMassAndPrincipalAxes(CenterOfMass):
    description = "Center of mass and principal axes"
    menu_info = MenuInfo("default/_Object:tools/_Transform:centeralign", "Center of mass and _principal axes frame", order=(0, 4, 1, 2, 4, 1))

    def analyze_selection():
        # A) calling ancestor
        if not CenterOfMass.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        if not isinstance(cache.node, ContainerMixin): return False
        if len(cache.transformed_children) == 0: return False
        if cache.some_children_fixed: return False
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)

    def do(self):
        cache = context.application.cache
        node = cache.node
        c = Complete()

        mass, com = calculate_center_of_mass(yield_particles(node))
        if mass == 0.0:
            raise UserError("No particles (atoms) found.")
        c.translation_vector = com

        tensor = calculate_inertia_tensor(yield_particles(node), com)
        c.rotation_matrix = default_rotation_matrix(tensor)
        CenterAlignBase.do(self, node, cache.translated_children, c)


actions = {
    "ChemicalFormula": ChemicalFormula,
    "CenterOfMass": CenterOfMass,
    "CenterOfMassAndPrincipalAxes": CenterOfMassAndPrincipalAxes,
}
