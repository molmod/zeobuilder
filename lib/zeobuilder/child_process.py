# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 Toon Verstraelen <Toon.Verstraelen@UGent.be>
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

import gobject, gtk, os, subprocess, cPickle, threading


__all__ = ["ChildProcessDialog"]




class BaseListenThread(threading.Thread):
    def __init__(self, f, pickle=False):
        self.f = f
        self.pickle = pickle
        threading.Thread.__init__(self)
        self.error = None

    def on_receive(self):
        raise NotImplementedError

    def on_done(self):
        raise NotImplementedError

    def run(self):
        if self.pickle:
            unpickler = cPickle.Unpickler(self.f)
            while True:
                try:
                    obj = unpickler.load()
                except EOFError:
                    break
                except Exception, error:
                    self.error = error
                    break
                gtk.gdk.threads_enter()
                self.on_receive(obj)
                gtk.gdk.threads_leave()
        else:
            while True:
                line = self.f.readline()
                if len(line) == 0:
                    break
                gtk.gdk.threads_enter()
                self.on_receive(line)
                gtk.gdk.threads_leave()
        gtk.gdk.threads_enter()
        self.on_done()
        gtk.gdk.threads_leave()
        print "END THREAD", self


class CustomListenThread(BaseListenThread):
    def __init__(self, f, pickle, on_receive, on_done=None):
        self.on_receive = on_receive
        if on_done is not None:
            self.on_done = on_done
        BaseListenThread.__init__(self, f, pickle)

    def on_done(self):
        pass


class ErrorListenThread(BaseListenThread):
    def __init__(self, f):
        BaseListenThread.__init__(self, f)
        self.lines = []

    def on_receive(self, data):
        print "CHILD STDERR:", data[:-1]
        self.lines.append(data)

    def on_done(self):
        pass


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

        for button in self.buttons:
            button.set_sensitive(False)

        print "ZEOBUILDER, spawn process"
        self.process = subprocess.Popen(
            args, bufsize=0, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if pickle:
            cPickle.dump(input_data, self.process.stdin, -1)
        else:
            self.process.stdin.write(input_data)
        self.process.stdin.close()

        print "ZEOBUILDER, fire communication thread"
        self.out_listen_thread = CustomListenThread(self.process.stdout, pickle, self.on_receive, self.on_done)
        self.out_listen_thread.start()
        self.err_listen_thread = ErrorListenThread(self.process.stderr)
        self.err_listen_thread.start()

        print "ZEOBUILDER, run the dialog"
        self.dialog.set_transient_for(context.parent_window)
        result = self.response_loop()
        self.dialog.hide()

        print "ZEOBUILDER, wait for threads to finnish"
        self.out_listen_thread.join()
        self.err_listen_thread.join()
        print "THREADS ENDED"
        print "result", result

        return result

    def response_loop(self):
        response = self.dialog.run()
        while not self.response_active:
            response = self.dialog.run()
            print "DIALOG CLOSED", response
        return response

    def on_receive(self, data):
        raise NotImplementedError

    def on_done(self):
        print "ZEOBUILDER, close stuff down"
        self.response_active = True
        for button in self.buttons:
            button.set_sensitive(True)

        os.kill(self.process.pid, 9)
        self.process.stdout.close()
        #print "ZEOBUILDER, wait for error thread to finnish"
        self.process.stderr.close()
        retcode = self.process.wait()
        if self.out_listen_thread.error is not None:
            ok_error(
                "An error occured in the communication with the child process.",
                str(self.out_listen_thread.error)
            )
        elif retcode != 0:
            ok_error(
                "An error occured in the child process.",
                "".join(self.err_listen_thread.lines)
            )

        if self.auto_close:
            print "ZEOBUILDER, auto_close dialog"
            self.dialog.response(gtk.RESPONSE_OK)

