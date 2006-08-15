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


__all__ = [
    "ok_error", "yes_no_question", "nosave_cancel_save_question",
    "ok_information", "ask_name", "field_error"
]


template="<big><b>%s</b></big>\n\n%s"

def run_dialog(dialog, line_wrap=True):
    dialog.set_title(context.title)
    dialog.label.set_property("use-markup", True)
    dialog.label.set_line_wrap(line_wrap)
    result = dialog.run()
    dialog.destroy()
    return result


def ok_error(message, details="", line_wrap=True):
    full = (template % (message, details)).strip()
    dialog = gtk.MessageDialog(context.parent_window, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, full)
    return run_dialog(dialog)


def ok_information(message, details="", line_wrap=True):
    full = (template % (message, details)).strip()
    dialog = gtk.MessageDialog(context.parent_window, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, message)
    return run_dialog(dialog)


def yes_no_question(message, details="", line_wrap=True):
    full = (template % (message, details)).strip()
    dialog = gtk.MessageDialog(context.parent_window, 0, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, message)
    return run_dialog(dialog)


def nosave_cancel_save_question(message, details="", line_wrap=True):
    full = (template % (message, details)).strip()
    dialog = gtk.MessageDialog(context.parent_window, 0, gtk.MESSAGE_QUESTION, gtk.BUTTONS_NONE, message)
    dialog.add_button(gtk.STOCK_NO, gtk.RESPONSE_NO)
    dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
    dialog.add_button(gtk.STOCK_SAVE, gtk.RESPONSE_OK)
    return run_dialog(dialog)


def ask_name(initial_name=None):
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
    if initial_name is not None:
        entry.set_text(initial_name)
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


field_template=template % (
    "Some of the fields you entered are invalid.",
    "Only the first problem is reported here. Correct it and try again.\n\n<b>Location:</b> %s\n<b>Problem:</b> %s"
)


def field_error(location, problem, line_wrap=True):
    full = field_template % (location, problem)
    dialog = gtk.MessageDialog(context.parent_window, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_NONE, full)
    button = dialog.add_button(gtk.STOCK_JUMP_TO, gtk.RESPONSE_OK)
    return run_dialog(dialog, line_wrap=True)

