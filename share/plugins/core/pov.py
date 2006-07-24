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
from zeobuilder.filters import DumpFilter, FilterError, Indenter

import numpy


class DumpPOV(DumpFilter):
    def __init__(self):
        DumpFilter.__init__(self, "Persistence of vision (render engine) (*.pov)")

    def __call__(self, f, universe, folder, nodes=None):
        application = context.application

        indenter = Indenter(f)

        scene = application.main.drawing_area.scene

        indenter.write_line("#include \"colors.inc\"")
        indenter.write_line("camera {", 1)
        if scene.opening_angle > 0.0:
            indenter.write_line("perspective")
        else:
            indenter.write_line("orthographic")
        indenter.write_line("location  <0.0, 0.0, 0.0>")
        indenter.write_line("look_at   <0.0, 0.0, -1.0>")
        indenter.write_line("right     -x*%f" % (scene.window_size*8/3))
        indenter.write_line("up        y*%f" % (scene.window_size*2))
        if scene.opening_angle > 0.0:
            indenter.write_line("angle     %f" % scene.opening_angle)

        indenter.write_line("translate <%r, %r, %r>" % tuple(-scene.viewer.translation_vector))
        indenter.write_line("translate <0.0, 0.0, %r>" % scene.znear())
        indenter.write_line("matrix <%r, %r, %r, %r, %r, %r, %r, %r, %r, 0.0, 0.0, 0.0>" % tuple(numpy.ravel(numpy.transpose(scene.rotation.rotation_matrix))))
        indenter.write_line("translate <%r, %r, %r>" % tuple(scene.center.translation_vector))

        indenter.write_line("}", -1)
        indenter.write_line("// background { White }")
        indenter.write_line("light_source {", 1)
        indenter.write_line("<1, 1, 3>, rgb .5*<1, 1, 1>")
        indenter.write_line("parallel")
        indenter.write_line("point_at <0, 0, 0>")
        indenter.write_line("}", -1)
        indenter.write_line("light_source {", 1)
        indenter.write_line("<1, 1, 3>, rgb 1*<1, 1, 1> shadowless")
        indenter.write_line("parallel")
        indenter.write_line("point_at <0, 0, 0>")
        indenter.write_line("}", -1)
        indenter.write_line("#declare my_finish = finish { ambient .3 diffuse .6 phong 1 phong_size 30};")

        # In the current implementation, each GLMixin node has to provide a
        # write_pov method. In principle one could make a 3D draw front end with
        # an opengl and povray backend to avoid this clumsy approach, but this
        # is would be an overengineered solution.
        if nodes is not None:
            for node in nodes:
                node.write_pov(indenter)
        else:
            universe.write_pov(indenter)


dump_filters = {
    "pov": DumpPOV(),
}

