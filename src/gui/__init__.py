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

import gtk, os


class GUIError(Exception):
    pass

def load_image(filename, size=None):
    for directory in context.share_dirs:
        filepath = os.path.join(directory, "images", filename)
        if os.path.isfile(filepath):
            if size is None:
                return gtk.gdk.pixbuf_new_from_file(filepath)
            else:
                return gtk.gdk.pixbuf_new_from_file_at_size(
                    filepath, size[0], size[1]
                )
    raise GUIError("Image '%s' not found." % filename)


gtk.window_set_default_icon(load_image("zeobuilder.svg"))
