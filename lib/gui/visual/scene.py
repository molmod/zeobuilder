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
from zeobuilder.undefined import Undefined

from molmod import angstrom, Translation

import numpy


class Scene(object):
    def __init__(self):
        # register configuration settings: default camera
        config = context.application.configuration
        config.register_setting(
            "background_color",
            numpy.array([0, 0, 0, 0], float),
            None,
        )
        config.register_setting(
            "selection_mesh_color",
            numpy.array([1, 1, 1, 0], float),
            None,
        )
        config.register_setting(
            "fog_color",
            numpy.array([0, 0, 0, 0], float),
            None,
        )
        config.register_setting(
            "fog_depth",
            10.0*angstrom,
            None,
        )

        self.revalidations = []
        self.clip_planes = []

    def initialize_draw(self):
        vb = context.application.vis_backend
        self.rotation_center_list = vb.create_list()
        self.begin_mesh_list = vb.create_list()
        self.end_mesh_list = vb.create_list()
        self.update_rotation_center()
        self.update_render_settings()

    def update_rotation_center(self):
        vb = context.application.vis_backend
        small = 0.1
        big = 0.3
        vb.begin_list(self.rotation_center_list)
        vb.draw_polygon((
            numpy.array([1.0, 0.0, 0.0], float),
            numpy.array([
                ( small,    0.0, 0.0),
                (   big,    big, 0.0),
                (   0.0,  small, 0.0),
                (  -big,    big, 0.0),
                (-small,    0.0, 0.0),
                (  -big,   -big, 0.0),
                (   0.0, -small, 0.0),
                (   big,   -big, 0.0),
            ], float)
        ))
        vb.end_list()

    def update_render_settings(self):
        vb = context.application.vis_backend
        configuration = context.application.configuration

        vb.set_background_color(configuration.background_color)
        if isinstance(configuration.fog_depth, Undefined):
            vb.unset_fog()
        else:
            camera = context.application.camera
            zfar = camera.znear + camera.window_depth
            vb.set_fog(configuration.fog_color, zfar - configuration.fog_depth, zfar)

        vb.begin_list(self.begin_mesh_list)
        c = configuration.selection_mesh_color
        vb.set_color(c[0]*5, c[1]*5, c[2]*5, c[3])
        vb.set_line_width(1)
        vb.set_specular(False)
        vb.end_list()

        vb.begin_list(self.end_mesh_list)
        vb.set_specular(True)
        vb.end_list()

        context.application.main.drawing_area.queue_draw()

    def get_model_center(self):
        universe = context.application.model.universe
        if universe is None:
            return Translation.identity()
        else:
            return universe.model_center
    model_center = property(get_model_center)

    def add_revalidation(self, revalidation):
        self.revalidations.append(revalidation)

    def draw(self):
        vb = context.application.vis_backend
        for plane_i, coefficients in enumerate(self.clip_planes):
            vb.set_clip_plane(plane_i, coefficients)

        self.revalidations.reverse()
        for revalidation in self.revalidations:
            revalidation()
        self.revalidations = []
        universe = context.application.model.universe
        if universe is not None:
            vb.call_list(universe.total_list)

        for plane_i in xrange(len(self.clip_planes)):
            vb.unset_clip_plane(plane_i)


