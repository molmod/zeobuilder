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
    import zeobuilder.gui.fields as fields

    dialog_fields = {}
    categories = set()

    for node in nodes.itervalues():
        if not issubclass(node, Reference):
            node.reference_icon = node.icon.copy()
            Reference.overlay_icon.composite(
                node.reference_icon, 0, 0, 20, 20, 0, 0, 1.0, 1.0,
                gtk.gdk.INTERP_BILINEAR, 255
            )
        for dialog_field_info in node.dialog_fields:
            key = (dialog_field_info.category, dialog_field_info.order, dialog_field_info.field.attribute_name)
            if key not in dialog_fields:
                dialog_fields[key] = dialog_field_info
            categories.add(dialog_field_info.category)

    fields_by_category = dict((category, []) for category in categories)
    for dialog_field_info in dialog_fields.itervalues():
        fields_by_category[dialog_field_info.category].append(dialog_field_info)
    fields_by_category = fields_by_category.items()

    fields_by_category.sort(key=(lambda cf: min(dfi.order for dfi in cf[1])))
    for category, field_infos in fields_by_category:
        field_infos.sort(key=(lambda dfi: dfi.order))

    #for category, field_infos in fields_by_category:
    #    print "C", category
    #    for dialog_field_info in field_infos:
    #        print "DFI", dialog_field_info.order, dialog_field_info.field.attribute_name, dialog_field_info.field.label_text

    main_field = fields.group.Notebook([
        (category, fields.group.Table([
            dialog_field_info.field
            for dialog_field_info
            in field_infos
        ])) for category, field_infos
        in fields_by_category
    ])
    context.application.edit_properties = EditProperties(main_field)
