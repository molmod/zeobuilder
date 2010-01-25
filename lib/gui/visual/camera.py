# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2007 - 2009 Toon Verstraelen <Toon.Verstraelen@UGent.be>, Center
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

"""
To understand this module properly, it is essential to be aware of the different
coordinate systems that are used in Zeobuilder

1) Screen coordinates

   These are just the pixel coordinates in the drawing area. x goes from 0 to
   width-1 (from left to right) and y goes from 0 to height-1 (from top to
   bottom).

2) Camera coordinates

   These are also two dimensional coordinates and they are just a simple
   transformation of the screen coordinates. x remains horizontal and y remains
   vertical. x = -0.5..0.5, y= -0.5..0.5

3) Eye coordinates

   These are three dimensional coordinates. The center of this coordinate frame
   is defined by the variable self.eye. The rotation of this frame is
   defined by the matrix self.rotation. The negative z-axis of this frame, is
   the direction in which the camera looks, while the two other axes define the
   tilt of the camera.

4) Model coordinates. These coordinates are used as 'fixed' coordinates in
   Zeobuilder. In the case of a periodic model, the origin corresponds to one
   of the corners of the periodic box.

All the visualization related coordinates are defined in one of the four
coordinate frames above. Some of the relevant variables for the 3D visualization
are explained below:

* self.rotation_center, defined in model coordinates + center of unit cell

  This is the point in space defines the center of rotation when the user
  rotates the whole model. (i.e. when nothing is selected)

* self.opening_angle

  This variable is used to determine the (minimal )opening angle of te camera,
  when the perspective projection is used. When this variable is set to zero,
  the orthogonal projection is used.

* self.znear

  The distance from the eye to the frontal clipping plane. In the case of
  orthogonal projection, this is alwas zero

* self.window_size

  The interpretation of this variable depends on the projection type.
    - Orthogonal: The distance in model_coordinates or obeserver coordinates
      (these are the same) of the min(width, height) of the screen.
    - Perspective: The distance in model_coordinates or obeserver coordinates
      (these are the same) of the min(width, height) of the screen, in the plane
      orthogonal to the viewing direction at a distance of self._znear from the
      eye.

* self.window_depth

  The distance in model or eye coordinates between the frontal and the
  back clipping plane.

* self.rotation.r

  This is a 3x3 orthonormal rotation matrix. it rotates a vector in model
  coordinates into eye coordinates. The full transformation then becomes...

  FIXME

* self.eye FIXME

"""


from zeobuilder import context
from zeobuilder.nodes.glmixin import GLTransformationMixin

from molmod import Translation, Rotation, angstrom

import numpy


