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
    # self_containing indicates wether the self.container also contains
    # the label or not.
    self_containing = True
    # this options are applied on the container when attached to a table
    xoptions = gtk.FILL | gtk.EXPAND
    yoptions = 0

    def __init__(self, label_text=None):
        self.label_text = label_text
        self.container = None
        self.label = None
        self.node = None
        self.nodes = None
        self.parent = None

    def get_active(self):
        return self.node != None or self.nodes != None

    def init_widgets(self, node):
        if self.applicable(node):
            self.node = node
            self.create_widgets()
        else:
            self.node = None

    def init_widgets_multiplex(self, nodes):
        for node in nodes:
            if not self.applicable(node):
                self.nodes = None
                #print "NOT APPLICABLE", self, self.label_text
                return
        #print "IS  APPLICABLE", self, self.label_text
        self.nodes = nodes
        self.create_widgets()

    def applicable(self, node):
        raise NotImplementedError

    def create_widgets(self):
        if self.label_text != None:
            self.label = gtk.Label(self.label_text)
            self.label.set_alignment(0.0, 0.5)
            self.label.set_use_markup(True)

    def destroy_widgets(self):
        if self.label != None:
            self.label.destroy()
            self.label = None
        if self.container != None:
            self.container.destroy()
            self.container = None
        self.node = None
        self.nodes = None

    def show(self, field=None):
        # makes sure the correct notebook page is shown
        # etc. to point at the incorrect field.
        if self.parent != None:
            self.parent.show(self)


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

    def read(self, node=None):
        if self.node is not None:
            for field in self.fields:
                field.read()

    def read_multiplex(self):
        if self.nodes is not None:
            for field in self.fields:
                field.read_multiplex()

    def write(self, node=None):
        if self.node is not None:
            for field in self.fields:
               field.write()

    def write_multiplex(self):
        if self.nodes is not None:
            for field in self.fields:
                field.write_multiplex()

    def check(self):
        if self.get_active():
            for field in self.fields:
                field.check()

