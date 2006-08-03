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
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.nodes.parent_mixin import ContainerMixin
from zeobuilder.gui.simple import ok_information
import zeobuilder.actions.primitive as primitive

from molmod.data import periodic


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


actions = {
    "ChemicalFormula": ChemicalFormula
}
