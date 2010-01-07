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
# ----------
# This proram contains dialogboxes used in zeobuilder


from zeobuilder import context

import gobject, gtk

import os


__all__ = [
    "ok_error", "yes_no_question", "nosave_cancel_save_question",
    "ok_information", "ask_name", "field_error"
]


template="<big><b>%s</b></big>\n\n%s"


def escape_pango(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def apply_template(template, items, escape):
    if escape:
        return (template % tuple(escape_pango(item) for item in items)).strip()
    else:
        return (template % items).strip()

def run_dialog(dialog, line_wrap=True):
    dialog.set_title(context.title)
    dialog.label.set_property("use-markup", True)
    dialog.label.set_line_wrap(line_wrap)
    result = dialog.run()
    dialog.destroy()
    return result


def ok_error(message, details="", line_wrap=True, markup=False):
    full = apply_template(template, (message, details), not markup)
    dialog = gtk.MessageDialog(context.parent_window, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, full)
    return run_dialog(dialog, line_wrap)


def ok_information(message, details="", line_wrap=True, markup=False):
    full = apply_template(template, (message, details), not markup)
    dialog = gtk.MessageDialog(context.parent_window, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, full)
    return run_dialog(dialog, line_wrap)


def yes_no_question(message, details="", line_wrap=True, markup=False):
    full = apply_template(template, (message, details), not markup)
    dialog = gtk.MessageDialog(context.parent_window, 0, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, full)
    return run_dialog(dialog, line_wrap)


def nosave_cancel_save_question(message, details="", line_wrap=True, markup=False):
    full = apply_template(template, (message, details), not markup)
    dialog = gtk.MessageDialog(context.parent_window, 0, gtk.MESSAGE_QUESTION, gtk.BUTTONS_NONE, full)
    dialog.add_button(gtk.STOCK_NO, gtk.RESPONSE_NO)
    dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
    dialog.add_button(gtk.STOCK_SAVE, gtk.RESPONSE_OK)
    return run_dialog(dialog, line_wrap)


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


def field_error(location, problem, line_wrap=True, markup=False):
    full = apply_template(field_template, (location, problem), not markup)
    dialog = gtk.MessageDialog(context.parent_window, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_NONE, full)
    button = dialog.add_button(gtk.STOCK_JUMP_TO, gtk.RESPONSE_OK)
    return run_dialog(dialog, line_wrap)


def ask_save_filename(title, filename):
    filename = os.path.join(
        context.application.main.get_current_directory(),
        filename
    )
    file_save_dialog = gtk.FileChooserDialog(
        title,
        context.parent_window,
        gtk.FILE_CHOOSER_ACTION_SAVE,
        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK)
    )
    file_save_dialog.set_default_response(gtk.RESPONSE_OK)
    file_save_dialog.set_filename(filename)
    file_save_dialog.set_current_name(os.path.basename(filename))
    response = file_save_dialog.run()
    file_save_dialog.hide()
    if response == gtk.RESPONSE_OK:
        return file_save_dialog.get_filename()
    else:
        return None


