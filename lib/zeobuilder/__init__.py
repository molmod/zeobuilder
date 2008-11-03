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


import os, sys

class Context(object):
    def __init__(self):
        self.title = "Zeobuilder"
        self.user_dir = os.path.expanduser("~/.zeobuilder")
        if not os.path.isdir(self.user_dir):
            os.mkdir(self.user_dir)
        candidate_share_dirs = [
            os.path.join(sys.prefix, "share/zeobuilder"),
            self.user_dir,
            "/usr/share/zeobuilder/",
            "/usr/local/share/zeobuilder/",
        ]
        self.share_dirs = []
        for share_dir in candidate_share_dirs:
            if os.path.isdir(share_dir):
                self.share_dirs.append(share_dir)
        self.config_filename = os.path.join(self.user_dir, "settings")

    def get_share_file(self, filename):
        for dir in self.share_dirs:
            result = os.path.join(dir, filename)
            if os.path.isfile(result):
                return result
        raise ValueError("No file '%s' found in the share directories." % filename)


context = Context()




