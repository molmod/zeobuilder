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


from zeobuilder import context
from zeobuilder.gui.simple import ok_error

import gobject, gtk, os, subprocess, cPickle, threading, gobject, sys


__all__ = ["ChildProcessDialog"]


class ChildProcessDialog(object):
    def __init__(self, dialog, buttons):
        self.dialog = dialog
        self.dialog.hide()
        self.buttons = buttons
        self.response_active = False

    def run(self, args, input_data, auto_close, pickle=False):
        self.response_active = False
        self.auto_close = auto_close
        self.error_lines = []
        self.pickle = pickle

        for button in self.buttons:
            button.set_sensitive(False)

        #print >> sys.stderr, "ZEOBUILDER, spawn process"
        self.process = subprocess.Popen(
            args, bufsize=0, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if self.pickle:
            cPickle.dump(input_data, self.process.stdin, -1)
        else:
            self.process.stdin.write(input_data)
        self.process.stdin.close()

        #print >> sys.stderr, "ZEOBUILDER, add io_watch"
        self.event_sources = [
            gobject.io_add_watch(self.process.stdout, gobject.IO_IN, self._on_receive_out, priority=200),
            gobject.io_add_watch(self.process.stdout, gobject.IO_HUP, self._on_done, priority=200),
            gobject.io_add_watch(self.process.stderr, gobject.IO_IN, self._on_receive_err, priority=200),
        ]

        self.dialog.set_transient_for(context.parent_window)
        result = self.response_loop()
        self.dialog.hide()

        #print >> sys.stderr, "result", result
        return result

    def response_loop(self):
        response = self.dialog.run()
        while not self.response_active:
            response = self.dialog.run()
            #print >> sys.stderr, "DIALOG CLOSED", response
        return response

    def _on_receive_out(self, source, condition):
        if self.pickle:
            data = cPickle.load(self.process.stdout)
        else:
            data = self.process.stdout.readline()
        #print >> sys.stderr, "CHILD STDOUT:", data
        self.on_receive(data)
        return True

    def _on_receive_err(self, source, condition):
        line = self.process.stderr.readline()[:-1]
        #print >> sys.stderr, "CHILD STDERR:", line
        self.error_lines.append(line)
        return True

    def _on_done(self, source, condition):
        #print >> sys.stderr, "ZEOBUILDER, _on_done"
        self.response_active = True
        for button in self.buttons:
            button.set_sensitive(True)

        # make sure there is not output is left unnoticed.
        while True:
            try:
                self._on_receive_out(0, 0)
            except EOFError:
                break

        retcode = self.process.wait()
        if retcode != 0:
            ok_error(
                "An error occured in the child process.",
                "".join(self.error_lines)
            )

        if self.auto_close:
            #print >> sys.stderr, "ZEOBUILDER, auto_close dialog"
            self.dialog.response(gtk.RESPONSE_OK)

        #print >> sys.stderr, "ZEOBUILDER, release io_watch"
        for source in self.event_sources:
            gobject.source_remove(source)

        return False

    def on_receive(self, data):
        raise NotImplementedError




