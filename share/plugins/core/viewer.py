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
from zeobuilder.actions.composed import Immediate
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.gui.fields_dialogs import FieldsDialogSimple
import zeobuilder.gui.fields as fields
import zeobuilder.authors as authors

import gtk

import math


class ViewReset(Immediate):
    description = "Reset view"
    menu_info = MenuInfo("default/_View:viewer", "_Reset viewer", order=(0, 2, 0, 0))
    repeatable = False
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        if context.application.main is None: return False
        # C) passed all tests:
        return True

    def do(self):
        drawing_area = context.application.main.drawing_area
        drawing_area.scene.reset_view()
        drawing_area.queue_draw()


class ViewerConfiguration(Immediate):
    description = "Edit viewer configuration"
    menu_info = MenuInfo("default/_View:viewer", "_Configure viewer", order=(0, 2, 0, 1))
    repeatable = False
    authors = [authors.toon_verstraelen]

    viewer_configuration = FieldsDialogSimple(
        "Viewer configuration",
         fields.group.HBox(fields=[
            fields.group.Table([
                fields.composed.Translation(
                    label_text="Rotation center",
                    attribute_name="center",
                ),
                fields.composed.Rotation(
                    label_text="Model rotation",
                    attribute_name="rotation",
                ),
            ]),
            fields.group.Table([
                fields.composed.Translation(
                    label_text="Viewer position",
                    attribute_name="viewer",
                ),
                fields.faulty.Length(
                    label_text="Window size",
                    attribute_name="window_size",
                    low=0.0,
                    low_inclusive=False,
                ),
                fields.faulty.Length(
                    label_text="Window depth",
                    attribute_name="window_depth",
                    low=0.0,
                    low_inclusive=False,
                ),
                fields.faulty.MeasureEntry(
                    measure="Angle",
                    label_text="Opening angle",
                    attribute_name="opening_angle",
                    low=0,
                    low_inclusive=True,
                    high=0.5*math.pi,
                    high_inclusive=False,
                    show_popup=False,
                ),
            ]),
        ]),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK))
    )

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating and initialising
        if context.application.main is None: return False
        # C) passed all tests:
        return True

    def do(self):
        drawing_area = context.application.main.drawing_area
        if self.viewer_configuration.run(drawing_area.scene) == gtk.RESPONSE_OK:
            drawing_area.scene.update_znear()
            drawing_area.scene.apply_renderer_settings()


class RendererConfiguration(Immediate):
    description = "Edit renderer configuration"
    menu_info = MenuInfo("default/_View:viewer", "_Configure renderer", order=(0, 2, 0, 2))
    repeatable = False
    authors = [authors.toon_verstraelen]

    renderer_configuration = FieldsDialogSimple(
        "Renderer configuration",
        fields.group.Table([
            fields.edit.Color(
                label_text="Background color",
                attribute_name="background_color",
            ),
            fields.optional.CheckOptional(fields.faulty.Length(
                label_text="Fog depth",
                attribute_name="fog_depth",
                low=0.0,
                low_inclusive=False,
            )),
        ]),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK))
    )

    def do(self):
        scene = context.application.main.drawing_area.scene
        class Settings(object):
            pass
        settings = Settings()
        settings.__dict__ = context.application.configuration.settings
        if self.renderer_configuration.run(settings) == gtk.RESPONSE_OK:
            context.application.configuration.settings = settings.__dict__
            scene.apply_renderer_settings()


actions = {
    "ViewReset": ViewReset,
    "ViewerConfiguration": ViewerConfiguration,
    "RendererConfiguration": RendererConfiguration,
}
