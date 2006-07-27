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

import gtk

__all__ = ["Single", "Multiple"]


class Single(object):
    high_widget = False

    def __init__(self, label_text=None, border_width=6):
        self.label_text = label_text
        self.data_widget = None
        self.label = None
        self.container = None
        self.instance = None
        self.instances = None
        self.parent = None
        self.border_width = border_width

    def get_active(self):
        return self.instance is not None or self.instances is not None

    def init_widgets(self, instance):
        if self.applicable(instance):
            self.instance = instance
            self.create_widgets()
        else:
            self.instance = None

    def init_widgets_multiplex(self, instances):
        for instance in instances:
            if not self.applicable(instance):
                self.instances = None
                #print "NOT APPLICABLE", self, self.label_text
                return
        #print "IS  APPLICABLE", self, self.label_text
        self.instances = instances
        self.create_widgets()

    def get_widgets_flat_container(self, show_popup=True):
        label, data_widget, bu_popup = self.get_widgets_separate()
        if not show_popup:
            bu_popup = None
        if label is None and bu_popup is None:
            container = data_widget
        else:
            container = gtk.HBox()
            container.set_spacing(6)
            if label is not None:
                container.pack_start(label)
            container.pack_start(data_widget)
            if bu_popup is not None:
                container.pack_start(bu_popup)
        self.container = container
        self.container.set_border_width(self.border_width)
        return container

    def get_widgets_short_container(self, show_popup=True):
        label, data_widget, bu_popup = self.get_widgets_separate()
        if not show_popup:
            bu_popup = None
        if label is None and bu_popup is None:
            container = data_widget
        else:
            container = gtk.VBox()
            container.set_spacing(6)
            if label is not None and bu_popup is not None:
                hbox = gtk.HBox()
                hbox.set_spacing(6)
                hbox.pack_start(label)
                hbox.pack_start(bu_popup, expand=False)
                container.pack_start(hbox)
            elif label is not None:
                container.pack_start(label)
            elif bu_popup is not None:
                container.pack_start(bu_popup, expand=False)
            hbox = gtk.HBox()
            l = gtk.Label()
            l.set_size_request(10, 1)
            hbox.pack_start(l, expand=False)
            hbox.pack_start(data_widget)
            container.pack_start(hbox)
        self.container = container
        self.container.set_border_width(self.border_width)
        return container

    def applicable(self, instance):
        raise NotImplementedError

    def create_widgets(self):
        if self.label_text is not None:
            self.label = gtk.Label(self.label_text)
            self.label.set_alignment(0.0, 0.5)
            self.label.set_use_markup(True)

    def destroy_widgets(self):
        if self.container is not None:
            self.container.destroy()
        else:
            if self.label is not None:
                self.label.destroy()
            if self.data_widget is not None:
                self.data_widget.destroy()
        self.data_widget = None
        self.label = None
        self.container = None
        self.instance = None
        self.instances = None

    def show(self, field=None):
        # makes sure the correct notebook page is shown
        # etc. to point at the incorrect field.
        if self.parent is not None:
            self.parent.show(self)


class Multiple(Single):
    def __init__(self, fields, label_text=None, border_width=6):
        Single.__init__(self, label_text, border_width)
        self.fields = fields
        for field in self.fields:
            field.parent = self

    def destroy_widgets(self):
        for field in self.fields:
            field.destroy_widgets()
        Single.destroy_widgets(self)

    def read(self, instance=None):
        if self.instance is not None:
            for field in self.fields:
                field.read()

    def read_multiplex(self):
        if self.instances is not None:
            for field in self.fields:
                field.read_multiplex()

    def write(self, instance=None):
        if self.instance is not None:
            for field in self.fields:
               field.write()

    def write_multiplex(self):
        if self.instances is not None:
            for field in self.fields:
                field.write_multiplex()

    def check(self):
        if self.get_active():
            for field in self.fields:
                field.check()

