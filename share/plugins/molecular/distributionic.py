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
from zeobuilder.actions.composed import ImmediateWithMemory, Parameters, UserError
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.nodes.parent_mixin import ContainerMixin
from zeobuilder.gui.fields_dialogs import FieldsDialogSimple
from zeobuilder.gui.glade_wrapper import GladeWrapper
from zeobuilder.gui.simple import ask_save_filename
from zeobuilder.gui import load_image
from zeobuilder.expressions import Expression
from zeobuilder.conversion import express_measure
import zeobuilder.gui.fields as fields

from molmod.units import to_unit
from molmod.graphs import Graph, SymmetricGraph, MatchFilterParameterized
from molmod.vectors import angle

import gtk, numpy, pylab, matplotlib

import math, os


class DistributionDialog(GladeWrapper):
    def __init__(self):
        GladeWrapper.__init__(self, "plugins/molecular/gui.glade", "di_distribution", "dialog")
        self.dialog.hide()
        self.init_callbacks(DistributionDialog)
        self.init_proxies(["fa_image"])

        figure = pylab.figure(0, figsize=(8, 4), dpi=100)
        self.mpl_widget = matplotlib.backends.backend_gtkagg.FigureCanvasGTKAgg(figure)
        self.mpl_widget.set_size_request(800, 400)
        self.fa_image.add(self.mpl_widget)

    def run(self, data, measure, label, comments):
        self.data = data
        self.data.sort()
        self.measure = measure
        self.unit = context.application.configuration.default_units[self.measure]
        self.label = label
        self.comments = comments

        self.dialog.set_title("%s distribution" % label)
        self.calculate_properties()

        self.comments.append("%s data in unit [%s]" % (self.label, self.unit))
        self.comments.append("model filename: %s" % os.path.basename(context.application.model.filename))

        self.create_images()

        self.dialog.show_all()
        result = self.dialog.run()
        self.dialog.hide()
        return result

    def calculate_properties(self):
        self.average = self.data.mean()
        self.median = numpy.median(self.data)
        self.stdev = math.sqrt(sum((self.data - self.data.mean())**2) / (len(self.data) - 1))
        request_bins = int(math.sqrt(len(self.data)))
        num_bins = request_bins
        while True:
            probs, bins = numpy.histogram(
                to_unit[self.unit](self.data),
                bins=num_bins,
                normed=False,
            )
            used_bins = sum(probs > 0)
            if used_bins >= request_bins:
                break
            num_bins = max([(request_bins*num_bins)/used_bins, num_bins+1])
        self.probs = probs*(100.0/len(self.data))
        self.bins = bins

        self.decimals = max([
            0,
            -int(math.floor(math.log10(
                abs(to_unit[self.unit](self.stdev))
            )))
        ])+2

        self.comments.append("Samples: %s" % len(self.data))
        self.comments.append("Bins: %i (%i)" % (num_bins, used_bins))
        self.comments.append("Average: %s" % express_measure(self.average, self.measure, self.decimals))
        self.comments.append("Median: %s" % express_measure(self.median, self.measure, self.decimals))
        self.comments.append("Stdev (N-1): %s" % express_measure(self.stdev, self.measure, self.decimals))

    def create_images(self):
        figure = pylab.figure(0)
        pylab.clf()
        pylab.axes([0.08, 0.1, 0.4, 0.85])
        patches = []
        labels = []

        patch_average = pylab.plot([to_unit[self.unit](self.average)]*2, [48, 52], "g-")
        patches.append(patch_average)
        labels.append("Average")

        xtmp = to_unit[self.unit](numpy.array([self.average - self.stdev, self.average + self.stdev]))
        patch_stdev = pylab.plot(xtmp, [50, 50], "m-")
        patches.append(patch_stdev)
        labels.append("+- Stdev")

        patch_line = pylab.plot(
            to_unit[self.unit](self.data),
            100*numpy.arange(len(self.data), dtype=float)/(len(self.data)-1),
            color="r",
        )
        patches.append(patch_line)
        labels.append("Cumulative")

        delta = self.bins[1] - self.bins[0]
        args = zip(self.bins, numpy.zeros(len(self.bins)), numpy.ones(len(self.bins))*delta, self.probs)
        for l, b, w, h in args:
            patch_hist = matplotlib.patches.Rectangle((l, b), w, h, facecolor="w", edgecolor="#AAAAAA")
            pylab.gca().add_patch(patch_hist)
        patches.append([patch_hist])
        labels.append("Histogram")

        pylab.xlim([self.bins[0], self.bins[-1]+delta])
        pylab.ylim([0, 100])
        #pylab.title(
        #    ("n = %s   " % len(self.data)) +
        #    ("av = %s   " % express_measure(self.average, self.measure, self.decimals)) +
        #    ("stdev = %s   " % express_measure(self.stdev, self.measure, self.decimals))
        #)
        pylab.xlabel("%s [%s]" % (self.label, self.unit))
        pylab.ylabel("Probability [%]")
        for index, line in enumerate(self.comments):
            pylab.text(
                1.05, 0.95 - index*0.06, line,
                horizontalalignment='left',
                verticalalignment='center',
                transform = pylab.gca().transAxes,
            )

        pylab.legend(patches, labels, 0)
        self.mpl_widget.draw()

    def save_data(self, filename):
        f = file(filename, "w")
        for line in self.comments:
            print >> f, "#", line
        for value in self.data:
            print >> f, to_unit[self.unit](value)
        f.close()

    def on_bu_save_clicked(self, button):
        filename = context.application.model.filename
        if filename is not None:
            filename = filename[:filename.rfind(".")] + "_"
        else:
            filename = ""
        filename += self.label.lower().replace(" ", "_")

        filename = ask_save_filename("Save distribution data", filename)
        if filename is not None:
            self.save_data("%s.txt" % filename)
            pylab.figure(0)
            self.mpl_widget.print_figure("%s.svg" % filename)
            self.mpl_widget.print_figure("%s.eps" % filename, orientation='landscape')
            self.mpl_widget.print_figure("%s.png" % filename, dpi=400)


