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
from zeobuilder.gui.glade_wrapper import GladeWrapper
from zeobuilder.gui import load_image

import gtk.gdk


class BaseDialog(GladeWrapper):
    def __init__(self, dialog_name):
        GladeWrapper.__init__(self, "plugins/core/gui.glade", dialog_name, "dialog")
        self.dialog.hide()

    def run(self):
        self.dialog.set_transient_for(context.parent_window)
        self.response_loop()
        self.dialog.hide()

    def response_loop(self):
        return self.dialog.run()


class AboutDialog(BaseDialog):
    def __init__(self):
        BaseDialog.__init__(self, "di_about")
        BaseDialog.init_proxies(self, ["im_logo"])
        self.im_logo.set_from_pixbuf(load_image("zeobuilder.svg", (72, 72)))

    def response_loop(self):
        response = BaseDialog.response_loop(self)
        while (response != gtk.RESPONSE_OK) or (response == gtk.RESPONSE_NONE) or (response == gtk.RESPONSE_DELETE_EVENT):
            if response == 1:
                warranty.run()
            elif response == 2:
                license.run()
            elif response == 3:
                credits.run()
            response = self.dialog.run()


about = AboutDialog()
warranty = BaseDialog("di_warranty")
license = BaseDialog("di_license")
credits = BaseDialog("di_credits")


class About(Immediate):
    description = "Show the about box"
    menu_info = MenuInfo("help/_Help:default", "_About", image_name=gtk.STOCK_ABOUT, order=(1, 0, 0, 0))

    def do(self):
        about.run()


actions = {
    "About": About
}
