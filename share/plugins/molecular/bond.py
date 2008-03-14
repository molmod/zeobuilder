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
from zeobuilder.actions.composed import Immediate, ImmediateWithMemory, Parameters
from zeobuilder.actions.abstract import ConnectBase, AutoConnectMixin
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.nodes.meta import Property
from zeobuilder.nodes.vector import Vector
from zeobuilder.nodes.glcontainermixin import GLContainerMixin
from zeobuilder.nodes.model_object import ModelObjectInfo
from zeobuilder.gui.fields_dialogs import DialogFieldInfo, FieldsDialogSimple
import zeobuilder.actions.primitive as primitive
import zeobuilder.gui.fields as fields
import zeobuilder.authors as authors

from molmod.data.periodic import periodic
from molmod.data.bonds import bonds, BOND_SINGLE, BOND_DOUBLE, BOND_TRIPLE, BOND_HYBRID, BOND_HYDROGEN

import numpy, gtk

import math


class Bond(Vector):
    info = ModelObjectInfo("plugins/molecular/bond.svg")
    authors = [authors.toon_verstraelen]

    #
    # State
    #

    def initnonstate(self):
        Vector.initnonstate(self)
        self.handlers = {}

    #
    # Properties
    #

    def set_quality(self, quality):
        self.quality = quality
        self.invalidate_draw_list()

    def set_bond_type(self, bond_type):
        self.bond_type = bond_type
        self.invalidate_draw_list()

    properties = [
        Property("quality", 15, lambda self: self.quality, set_quality),
        Property("bond_type", BOND_SINGLE, lambda self: self.bond_type, set_bond_type)
    ]

    #
    # Dialog fields (see action EditProperties)
    #

    dialog_fields = set([
        DialogFieldInfo("Markup", (1, 3), fields.faulty.Int(
            label_text="Quality",
            attribute_name="quality",
            minimum=3,
        )),
        DialogFieldInfo("Molecular", (6, 1), fields.edit.ComboBox(
            choices=[
                (BOND_SINGLE, "Single bond"),
                (BOND_DOUBLE, "Double bond"),
                (BOND_TRIPLE, "Triple bond"),
                (BOND_HYBRID, "Hybrid bond"),
                (BOND_HYDROGEN, "Hydrogen bond"),
            ],
            label_text="Bond type",
            attribute_name="bond_type",
        )),
    ])

    #
    # References
    #

    def define_target(self, reference, new_target):
        Vector.define_target(self, reference, new_target)
        self.handlers[new_target] = [
            new_target.connect("on_number_changed", self.atom_property_changed),
            new_target.connect("on_user_radius_changed", self.atom_property_changed),
            new_target.connect("on_user_color_changed", self.atom_property_changed),
        ]

    def undefine_target(self, reference, old_target):
        Vector.undefine_target(self, reference, old_target)
        for handler in self.handlers[old_target]:
            old_target.disconnect(handler)

    def check_target(self, reference, target):
        return isinstance(target, context.application.plugins.get_node("Atom"))

    def atom_property_changed(self, atom):
        self.invalidate_boundingbox_list()
        self.invalidate_draw_list()

    #
    # Draw
    #

    def draw(self):
        Vector.draw(self)
        if self.length <= 0: return
        half_length = 0.5 * (self.end_position - self.begin_position)
        if half_length <= 0: return
        half_radius = 0.5 * (self.begin_radius + self.end_radius)

        begin = self.children[0].target
        end = self.children[1].target

        vb = context.application.vis_backend
        vb.set_color(*begin.get_color())
        vb.translate(0.0, 0.0, self.begin_position)
        vb.draw_cone(self.begin_radius, half_radius, half_length, self.quality)
        vb.translate(0.0, 0.0, half_length)
        vb.set_color(*end.get_color())
        vb.draw_cone(half_radius, self.end_radius, half_length, self.quality)

    def write_pov(self, indenter):
        self.calc_vector_dimensions()
        if self.length <= 0: return
        half_length = 0.5 * (self.end_position - self.begin_position)
        if half_length <= 0: return
        half_position = half_length + self.begin_position
        half_radius = 0.5 * (self.begin_radius + self.end_radius)
        begin = self.children[0].target
        end = self.children[1].target
        indenter.write_line("union {", 1)
        indenter.write_line("cone {", 1)
        indenter.write_line("<0.0, 0.0, %f>, %f, <0.0, 0.0, %f>, %f" % (self.begin_position, self.begin_radius, half_position, half_radius))
        indenter.write_line("pigment { rgb <%f, %f, %f> }" % tuple(begin.get_color()[0:3]))
        indenter.write_line("finish { my_finish }")
        indenter.write_line("}", -1)
        indenter.write_line("cone {", 1)
        indenter.write_line("<0.0, 0.0, %f>, %f, <0.0, 0.0, %f>, %f" % (half_position, half_radius, self.end_position, self.end_radius))
        indenter.write_line("pigment { rgb <%f, %f, %f> }" % tuple(end.get_color()[0:3]))
        indenter.write_line("finish { my_finish }")
        indenter.write_line("}", -1)
        Vector.write_pov(self, indenter)
        indenter.write_line("}", -1)

    #
    # Revalidation
    #

    def revalidate_bounding_box(self):
        Vector.revalidate_bounding_box(self)
        if self.length > 0:
            temp = {True: self.begin_radius, False: self.end_radius}[self.begin_radius > self.end_radius]
            self.bounding_box.extend_with_point(numpy.array([-temp, -temp, self.begin_position]))
            self.bounding_box.extend_with_point(numpy.array([temp, temp, self.end_position]))

    def calc_vector_dimensions(self):
        Vector.calc_vector_dimensions(self)
        begin = self.children[0].target
        end = self.children[1].target
        if self.length <= 0.0: return
        c = (begin.get_radius() - end.get_radius()) / self.length
        if abs(c) > 1:
            self.begin_radius = 0
            self.end_radius = 0
            self.begin_position = 0
            self.end_position = 0
        else:
            scale = 0.5
            s = math.sqrt(1 - c**2)
            self.begin_radius = scale * begin.get_radius() * s
            self.end_radius = scale * end.get_radius() * s
            self.begin_position = scale * c * begin.get_radius()
            self.end_position = self.length + scale * c * end.get_radius()