distribution_dialog = DistributionDialog()


def search_bonds(selected_nodes):
    Bond = context.application.plugins.get_node("Bond")
    def yield_bonds(nodes):
        for node in nodes:
            if isinstance(node, Bond):
                yield node
            elif isinstance(node, ContainerMixin):
                for result in yield_bonds(node.children):
                    yield result

    bonds = {}
    for bond in yield_bonds(selected_nodes):
        key = frozenset([bond.children[0].target, bond.children[1].target])
        bonds[key] = bond
    return bonds


class DistributionBondLengths(ImmediateWithMemory):
    description = "Distribution of bond lengths"
    menu_info = MenuInfo("default/_Object:tools/_Molecular:dist", "Distribution of bond _lengths", order=(0, 4, 1, 5, 3, 0))

    parameters_dialog = FieldsDialogSimple(
        "Bond length distribution parameters",
        fields.group.Table(fields=[
            fields.faulty.Expression(
                label_text="Filter expression: atom 1",
                attribute_name="filter_atom1",
                history_name="filter_atom",
                width=250,
                height=60,
            ),
            fields.faulty.Expression(
                label_text="Filter expression: bond 1-2",
                attribute_name="filter_bond12",
                history_name="filter_bond",
                width=250,
                height=60,
            ),
            fields.faulty.Expression(
                label_text="Filter expression: atom 2",
                attribute_name="filter_atom2",
                history_name="filter_atom",
                width=250,
                height=60,
            ),
        ], cols=2),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK)),
    )

    @staticmethod
    def analyze_selection(parameters=None):
        # A) calling ancestor
        if not ImmediateWithMemory.analyze_selection(parameters): return False
        # B) validating
        cache = context.application.cache
        if len(cache.nodes) == 0: return False
        # C) passed all tests:
        return True

    @classmethod
    def default_parameters(cls):
        result = Parameters()
        result.filter_atom1 = Expression()
        result.filter_bond12 = Expression()
        result.filter_atom2 = Expression()
        return result

    def do(self):
        for key, val in self.parameters.__dict__.iteritems():
            if isinstance(val, Expression):
                val.compile_as("<%s>" % key)
                val.variables = (key[7:11],)

        bonds = search_bonds(context.application.cache.nodes)
        lengths = []

        bond_graph = SymmetricGraph([(1, 2)], 1)
        match_filter = MatchFilterParameterized(
            subgraph=bond_graph,
            calculation_tags={1: 1, 2: 1},
            thing_criteria={
                1: self.parameters.filter_atom1,
                2: self.parameters.filter_atom2,
            },
            relation_criteria={
                frozenset([1,2]): lambda things: self.parameters.filter_bond12(bonds[things]),
            },
            filter_tags=False,
        )
        graph = Graph(bonds.keys())
        try:
            for match in bond_graph.yield_matching_subgraphs(graph):
                for transformed_match in match_filter.parse(match):
                    point1 = transformed_match.forward[1].get_absolute_frame().t
                    point2 = transformed_match.forward[2].get_absolute_frame().t
                    lengths.append(numpy.linalg.norm(point1 - point2))
        except:
            raise UserError(
                "An error occured while sampling the bond lengths.",
                "If this is an error in one of the filter expressions,\n" +
                "one should see the expression mentioned below as <filter_...>.\n\n"
            )

        comments = [
            "atom 1 filter expression: %s" % self.parameters.filter_atom1.code,
            "bond 1-2 filter expression: %s" % self.parameters.filter_bond12.code,
            "atom 2 filter expression: %s" % self.parameters.filter_atom2.code,
        ]

        if len(lengths) > 0:
            distribution_dialog.run(numpy.array(lengths), "Length", "Bond length", comments)
        else:
            raise UserError("No bonds match the given criteria.")


