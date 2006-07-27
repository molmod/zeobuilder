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
# ----------
# This proram contains dialogboxes used in zeobuilder


from zeobuilder import context

import gobject, gtk

__all__ = ["ok_error", "yes_no_question", "nosave_cancel_save_question",
           "ok_information"]

def run_dialog(dialog):
    dialog.set_title(context.title)
    result = dialog.run()
    dialog.destroy()
    return result

def ok_error(message):
    dialog = gtk.MessageDialog(context.parent_window, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, message)
    result = run_dialog(dialog)
    dialog.destroy()
    return result

def ok_information(message):
    dialog = gtk.MessageDialog(context.parent_window, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, message)
    result = run_dialog(dialog)
    dialog.destroy()
    return result

def yes_no_question(message):
    dialog = gtk.MessageDialog(context.parent_window, 0, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, message)
    result = run_dialog(dialog)
    dialog.destroy()
    return result

def nosave_cancel_save_question(message):
    dialog = gtk.MessageDialog(context.parent_window, 0, gtk.MESSAGE_QUESTION, gtk.BUTTONS_NONE, message)
    dialog.add_button(gtk.STOCK_NO, gtk.RESPONSE_NO)
    dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
    dialog.add_button(gtk.STOCK_SAVE, gtk.RESPONSE_OK)
    result = run_dialog(dialog)
    dialog.destroy()
    return result

def ask_name():
    dialog = gtk.Dialog(
        context.title,
        context.parent_window,
        flags=0,
        buttons=(
            gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
            gtk.STOCK_OK, gtk.RESPONSE_OK
       )
    )
    hbox = gtk.HBox()
    hbox.pack_start(gtk.Label("Name:"))
    entry = gtk.Entry()
    entry.set_activates_default(True)
    hbox.pack_start(entry)
    hbox.set_spacing(6)
    hbox.set_border_width(6)
    dialog.vbox.pack_start(hbox)
    dialog.action_area.get_children()[0].set_property("has-default", True)
    dialog.show_all()
    if dialog.run() == gtk.RESPONSE_OK:
        result = entry.get_text()
    else:
        result = None
    dialog.destroy()
    return result
