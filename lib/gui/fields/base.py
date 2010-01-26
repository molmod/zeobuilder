# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 - 2010 Toon Verstraelen <Toon.Verstraelen@UGent.be>, Center
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

import gtk

__all__ = ["Single", "Multiple"]


class Single(object):
    high_widget = False

    def __init__(self, label_text=None):
        self.label_text = label_text
        self.data_widget = None
        self.label = None
        self.container = None
        self.instance = None
        self.instances = None
        self.parent = None

    def get_description(self, caller):
        if self.label_text is None:
            return None
        else:
            return self.label_text

    def get_trace(self, caller=None):
        description = self.get_description(caller)
        if self.parent is None:
            trace = None
        else:
            trace = self.parent.get_trace(self)

        if description is None and trace is None:
            return None
        elif description is None:
            return trace
        elif trace is None:
            return description
        else:
            return "%s  <b>-&gt;</b>  %s" % (self.parent.get_trace(self), description)

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
                container.pack_start(label, True, True)
            container.pack_start(data_widget, True, True)
            if bu_popup is not None:
                container.pack_start(bu_popup, False, False)
        self.container = container
        self.container.set_border_width(6)
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
            if label is not None:
                label.set_alignment(0.0, 1.0)
            if label is not None and bu_popup is not None:
                hbox = gtk.HBox()
                hbox.set_spacing(6)
                hbox.pack_start(label, True, True)
                hbox.pack_start(bu_popup, False, False)
                container.pack_start(hbox, False, False)
            elif label is not None:
                container.pack_start(label, False, False)
            elif bu_popup is not None:
                container.pack_start(bu_popup, False, False)
            hbox = gtk.HBox()
            l = gtk.Label()
            l.set_size_request(18, 1)
            hbox.pack_start(l, False, False)
            hbox.pack_start(data_widget, True, True)
            container.pack_start(hbox, False, False)
        self.container = container
        self.container.set_border_width(6)
        return container

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

    def show(self, caller=None):
        # makes sure the correct notebook page is shown
        # etc. to point at the incorrect field.
        if self.parent is not None:
            self.parent.show(self)

    def grab_focus(self):
        self.data_widget.grab_focus()

    def get_sensitive(self):
        return self.data_widget.get_property("sensitive")

    def set_sensitive(self, sensitive):
        if self.get_active():
            if self.label is not None:
                self.label.set_sensitive(sensitive)
            self.data_widget.set_sensitive(sensitive)



class Multiple(Single):
    def __init__(self, fields, label_text=None):
        Single.__init__(self, label_text)
        self.fields = fields
        for field in self.fields:
            field.parent = self

    def destroy_widgets(self):
        for field in self.fields:
            field.destroy_widgets()
        Single.destroy_widgets(self)

    def read(self):
        if self.get_active():
            for field in self.fields:
                field.read()

    def read_multiplex(self):
        if self.get_active():
            for field in self.fields:
                field.read_multiplex()

    def write(self):
        if self.get_active():
            for field in self.fields:
               field.write()

    def write_multiplex(self):
        if self.get_active():
            for field in self.fields:
                field.write_multiplex()

    def check(self):
        if self.get_active():
            for field in self.fields:
                field.check()

    def grab_focus(self):
        self.fields[0].grab_focus()

    def get_sensitive(self):
        if self.get_active():
            for field in self.fields:
                if field.get_sensitive():
                    return True
            return False

    def set_sensitive(self, sensitive):
        Single.set_sensitive(self, sensitive)
        if self.get_active():
            for field in self.fields:
                field.set_sensitive(sensitive)