class DistributionBendingAngles(ImmediateWithMemory):
    description = "Distribution of bending angles"
    menu_info = MenuInfo("default/_Object:tools/_Molecular:dist", "Distribution of bending _angles", order=(0, 4, 1, 5, 3, 1))

    parameters_dialog = FieldsDialogSimple(
        "Bending angle distribution parameters",
        fields.group.Table(fields=[
            fields.faulty.Expression(
                label_text="Filter expression: atom 1",
                attribute_name="filter_atom1",
                history_name="filter_atom",
                width=250,
                height=60,
            ),
            fields.faulty.Expression(
                label_text="Filter expression: bond 1-2",
                attribute_name="filter_bond12",
                history_name="filter_bond",
                width=250,
                height=60,
            ),
            fields.faulty.Expression(
                label_text="Filter expression: atom 2",
                attribute_name="filter_atom2",
                history_name="filter_atom",
                width=250,
                height=60,
            ),
            fields.faulty.Expression(
                label_text="Filter expression: bond 2-3",
                attribute_name="filter_bond23",
                history_name="filter_bond",
                width=250,
                height=60,
            ),
            fields.faulty.Expression(
                label_text="Filter expression: atom 3",
                attribute_name="filter_atom3",
                history_name="filter_atom",
                width=250,
                height=60,
            ),
        ], cols=2),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK)),
    )

    @staticmethod
    def analyze_selection(parameters=None):
        # A) calling ancestor
        if not ImmediateWithMemory.analyze_selection(parameters): return False
        # B) validating
        cache = context.application.cache
        if len(cache.nodes) == 0: return False
        # C) passed all tests:
        return True

    @classmethod
    def default_parameters(cls):
        result = Parameters()
        result.filter_atom1 = Expression()
        result.filter_bond12 = Expression()
        result.filter_atom2 = Expression()
        result.filter_bond23 = Expression()
        result.filter_atom3 = Expression()
        return result

    def do(self):
        for key, val in self.parameters.__dict__.iteritems():
            if isinstance(val, Expression):
                val.compile_as("<%s>" % key)
                val.variables = (key[7:11],)

        bonds = search_bonds(context.application.cache.nodes)
        angles = []

        angle_graph = SymmetricGraph([(1, 2), (2, 3)], 2)
        match_filter = MatchFilterParameterized(
            subgraph=angle_graph,
            calculation_tags={1: 1, 2: 0, 3: 1},
            thing_criteria={
                1: self.parameters.filter_atom1,
                2: self.parameters.filter_atom2,
                3: self.parameters.filter_atom3,
            },
            relation_criteria={
                frozenset([1,2]): lambda things: self.parameters.filter_bond12(bonds[things]),
                frozenset([2,3]): lambda things: self.parameters.filter_bond23(bonds[things]),
            },
            filter_tags=False,
        )
        graph = Graph(bonds.keys())
        try:
            for match in angle_graph.yield_matching_subgraphs(graph):
                for transformed_match in match_filter.parse(match):
                    point1 = transformed_match.forward[1].get_absolute_frame().t
                    point2 = transformed_match.forward[2].get_absolute_frame().t
                    point3 = transformed_match.forward[3].get_absolute_frame().t
                    delta1 = point2-point1
                    delta2 = point2-point3
                    if numpy.linalg.norm(delta1) > 1e-8 and \
                       numpy.linalg.norm(delta2) > 1e-8:
                        angles.append(angle(delta1, delta2))
        except:
            raise UserError(
                "An error occured while sampling the bending angles.",
                "If this is an error in one of the filter expressions,\n" +
                "one should see the expression mentioned below as <filter_...>.\n\n"
            )

        comments = [
            "atom 1 filter expression: %s" % self.parameters.filter_atom1.code,
            "bond 1-2 filter expression: %s" % self.parameters.filter_bond12.code,
            "atom 2 filter expression: %s" % self.parameters.filter_atom2.code,
            "bond 2-3 filter expression: %s" % self.parameters.filter_bond23.code,
            "atom 3 filter expression: %s" % self.parameters.filter_atom3.code,
        ]

        if len(angles) > 0:
            distribution_dialog.run(numpy.array(angles), "Angle", "Bending angle", comments)
        else:
            raise UserError("No bending angles match the given criteria.")


