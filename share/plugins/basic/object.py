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
from zeobuilder.nodes.reference import Reference
from zeobuilder.actions.composed import Immediate
from zeobuilder.actions.collections.menu import MenuInfo
import zeobuilder.actions.primitive as primitive
import zeobuilder.authors as authors

import gtk

import copy


class EditProperties(Immediate):
    description = "Edit Properties"
    menu_info = MenuInfo("default/_Object:basic", "_Properties", ord("e"), image_name=gtk.STOCK_PROPERTIES, order=(0, 4, 0, 1))
    repeatable = False
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        if len(cache.nodes) == 0: return False
        for cls in cache.classes:
            if issubclass(cls, Reference): return False
        # C) passed all tests:
        return True

    def do(self):
        victims = context.application.cache.nodes
        # Define the old copy of the state
        old_states = dict((victim, copy.deepcopy(victim.__getstate__())) for victim in victims)
        # Let the user make changes
        edit_properties = context.application.edit_properties
        edit_properties.run(victims)
        for changed_name in edit_properties.changed_names:
            for victim, old_state in old_states.iteritems():
                old_value = old_state.get(changed_name)
                if old_value is None: old_value = victim.properties_by_name[changed_name].default(victim)
                primitive.SetProperty(victim, changed_name, old_value, done=True)


actions = {
    "EditProperties": EditProperties,
}