class ConnectBond(ConnectBase):
    bond_type = None

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not ConnectBase.analyze_selection(): return False
        # B) validating
        for cls in context.application.cache.classes:
            if not issubclass(cls, context.application.plugins.get_node("Atom")):
                return False
        # C) passed all tests:
        return True

    def new_connector(self, begin, end):
        return Bond(targets=[begin, end], bond_type=self.bond_type)


class ConnectSingleBond(ConnectBond):
    description = "Connect with a single bond"
    menu_info = MenuInfo("default/_Object:tools/_Connect:pair", "_Single bond", image_name="plugins/molecular/bond1.svg", order=(0, 4, 1, 3, 0, 1))
    authors = [authors.toon_verstraelen]
    bond_type = BOND_SINGLE


class ConnectDoubleBond(ConnectBond):
    description = "Connect with a double bond"
    menu_info = MenuInfo("default/_Object:tools/_Connect:pair", "_Double bond", image_name="plugins/molecular/bond2.svg", order=(0, 4, 1, 3, 0, 2))
    authors = [authors.toon_verstraelen]
    bond_type = BOND_DOUBLE


class ConnectTripleBond(ConnectBond):
    description = "Connect with a triple bond"
    menu_info = MenuInfo("default/_Object:tools/_Connect:pair", "_Triple bond", image_name="plugins/molecular/bond3.svg", order=(0, 4, 1, 3, 0, 3))
    authors = [authors.toon_verstraelen]
    bond_type = BOND_TRIPLE


class AutoConnectPhysical(AutoConnectMixin, Immediate):
    description = "Add bonds (database)"
    menu_info = MenuInfo("default/_Object:tools/_Molecular:add", "_Add bonds (database)", ord("b"), order=(0, 4, 1, 5, 1, 0))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not AutoConnectMixin.analyze_selection(): return False
        if not Immediate.analyze_selection(): return False
        # C) passed all tests:
        return True

    def allow_node(self, node):
        return isinstance(node, context.application.plugins.get_node("Atom"))

    def get_vector(self, atom1, atom2, distance):
        if atom1 in atom2.yield_neighbors():
            return None
        bond_type = bonds.bonded(atom1.number, atom2.number, distance)
        if bond_type is None:
            return None
        else:
            return Bond(bond_type=bond_type, targets=[atom1, atom2])

    def do(self):
        AutoConnectMixin.do(self, bonds.max_length)


class AutoConnectParameters(AutoConnectMixin, ImmediateWithMemory):
    description = "Add bonds (parameters)"
    menu_info = MenuInfo("default/_Object:tools/_Molecular:add", "_Add bonds (parameters)", order=(0, 4, 1, 5, 1, 1))
    authors = [authors.toon_verstraelen]

    parameters_dialog = FieldsDialogSimple(
        "Bond specification",
        fields.group.Table([
            fields.faulty.Int(
                label_text="Atom number 1",
                attribute_name="number1",
                show_popup=False,
                minimum=1,
                maximum=118
            ),
            fields.faulty.Int(
                label_text="Atom number 2",
                attribute_name="number2",
                show_popup=False,
                minimum=1,
                maximum=118
            ),
            fields.faulty.Length(
                label_text="Maximum bond length",
                attribute_name="distance",
                show_popup=False,
                low=0.0,
                low_inclusive=False
            ),
            fields.edit.ComboBox(
                choices=[
                    (BOND_SINGLE, "Single bond"),
                    (BOND_DOUBLE, "Double bond"),
                    (BOND_TRIPLE, "Triple bond")],
                label_text="Bond type",
                attribute_name="bond_type"
            ),
        ]),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK))
    )

    @staticmethod
    def analyze_selection(parameters=None):
        # A) calling ancestor
        if not ImmediateWithMemory.analyze_selection(parameters): return False
        if not AutoConnectMixin.analyze_selection(): return False
        # C) passed all tests:
        return True

    def allow_node(self, node):
        return (
            isinstance(node, context.application.plugins.get_node("Atom")) and
            (
                node.number == self.parameters.number1 or
                node.number == self.parameters.number2
            )
        )

    def get_vector(self, atom1, atom2, distance):
        if (((atom1.number == self.parameters.number1) and
             (atom2.number == self.parameters.number2)) or
            ((atom1.number == self.parameters.number2) and
             (atom2.number == self.parameters.number1))) and \
           atom1 not in atom2.yield_neighbors():
            if self.parameters.distance >= distance:
                return Bond(bond_type=self.parameters.bond_type, targets=[atom1, atom2])
        return None

    @classmethod
    def default_parameters(cls):
        result = Parameters()
        result.number1 = 6
        result.number2 = 6
        result.distance = 0.5
        result.bond_type = BOND_SINGLE
        return result

    def do(self):
        AutoConnectMixin.do(self, max([1, self.parameters.distance]))


nodes = {
    "Bond": Bond,
}

actions = {
    "ConnectSingleBond": ConnectSingleBond,
    "ConnectDoubleBond": ConnectDoubleBond,
    "ConnectTripleBond": ConnectTripleBond,
    "AutoConnectPhysical": AutoConnectPhysical,
    "AutoConnectParameters": AutoConnectParameters,
}




