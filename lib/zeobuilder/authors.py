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


from zeobuilder.gui.glade_wrapper import GladeWrapper

import gtk


class Author(object):
    def __init__(self, name, role, affiliation):
        self.name = name
        self.role = role
        self.affiliation = affiliation


toon_verstraelen = Author(
"Toon Verstraelen",
"Lead Developer",
"""Center for Molecular Modeling
Ghent University
Proeftuinstraat 86
9000 Gent, Belgium
Tel: +32 (0)9 264 65 56
<span foreground="#0000FF" underline="single">Toon.Verstraelen@UGent.be</span>""")


wouter_smet = Author(
"Wouter Smet",
"Contributor",
"""Center for Molecular Modeling
Ghent University
Proeftuinstraat 86
9000 Gent, Belgium""")


bartek_szyja = Author(
"Bartek Szyja",
"Contributor",
"""Eindhoven University of Technology
Chemical Engineering and Chemistry
Molecular Heterogeneous Catalysis
PO Box 513, STW 4.22
5600 MB Eindhoven, The Netherlands
Tel: +31 40 247 2124
Fax: +31 40 245 5054
<span foreground="#0000FF" underline="single">B.M.Szyja@tue.nl</span>""")


all = [
    toon_verstraelen,
    bartek_szyja,
]


class AuthorDialog(GladeWrapper):
    def __init__(self):
        GladeWrapper.__init__(self, "zeobuilder.glade", "di_author", "dialog")
        self.init_proxies(["la_author", "la_affiliation"])
        self.dialog.hide()

    def run(self, author):
        self.la_author.set_markup("<b>%s</b>\n%s" % (author.name, author.role))
        self.la_affiliation.set_markup(author.affiliation)
        self.dialog.run()
        self.dialog.hide()

author_dialog = AuthorDialog()


def init_widgets(list_view, button):
    store = gtk.ListStore(str, str, object)
    list_view.set_model(store)

    column = gtk.TreeViewColumn("Author", gtk.CellRendererText(), text=0)
    list_view.append_column(column)
    column = gtk.TreeViewColumn("Role", gtk.CellRendererText(), text=1)
    list_view.append_column(column)

    def on_selection_changed(tree_selection):
        button.set_sensitive(tree_selection.count_selected_rows() == 1)

    list_view.get_selection().connect("changed", on_selection_changed)
    button.set_sensitive(False)

    def on_button_clicked(button):
        iter = list_view.get_selection().get_selected()[1]
        author = store.get_value(iter, 2)
        author_dialog.run(author)

    button.connect("clicked", on_button_clicked)

    return store


def fill_store(store, authors=all):
    store.clear()
    for author in authors:
        store.append((author.name, author.role, author))


