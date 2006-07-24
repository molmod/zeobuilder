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


import os, sys

class Context(object):
    def __init__(self):
        self.title = "Zeobuilder"
        self.version = "0.1.0"
        self.user_dir = os.path.expanduser("~/.zeobuilder")
        if not os.path.isdir(self.user_dir):
            os.mkdir(self.user_dir)
        self.share_dirs = [
            os.path.join(sys.prefix, "share/zeobuilder", self.version),
            self.user_dir
        ]
        self.config_filename = os.path.join(self.user_dir, "settings")


context = Context()
