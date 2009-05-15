# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 - 2009 Toon Verstraelen <Toon.Verstraelen@UGent.be>, Center
# for Molecular Modeling (CMM), Ghent University, Ghent, Belgium; all rights
# reserved unless otherwise stated.
#
# This file is part of Zeobuilder.
#
# Zeobuilder is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# In addition to the regulations of the GNU General Public License,
# publications and communications based in parts on this program or on
# parts of this program are required to cite the following article:
#
# "ZEOBUILDER: a GUI toolkit for the construction of complex molecules on the
# nanoscale with building blocks", Toon Verstraelen, Veronique Van Speybroeck
# and Michel Waroquier, Journal of Chemical Information and Modeling, Vol. 48
# (7), 1530-1541, 2008
# DOI:10.1021/ci8000748
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
from zeobuilder.actions.composed import Immediate
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.gui.glade_wrapper import GladeWrapper
from zeobuilder.gui import load_image
import zeobuilder.authors as authors

import gtk.gdk


class BaseDialog(GladeWrapper):
    def __init__(self, dialog_name):
        GladeWrapper.__init__(self, "plugins/basic/gui.glade", dialog_name, "dialog")
        self.dialog.hide()

    def run(self):
        self.dialog.set_transient_for(context.parent_window)
        self.response_loop()
        self.dialog.hide()

    def response_loop(self):
        return self.dialog.run()


class CreditsDialog(BaseDialog):
    def __init__(self):
        BaseDialog.__init__(self, "di_credits")
        self.init_proxies(["tv_authors", "bu_information"])
        author_store = authors.init_widgets(self.tv_authors, self.bu_information)
        authors.fill_store(author_store)


class AboutDialog(BaseDialog):
    def __init__(self):
        BaseDialog.__init__(self, "di_about")
        BaseDialog.init_proxies(self, ["im_logo"])
        self.im_logo.set_from_pixbuf(load_image("zeobuilder.svg", (72, 72)))

    def response_loop(self):
        response = BaseDialog.response_loop(self)
        while (response != gtk.RESPONSE_CLOSE) or (response == gtk.RESPONSE_NONE) or (response == gtk.RESPONSE_DELETE_EVENT):
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
credits = CreditsDialog()


class About(Immediate):
    description = "Show the about box"
    menu_info = MenuInfo("help/_Help:default", "_About", image_name=gtk.STOCK_ABOUT, order=(1, 0, 0, 0))
    authors = [authors.toon_verstraelen]

    def do(self):
        about.run()


actions = {
    "About": About
}


