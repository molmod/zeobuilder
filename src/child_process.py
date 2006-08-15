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


from zeobuilder import context
from zeobuilder.gui.simple import ok_error

import comthread

import gobject, gtk

import os, socket, signal


__all__ = ["ComThread", "ChildProcessDialog"]


class ComThread(comthread.ComThread, gobject.GObject):
    def __init__(self, conn):
        comthread.ComThread.__init__(self, conn)#, "ZEOBUILDER")
        gobject.GObject.__init__(self)
        self.stack = []

    def run(self):
        try:
            comthread.ComThread.run(self)
        except comthread.ProtocolError:
            gobject.idle_add(self.emit, "on-protocol-error")

    def on_received(self, instance):
        self.stack.append(instance)
        gobject.idle_add(self.emit, "on-received")


    def on_finished(self, instance):
        self.stack.append(instance)
        gobject.idle_add(self.emit, "on-finished")


gobject.signal_new("on-received", ComThread, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
gobject.signal_new("on-finished", ComThread, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
gobject.signal_new("on-protocol-error", ComThread, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())


class ChildProcessDialog(object):
    def __init__(self, dialog, buttons):
        self.dialog = dialog
        self.dialog.hide()
        self.buttons = buttons
        self.response_active = False

    def cleanup(self, kill=False, response=gtk.RESPONSE_DELETE_EVENT):
        if not self.ended:
            self.ended = True
            if kill:
                #print "ZEOBUILDER, kill child process"
                os.kill(self.pid, signal.SIGKILL)
            else:
                #print "ZEOBUILDER, wait for child process"
                os.waitpid(self.pid, 0)
            self.response_active = True
            self.dialog.response(response)
            self.dialog.hide()
            if self.connection is not None:
                self.connection.close()
            self.socket.close()
            if os.path.exists(self.socket_name):
                os.remove(self.socket_name)
            for handler in self.handlers:
                self.com_thread.disconnect(handler)
            #print "ZEOBUILDER, end of cleanup"
            del self.socket_name
            del self.pid
            del self.socket
            del self.connection


    def run(self, executable, input_instance, auto_close):
        self.response_active = False
        self.auto_close = auto_close

        for button in self.buttons:
            button.set_sensitive(False)

        class AcceptTimeOut(Exception):
            pass

        def sigalrm_handler(signal, frame):
            raise AcceptTimeOut

        self.socket_name = "ZEOBUILDER-DIALOG-%i" % os.getpid()
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.bind(self.socket_name)
        self.socket.listen(1)
        self.connection = None
        result = None


        #print "ZEOBUILDER, spawn process"
        self.pid = os.spawnv(os.P_NOWAIT, executable, [executable, self.socket_name])
        self.ended = False
        #print "ZEOBUILDER, wait 5 seconds for connection"
        #signal.signal(signal.SIGALRM, sigalrm_handler)
        #signal.alarm(5)
        try:
            self.connection, addr = self.socket.accept()
        except AcceptTimeOut:
            #print "ZEOBUILDER, no connection from child in five seconds."
            ok_error("<b><big>The child process did not connect to Zeobuilder within 5 seconds.</big></b>\n\nInform the authors of zeobuilder if you did not expect this to happen.")
            self.cleanup(kill=True)
            return None
        #print "ZEOBUILDER, child connected"
        #signal.alarm(0)
        #signal.signal(signal.SIGALRM, signal.SIG_IGN)

        #print "ZEOBUILDER, creating comthread"
        self.com_thread = ComThread(self.connection)
        #print "ZEOBUILDER, connecting signal handlers"
        self.handlers = []
        self.handlers.append(self.com_thread.connect("on-received", self.on_received))
        self.handlers.append(self.com_thread.connect("on-finished", self.on_finished))
        self.handlers.append(self.com_thread.connect("on-protocol-error", self.on_protocol_error))

        self.com_thread.start()
        #print "ZEOBUILDER, send the input to the child process"
        self.com_thread.send(input_instance)

        #print "ZEOBUILDER, run the dialog"
        self.dialog.set_transient_for(context.parent_window)
        result = self.response_loop()
        self.dialog.hide()

        #print "ZEOBUILDER, join the thread"
        self.com_thread.join()
        self.cleanup(kill=False)
        del self.ended

        return result

    def response_loop(self):
        response = self.dialog.run()
        while not self.response_active:
            response = self.dialog.run()
        return response

    def on_received(self, com_thread):
        self.handle_message(com_thread.stack.pop(0))

    def on_finished(self, com_thread):
        instance = com_thread.stack.pop(0)
        self.response_active = True
        for button in self.buttons:
            button.set_sensitive(True)
        if isinstance(instance, comthread.Failure):
            self.cleanup(kill=False)
            ok_error(
                "An exception occured in the child process.",
                instance.message,
                line_wrap=False
            )
        else:
            self.handle_done(instance)
            if self.auto_close:
                self.cleanup(kill=False, response=gtk.RESPONSE_OK)


    def on_protocol_error(self, com_thread):
        self.cleanup(kill=True)
        ok_error(
            "Invalid data was received from the client process.",
            "Inform the authors of zeobuilder if you did not expect this to happen."
        )

    def handle_message(self, message):
        pass

    def handle_done(self, message):
        pass
