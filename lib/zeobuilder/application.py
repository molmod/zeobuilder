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

import gtk

import os, sys, traceback


__all__ = ["Application"]


class Application(object):
    def __init__(self, init_fn, quit=False):
        context.application = self
        self.init_fn = init_fn
        self.quit = quit

        self.initialize_config()
        self.initialize_model()
        self.initialize_action_manager()
        self.initialize_gui()
        self.initialize_cache()
        self.initialize_plugins()

        self.collect_actions()

        self.main.window.show_all()
        import gtk, gobject
        #gobject.threads_init()
        gobject.idle_add(self.after_gui)
        gtk.main()

        self.configuration.save_to_file()

    def initialize_config(self):
        from zeobuilder.config import Configuration
        self.configuration = Configuration(context.config_filename)

    def initialize_plugins(self):
        from zeobuilder.plugins import PluginsCollection
        self.plugins = PluginsCollection()

    def initialize_model(self):
        from zeobuilder.gui.models import Model
        self.model = Model()

    def initialize_cache(self):
        from zeobuilder.selection_cache import SelectionCache
        self.cache = SelectionCache()

    def initialize_action_manager(self):
        from zeobuilder.actions.manager import ActionManager
        self.action_manager = ActionManager()

    def initialize_gui(self):
        from zeobuilder.gui.visual.scene import Scene
        from zeobuilder.gui.visual.camera import Camera
        from zeobuilder.gui.visual.vis_backends import VisBackendOpenGL
        from zeobuilder.gui.main import Main
        self.camera = Camera()
        self.scene = Scene()
        self.vis_backend = VisBackendOpenGL(self.scene, self.camera)
        self.main = Main()
        context.parent_window = self.main.window

    def collect_actions(self):
        # initialize collections
        from zeobuilder.actions.collections.menu import Menu
        self.menu = Menu()
        from zeobuilder.actions.collections.interactive import InteractiveBar
        self.interactive_bar = InteractiveBar()
        self.main.vb_main.pack_start(self.interactive_bar, False, False)
        self.main.vb_main.reorder_child(self.interactive_bar, 0)
        from zeobuilder.actions.collections.drag import Drag
        self.drag = Drag()

        # translate collected actions in GUI components
        self.menu.fill_menubar(self.main.menubar)

    def after_gui(self):
        self.init_fn()
        if self.quit:
            self.model.file_close()
            self.main.window.destroy()
            gtk.main_quit()


class TestApplication(Application):
    def __init__(self, init_fn, quit=True):
        self.error_message = None
        Application.__init__(self, init_fn, quit)

    def after_gui(self):
        try:
            self.init_fn()
            if self.quit:
                self.model.file_close()
                self.main.window.destroy()
                gtk.main_quit()
        except Exception, e:
            self.error_message = (":"*70 + "\nTRACEBACK:\n%s\nMESSAGE:\n%s\n%s\n" + ":"*70) % (
                "".join(traceback.format_tb(sys.exc_traceback)), e.__class__, e
            )
            gtk.main_quit()





