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


from zeobuilder.nodes.meta import PublishedProperties, Property, ModelObjectInfo
from zeobuilder.nodes.model_object import ModelObject
from zeobuilder.actions.abstract import AddBase
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.gui.fields_dialogs import DialogFieldInfo
import zeobuilder.gui.fields as fields

import StringIO


class Notes(ModelObject):
    info = ModelObjectInfo("plugins/core/notes.svg")

    #
    # Properties
    #

    def set_notes(self, notes):
        self.notes = notes

    published_properties = PublishedProperties({
        "notes": Property(StringIO.StringIO(), lambda self: self.notes, set_notes)
    })

    #
    # Dialog fields (see action EditProperties)
    #

    dialog_fields = set([
        DialogFieldInfo("Basic", (0, 1), fields.edit.TextView(
            label_text="Notes",
            attribute_name="notes",
            line_breaks=True,
        ))
    ])


class AddNotes(AddBase):
    description = "Add notes"
    menu_info = MenuInfo("default/_Object:tools/_Add:non3d", "_Notes", image_name="plugins/core/notes.svg", order=(0, 4, 1, 0, 1, 1))

    def analyze_selection():
        return AddBase.analyze_selection(Notes)
    analyze_selection = staticmethod(analyze_selection)

    def do(self):
        AddBase.do(self, Notes)


nodes = {
    "Notes": Notes
}

actions = {
    "AddNotes": AddNotes,
}