class DistributionDihedralAngles(ImmediateWithMemory):
    description = "Distribution of dihedral angles"
    menu_info = MenuInfo("default/_Object:tools/_Molecular:dist", "Distribution of _dihedral angles", order=(0, 4, 1, 5, 3, 2))

    parameters_dialog = FieldsDialogSimple(
        "Dihedral angle distribution parameters",
        fields.group.Table(fields=[
            fields.faulty.Expression(
                label_text="Filter expression: atom 1",
                attribute_name="filter_atom1",
                history_name="filter_atom",
                width=250,
                height=60,
            ),
            fields.faulty.Expression(
                label_text="Filter expression: bond 1-2",
                attribute_name="filter_bond12",
                history_name="filter_bond",
                width=250,
                height=60,
            ),
            fields.faulty.Expression(
                label_text="Filter expression: atom 2",
                attribute_name="filter_atom2",
                history_name="filter_atom",
                width=250,
                height=60,
            ),
            fields.faulty.Expression(
                label_text="Filter expression: bond 2-3",
                attribute_name="filter_bond23",
                history_name="filter_bond",
                width=250,
                height=60,
            ),
            fields.faulty.Expression(
                label_text="Filter expression: atom 3",
                attribute_name="filter_atom3",
                history_name="filter_atom",
                width=250,
                height=60,
            ),
            fields.faulty.Expression(
                label_text="Filter expression: bond 3-4",
                attribute_name="filter_bond34",
                history_name="filter_bond",
                width=250,
                height=60,
            ),
            fields.faulty.Expression(
                label_text="Filter expression: atom 4",
                attribute_name="filter_atom4",
                history_name="filter_atom",
                width=250,
                height=60,
            ),
        ], cols=2),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK)),
    )

    @staticmethod
    def analyze_selection(parameters=None):
        # A) calling ancestor
        if not ImmediateWithMemory.analyze_selection(parameters): return False
        # B) validating
        cache = context.application.cache
        if len(cache.nodes) == 0: return False
        # C) passed all tests:
        return True

    @classmethod
    def default_parameters(cls):
        result = Parameters()
        result.filter_atom1 = Expression()
        result.filter_bond12 = Expression()
        result.filter_atom2 = Expression()
        result.filter_bond23 = Expression()
        result.filter_atom3 = Expression()
        result.filter_bond34 = Expression()
        result.filter_atom4 = Expression()
        return result

    def do(self):
        for key, val in self.parameters.__dict__.iteritems():
            if isinstance(val, Expression):
                val.compile_as("<%s>" % key)
                val.variables = (key[7:11],)

        bonds = search_bonds(context.application.cache.nodes)
        angles = []

        angle_graph = SymmetricGraph([(1, 2), (2, 3), (3, 4)], 2)
        match_filter = MatchFilterParameterized(
            subgraph=angle_graph,
            calculation_tags={1: 1, 2: 0, 3: 0, 4: 1},
            thing_criteria={
                1: self.parameters.filter_atom1,
                2: self.parameters.filter_atom2,
                3: self.parameters.filter_atom3,
                4: self.parameters.filter_atom4,
            },
            relation_criteria={
                frozenset([1,2]): lambda things: self.parameters.filter_bond12(bonds[things]),
                frozenset([2,3]): lambda things: self.parameters.filter_bond23(bonds[things]),
                frozenset([3,4]): lambda things: self.parameters.filter_bond34(bonds[things]),
            },
            filter_tags=False,
        )
        graph = Graph(bonds.keys())
        try:
            for match in angle_graph.yield_matching_subgraphs(graph):
                for transformed_match in match_filter.parse(match):
                    point1 = transformed_match.forward[1].get_absolute_frame().t
                    point2 = transformed_match.forward[2].get_absolute_frame().t
                    point3 = transformed_match.forward[3].get_absolute_frame().t
                    point4 = transformed_match.forward[4].get_absolute_frame().t

                    normal1 = numpy.cross(point2-point1, point2-point3)
                    normal2 = numpy.cross(point3-point4, point3-point2)
                    if numpy.linalg.norm(normal1) > 1e-8 and \
                       numpy.linalg.norm(normal2) > 1e-8:
                        angles.append(angle(normal1, normal2))
        except:
            raise UserError(
                "An error occured while sampling the dihedral angles.",
                "If this is an error in one of the filter expressions,\n" +
                "one should see the expression mentioned below as <filter_...>.\n\n"
            )


        comments = [
            "atom 1 filter expression: %s" % self.parameters.filter_atom1.code,
            "bond 1-2 filter expression: %s" % self.parameters.filter_bond12.code,
            "atom 2 filter expression: %s" % self.parameters.filter_atom2.code,
            "bond 2-3 filter expression: %s" % self.parameters.filter_bond23.code,
            "atom 3 filter expression: %s" % self.parameters.filter_atom3.code,
            "bond 3-4 filter expression: %s" % self.parameters.filter_bond34.code,
            "atom 4 filter expression: %s" % self.parameters.filter_atom4.code,
        ]

        if len(angles) > 0:
            distribution_dialog.run(numpy.array(angles), "Angle", "Dihedral angle", comments)
        else:
            raise UserError("No dihedral angles match the given criteria.")

actions = {
    "DistributionBondLengths": DistributionBondLengths,
    "DistributionBendingAngles": DistributionBendingAngles,
    "DistributionDihedralAngles": DistributionDihedralAngles,
}
