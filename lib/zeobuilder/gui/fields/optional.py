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



from base import Single
from mixin import ambiguous, EditMixin

import gtk


class Optional(Single):
    def __init__(self, slave):
        Single.__init__(self)
        self.slave = slave
        slave.parent = self
        self.toggle_button = None

    def init_widgets(self, instance):
        self.slave.init_widgets(instance)
        Single.init_widgets(self, instance)

    def init_widgets_multiplex(self, instances):
        self.slave.init_widgets_multiplex(instances)
        Single.init_widgets_multiplex(self, instances)

    def get_active(self):
        return self.slave.get_active()

    def applicable(self, instance):
        return self.slave.get_active()

    def changed_names(self):
        if not self.get_active():
            return []
        else:
            return self.slave.changed_names()

    def create_widgets(self):
        Single.create_widgets(self)
        self.data_widget = self.toggle_button
        self.high_widget = self.slave.high_widget
        self.toggle_button.connect("toggled", self.toggle_button_toggled)
        if isinstance(self.slave, EditMixin):
            self.toggle_button.connect("toggled", self.slave.on_widget_changed)
        if self.slave.label_text is not None:
            label, data_widget, bu_popup = self.slave.get_widgets_separate()
            if label is not None:
                self.toggle_button.add(label)

    def destroy_widgets(self):
        self.slave.destroy_widgets()
        Single.destroy_widgets(self)

    def get_widgets_separate(self):
        label, data_widget, bu_popup = self.slave.get_widgets_separate()
        return self.toggle_button, data_widget, bu_popup

    def read(self):
        if self.get_active():
            self.slave.read()
            self.toggle_button.set_active(self.slave.get_sensitive())

    def read_multiplex(self):
        if self.get_active():
            self.slave.read_multiplex()
            self.toggle_button.set_active(self.slave.get_sensitive())

    def write(self):
        if self.get_active():
            self.slave.write()

    def write_multiplex(self):
        if self.get_active():
            self.slave.write_multiplex()

    def check(self):
        if self.get_active():
            self.slave.check()

    def grab_focus(self):
        self.slave.grab_focus()

    def toggle_button_toggled(self, toggle_button):
        self.slave.set_sensitive(toggle_button.get_active())


class CheckOptional(Optional):
    def create_widgets(self):
        self.toggle_button = gtk.CheckButton()
        Optional.create_widgets(self)


class RadioOptional(Optional):
    def create_widgets(self):
        first = None
        for field in self.parent.fields:
            if isinstance(field, RadioOptional):
                first = field.toggle_button
                break
        self.toggle_button = gtk.RadioButton(first)
        Optional.create_widgets(self)





