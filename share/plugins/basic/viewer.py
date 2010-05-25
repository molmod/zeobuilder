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


from zeobuilder import context
from zeobuilder.actions.composed import Immediate
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.gui.fields_dialogs import FieldsDialogSimple
import zeobuilder.gui.fields as fields
import zeobuilder.authors as authors

import gtk, numpy


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
        context.application.camera.reset()
        context.application.main.drawing_area.queue_draw()


class CameraSettings(Immediate):
    description = "Edit camera settings"
    menu_info = MenuInfo("default/_View:viewer", "_Camera settings", order=(0, 2, 0, 1))
    repeatable = False
    authors = [authors.toon_verstraelen]

    viewer_configuration = FieldsDialogSimple(
        "Camera configuration",
         fields.group.HBox(fields=[
            fields.group.Table([
                fields.composed.Translation(
                    label_text="Rotation center",
                    attribute_name="rotation_center",
                ),
                fields.composed.Rotation(
                    label_text="Model rotation",
                    attribute_name="rotation",
                ),
            ]),
            fields.group.Table([
                fields.composed.Translation(
                    label_text="Eye position",
                    attribute_name="eye",
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
                    high=0.5*numpy.pi,
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
        camera = context.application.camera
        if self.viewer_configuration.run(camera) == gtk.RESPONSE_OK:
            context.application.scene.update_render_settings()


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
            fields.edit.Color(
                label_text="Periodic box color",
                attribute_name="periodic_box_color",
            ),
            fields.edit.Color(
                label_text="Selection mesh color",
                attribute_name="selection_mesh_color",
            ),
            fields.edit.Color(
                label_text="Fog color",
                attribute_name="fog_color",
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
        class Settings(object):
            pass
        settings = Settings()
        settings.__dict__ = context.application.configuration.settings
        if self.renderer_configuration.run(settings) == gtk.RESPONSE_OK:
            context.application.configuration.settings = settings.__dict__
            context.application.scene.update_render_settings()


actions = {
    "ViewReset": ViewReset,
    "CameraSettings": CameraSettings,
    "RendererConfiguration": RendererConfiguration,
}


