# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 Toon Verstraelen <Toon.Verstraelen@UGent.be>
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


from fields_dialogs import FieldsDialogMultiplex
from molmod.data import BOND_SINGLE, BOND_DOUBLE, BOND_TRIPLE

import gtk

__all__ = ["EditProperties"]


class EditProperties(FieldsDialogMultiplex):
    def __init__(self, main_field):
        FieldsDialogMultiplex.__init__(
            self,
            "Edit properties",
            main_field,
            [
                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL),
                (gtk.STOCK_APPLY, gtk.RESPONSE_APPLY),
                (gtk.STOCK_OK, gtk.RESPONSE_OK)
            ]
        )

    def run(self, nodes):
        self.nodes = nodes
        self.changed_names = set([])
        return FieldsDialogMultiplex.run(self, nodes)

    def write(self):
        FieldsDialogMultiplex.write(self)
        for name in self.main_field.changed_names():
            self.changed_names.add(name)
            # this is necessary when the user clicks the apply button:
            for node in self.nodes:
                p = node.properties_by_name.get(name)
                if p is not None:
                    p.set(node, p.get(node))

