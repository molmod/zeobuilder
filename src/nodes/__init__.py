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

import gtk


def init_nodes(nodes):
    from reference import Reference, SpatialReference
    from zeobuilder.gui.edit_properties import EditProperties
    from zeobuilder.gui.fields_dialogs import create_tabbed_main_field

    dialog_fields = []

    for node in nodes.itervalues():
        node.reference_icon = node.icon.copy()
        Reference.overlay_icon.composite(
            node.reference_icon, 0, 0, 20, 20, 0, 0, 1.0, 1.0,
            gtk.gdk.INTERP_BILINEAR, 255
        )
        dialog_fields.extend(node.dialog_fields)

    main_field = create_tabbed_main_field(dialog_fields)
    context.application.edit_properties = EditProperties(main_field)