class Camera(object):
    def __init__(self):
        # register configuration settings: default camera
        from zeobuilder.gui import fields
        from zeobuilder.gui.fields_dialogs import DialogFieldInfo
        config = context.application.configuration
        config.register_setting(
            "viewer_distance",
            100.0*angstrom,
            DialogFieldInfo("Default Viewer", (1, 0), fields.faulty.Length(
                label_text="Distance from origin",
                attribute_name="viewer_distance",
                low=0.0,
                low_inclusive=True,
            )),
        )
        config.register_setting(
            "opening_angle",
            0.0,
            DialogFieldInfo("Default Viewer", (1, 1), fields.faulty.MeasureEntry(
                measure="Angle",
                label_text="Camera opening angle",
                attribute_name="opening_angle",
                low=0.0,
                low_inclusive=True,
                high=0.5*numpy.pi,
                high_inclusive=False,
                show_popup=False,
            )),
        )
        config.register_setting(
            "window_size",
            25*angstrom,
            DialogFieldInfo("Default Viewer", (1, 2), fields.faulty.Length(
                label_text="Window size",
                attribute_name="window_size",
                low=0.0,
                low_inclusive=False,
            )),
        )
        config.register_setting(
            "window_depth",
            200.0*angstrom,
            DialogFieldInfo("Default Viewer", (1, 3), fields.faulty.Length(
                label_text="Window depth",
                attribute_name="window_depth",
                low=0.0,
                low_inclusive=False,
            )),
        )

        self.reset()

    def reset(self):
        config = context.application.configuration
        self.rotation_center = Translation.identity()
        self.rotation = Rotation.identity()
        self.eye = Translation([0,0,config.viewer_distance])
        self.opening_angle = config.opening_angle
        self.window_size = config.window_size
        self.window_depth = config.window_depth

    def get_znear(self):
        if self.opening_angle > 0.0:
            return 0.5*self.window_size/numpy.tan(0.5*self.opening_angle)
        else:
            return 0.0
    znear = property(get_znear)

    # coordinate transformations

    def eye_to_camera(self, vector_e):
        tmp = numpy.ones(2, float)
        znear = self.znear
        if znear > 0:
            return -vector_e[:2]/vector_e[2]/self.window_size*znear
        else:
            return vector_e[:2]/self.window_size

    def camera_window_to_eye(self, vector_c):
        tmp = numpy.zeros(3, float)
        tmp[:2] = vector_c*self.window_size
        znear = self.znear
        if znear > 0:
            tmp[2] = -self.znear
        else:
            tmp[2] = -self.window_size/3.0
        return tmp

    def model_to_eye(self, vector_m):
        scene = context.application.scene
        tmp = scene.model_center.inv * vector_m
        tmp = self.rotation_center.inv * tmp
        tmp = self.rotation.inv * tmp
        tmp[2] -= self.znear
        tmp = self.eye.inv * tmp
        return tmp

    def eye_to_model(self, vector_e):
        scene = context.application.scene
        tmp = self.eye * vector_e
        tmp[2] += self.znear
        tmp = self.rotation * tmp
        tmp = self.rotation_center * tmp
        tmp = scene.model_center * tmp
        return tmp

    def model_to_camera(self, vector_m):
        return self.eye_to_camera(self.model_to_eye(vector_m))

    def camera_window_to_model(self, vector_c):
        return self.eye_to_model(self.camera_window_to_eye(vector_c))

    def object_to_depth(self, gl_object):
        result = -self.model_to_eye(gl_object.get_absolute_frame().t)[2]
        return result

    def object_to_camera(self, gl_object):
        return self.eye_to_camera(self.model_to_eye(gl_object.get_absolute_frame().t))

    def object_to_eye(self, gl_object):
        return self.model_to_eye(gl_object.get_absolute_frame().t)

    def object_eye_rotation(self, gl_object):
        """
            Returns a matrix that consists of the x, y and z axes of the
            eye frame in the coordinates of the parent frame of the given
            object.
        """
        if hasattr(gl_object, "parent") and \
           isinstance(gl_object.parent, GLTransformationMixin):
            parent_matrix = gl_object.parent.get_absolute_frame().r
        else:
            parent_matrix = numpy.identity(3, float)
        result = numpy.dot(self.rotation.r.transpose(), parent_matrix).transpose()
        return result

    def depth_to_scale(self, depth):
        """ transforms a depth into a scale (au/camcoords)"""
        znear = self.znear
        if znear > 0:
            return depth/znear*self.window_size
        else:
            return self.window_size

    def vector_in_plane(self, r, p_m):
        """Returns a vector at camera position r in a plane (through p, orthogonal to viewing direction)

        Arguments
            r  --  a two-dimensional vector in camera coordinates
            p_m  --  a three-dimensional vector in model coordinates

        Returns
            rp  --  a three-dimensional vector in model coordinates that lies
                    at the intersection of a plane and a line. The plane is
                    orthogonal to the viewing direction and goes through the
                    point p. The line connects the eye (eye_m below) with the
                    point r (r_m below) in the camera window.
        """

        eye_m = self.eye_to_model(numpy.zeros(3, float))
        r_m = self.camera_window_to_model(r)
        center_m = self.camera_window_to_model(numpy.zeros(2, float))

        normal = (eye_m - center_m)
        normal /= numpy.linalg.norm(normal)

        if self.znear > 0:
            # the line is defined as r = eye_m + d*t, where t = -infinity ... infinity
            d =  eye_m - r_m

            # t at the intersection:
            t = -numpy.dot(eye_m - p_m, normal)/numpy.dot(d, normal)

            return eye_m + d*t
        else:
            # the line is defined as r = r_m + d*t, where t = -infinity ... infinity
            d = normal

            # t at the intersection:
            t = -numpy.dot(r_m - p_m, normal)/numpy.dot(d, normal)

            return r_m + d*t


