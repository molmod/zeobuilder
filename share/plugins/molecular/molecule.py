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
from zeobuilder.actions.composed import Immediate, UserError
from zeobuilder.actions.abstract import CenterAlignBase
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.conversion import express_measure
from zeobuilder.nodes.parent_mixin import ContainerMixin
from zeobuilder.nodes.glcontainermixin import GLContainerMixin
from zeobuilder.gui.simple import ok_information, ok_error, ask_save_filename
from zeobuilder.gui.fields_dialogs import FieldsDialogSimple
from zeobuilder.gui.glade_wrapper import GladeWrapper
from zeobuilder.expressions import Expression
from zeobuilder.moltools import yield_atoms, chemical_formula, create_graph_bonds
import zeobuilder.gui.fields as fields
import zeobuilder.actions.primitive as primitive
import zeobuilder.authors as authors

from molmod.data.periodic import periodic
from molmod.data.bonds import bonds, BOND_SINGLE, BOND_DOUBLE, BOND_TRIPLE
from molmod.transformations import Translation, Complete, Rotation
from molmod.graphs import MatchDefinitionError, ExactMatchDefinition, RingMatchDefinition, MatchGenerator
from molmod.vectors import random_orthonormal

import numpy, gtk

import math, sys, traceback, copy


class ChemicalFormula(Immediate):
    description = "Show chemical formula"
    menu_info = MenuInfo("default/_Object:tools/_Molecular:info", "_Chemical Formula", order=(0, 4, 1, 5, 2, 0))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        if not Immediate.analyze_selection(): return False
        if len(context.application.cache.nodes) == 0: return False
        return True

    def do(self):
        total, formula = chemical_formula(yield_atoms(context.application.cache.nodes), True)
        if total > 0:
            answer = "Chemical formula: %s" % formula
            answer += "\nNumber of atoms: %i" % total
        else:
            answer = "No atoms found."
        ok_information(answer, markup=True)


def yield_particles(node, parent=None):
    if parent is None:
        parent = node
    Atom = context.application.plugins.get_node("Atom")
    for child in node.children:
        if isinstance(child, Atom):
            yield (
                periodic[child.number].mass,
                child.get_frame_relative_to(parent).t
            )
        elif isinstance(child, GLContainerMixin):
            for particle in yield_particles(child, parent):
                yield particle

def calculate_center_of_mass(particles):
    weighted_center = numpy.zeros(3, float)
    total_mass = 0.0
    for mass, coordinate in particles:
        weighted_center += mass*coordinate
        total_mass += mass
    if total_mass == 0.0:
        return total_mass, weighted_center
    else:
        return total_mass, weighted_center/total_mass

def calculate_inertia_tensor(particles, center):
    tensor = numpy.zeros((3,3), float)
    for mass, coordinate in particles:
        delta = coordinate - center
        tensor += mass*(
            numpy.dot(delta, delta)*numpy.identity(3, float)
           -numpy.outer(delta, delta)
        )
    return tensor

def default_rotation_matrix(inertia_tensor):
    if abs(inertia_tensor.ravel()).max() < 1e-6:
        return numpy.identity(3, float)
    evals, evecs = numpy.linalg.eig(inertia_tensor)
    result = numpy.array([evecs[:,index] for index in evals.argsort()], float).transpose()
    if numpy.linalg.det(result) < 0: result *= -1
    return result


class CenterOfMass(CenterAlignBase):
    description = "Center of mass"
    menu_info = MenuInfo("default/_Object:tools/_Transform:center", "Center of _mass frame", order=(0, 4, 1, 2, 2, 2))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not CenterAlignBase.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        if not isinstance(cache.node, ContainerMixin): return False
        if len(cache.translated_children) == 0: return False
        if cache.some_children_fixed: return False
        # C) passed all tests:
        return True

    def do(self):
        cache = context.application.cache
        node = cache.node
        translation = Translation()
        mass, com = calculate_center_of_mass(yield_particles(node))
        if mass == 0.0:
            raise UserError("No particles (atoms) found.")
        translation.t = com
        CenterAlignBase.do(self, node, cache.translated_children, translation)


class CenterOfMassAndPrincipalAxes(CenterOfMass):
    description = "Center of mass and principal axes"
    menu_info = MenuInfo("default/_Object:tools/_Transform:centeralign", "Center of mass and _principal axes frame", order=(0, 4, 1, 2, 4, 1))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not CenterOfMass.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        if not isinstance(cache.node, ContainerMixin): return False
        if len(cache.transformed_children) == 0: return False
        if cache.some_children_fixed: return False
        # C) passed all tests:
        return True

    def do(self):
        cache = context.application.cache
        node = cache.node
        transformation = Complete()

        mass, com = calculate_center_of_mass(yield_particles(node))
        if mass == 0.0:
            raise UserError("No particles (atoms) found.")
        transformation.t = com

        tensor = calculate_inertia_tensor(yield_particles(node), com)
        transformation.r = default_rotation_matrix(tensor)
        CenterAlignBase.do(self, node, cache.translated_children, transformation)


class SaturateWithHydrogens(Immediate):
    description = "Saturate with hydrogens"
    menu_info = MenuInfo("default/_Object:tools/_Molecular:add", "S_aturate with hydrogens", order=(0, 4, 1, 5, 1, 2))
    authors = [authors.toon_verstraelen]
    opening_angles = {
        # (hybr, numsit): angle
          (2,    1):                  0.0,
          (3,    1):                  0.0,
          (4,    1):                  0.0,
          (3,    2):      math.pi/180*60.0,
          (4,    2):      math.pi/180*54.735610317245346,
          (4,    3):      math.pi/180*70.528779365509308
    }

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        if len(context.application.cache.nodes) == 0: return False
        # C) passed all tests:
        return True

    def do(self):
        Atom = context.application.plugins.get_node("Atom")
        Bond = context.application.plugins.get_node("Bond")

        def lone_pairs(number):
            # very naive implemention for neutral atoms in the second and the
            # third row
            if number <= 6:
                return 0
            elif number <= 10:
                return number - 6
            elif number <= 14:
                return 0
            elif number <= 18:
                return number - 14
            else:
                return 0

        def valence_el(number):
            # very naive implemention for neutral atoms in the second and the
            # third row
            if number <= 2:
                return number
            elif number <= 10:
                return number - 2
            elif number <= 18:
                return number - 10
            else:
                return 0

        def add_hydrogens(atom):
            existing_bonds = list(atom.yield_bonds())
            num_bonds = len(existing_bonds)
            if num_bonds == 0:
                return

            used_valence = 0
            oposite_direction = numpy.zeros(3, float)
            for bond in existing_bonds:
                shortest_vector = bond.shortest_vector_relative_to(atom.parent)
                if bond.children[1].target == atom:
                    shortest_vector *= -1
                oposite_direction -= shortest_vector

                if bond.bond_type == BOND_SINGLE:
                    used_valence += 1
                elif bond.bond_type == BOND_DOUBLE:
                    used_valence += 2
                elif bond.bond_type == BOND_TRIPLE:
                    used_valence += 3

            oposite_direction /= numpy.linalg.norm(oposite_direction)

            num_hydrogens = valence_el(atom.number) - 2*lone_pairs(atom.number) - used_valence
            if num_hydrogens <= 0:
                return

            hybride_count = num_hydrogens + lone_pairs(atom.number) + num_bonds - (used_valence - num_bonds)
            num_sites = num_hydrogens + lone_pairs(atom.number)
            rotation = Rotation()
            rotation.set_rotation_properties(2*math.pi / float(num_sites), oposite_direction, False)
            opening_key = (hybride_count, num_sites)
            opening_angle = self.opening_angles.get(opening_key)
            if opening_angle is None:
                return

            if num_bonds == 1:
                first_bond = existing_bonds[0]
                other_atom = first_bond.children[0].target
                if other_atom == atom:
                    other_atom = first_bond.children[1].target
                other_bonds = [bond for bond in other_atom.yield_bonds() if bond != first_bond]
                if len(other_bonds) > 0:
                    normal = other_bonds[0].shortest_vector_relative_to(atom.parent)
                    normal -= numpy.dot(normal, oposite_direction) * oposite_direction
                    normal /= numpy.linalg.norm(normal)
                    if other_bonds[0].children[0].target == other_atom:
                        normal *= -1
                else:
                    normal = random_orthonormal(oposite_direction)
            elif num_bonds == 2:
                normal = numpy.cross(oposite_direction, existing_bonds[0].shortest_vector_relative_to(atom.parent))
                normal /= numpy.linalg.norm(normal)
            elif num_bonds == 3:
                normal = random_orthonormal(oposite_direction)
            else:
                return

            bond_length = bonds.get_length(atom.number, 1, BOND_SINGLE)
            h_pos = bond_length*(oposite_direction*math.cos(opening_angle) + normal*math.sin(opening_angle))

            for i in range(num_hydrogens):
                H = Atom(name="auto H", number=1)
                H.transformation.t = atom.transformation.t + h_pos
                primitive.Add(H, atom.parent)
                bond = Bond(name="aut H bond", targets=[atom, H])
                primitive.Add(bond, atom.parent)
                h_pos = rotation.vector_apply(h_pos)

        def hydrogenate_unsaturated_atoms(nodes):
            for node in nodes:
                if isinstance(node, Atom):
                    add_hydrogens(node)
                elif isinstance(node, ContainerMixin):
                    hydrogenate_unsaturated_atoms(node.children)

        hydrogenate_unsaturated_atoms(context.application.cache.nodes)


RESPONSE_EVALUATE = 1
RESPONSE_SELECT = 2
RESPONSE_SAVE = 3

class NeighborShellsDialog(FieldsDialogSimple):
    def __init__(self):
        self.atom_expression = Expression()
        FieldsDialogSimple.__init__(
            self,
            "Neighbor shells",
            fields.faulty.Expression(
                label_text="Atom expression (atom, graph)",
                attribute_name="atom_expression",
                history_name="atom_expression",
                width=250,
                height=150,
            ), (
                ("Evaluate", RESPONSE_EVALUATE),
                ("Select", RESPONSE_SELECT),
                (gtk.STOCK_SAVE, RESPONSE_SAVE),
                (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
            )
        )

    def create_dialog(self):
        FieldsDialogSimple.create_dialog(self)

        self.list_view = gtk.TreeView(self.list_store)

        column = gtk.TreeViewColumn("Index", gtk.CellRendererText(), text=0)
        column.set_sort_column_id(0)
        self.list_view.append_column(column)

        column = gtk.TreeViewColumn("Number", gtk.CellRendererText(), text=1)
        column.set_sort_column_id(1)
        self.list_view.append_column(column)

        column = gtk.TreeViewColumn("Atom", gtk.CellRendererText(), text=2)
        column.set_sort_column_id(2)
        self.list_view.append_column(column)

        column = gtk.TreeViewColumn("Value", gtk.CellRendererText(), markup=3)
        column.set_sort_column_id(3)
        self.list_view.append_column(column)

        for index in xrange(1, self.max_shell_size+1):
            column = gtk.TreeViewColumn("Shell %i" % index, gtk.CellRendererText(), markup=index+3)
            column.set_sort_column_id(index+3)
            self.list_view.append_column(column)

        selection = self.list_view.get_selection()
        selection.set_mode(gtk.SELECTION_MULTIPLE)
        selection.connect("changed", self.on_selection_changed)

        self.scrolled_window = gtk.ScrolledWindow()
        self.scrolled_window.set_shadow_type(gtk.SHADOW_IN)
        self.scrolled_window.set_shadow_type(gtk.SHADOW_IN)
        self.scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scrolled_window.set_border_width(6)
        self.scrolled_window.add(self.list_view)
        self.scrolled_window.set_size_request(400, 300)
        self.scrolled_window.show_all()

        self.dialog.vbox.pack_start(self.scrolled_window)

    def run(self, max_shell_size, rows, graph):
        self.graph = graph
        self.max_shell_size = max_shell_size

        self.list_store = gtk.ListStore(int, int, *([str]*(max_shell_size+2)))
        for index, row in enumerate(rows):
            row += [""]*(max_shell_size-(len(row)-4))
            self.list_store.append(row)

        response = FieldsDialogSimple.run(self, self)

        self.list_view.set_model(None)
        for column in self.list_view.get_columns():
            self.list_view.remove_column(column)
        del self.graph
        del self.max_shell_size

        return response

    def on_selection_changed(self, selection):
        model, paths = selection.get_selected_rows()
        to_select = []
        for path in paths:
            iter = model.get_iter(path)
            to_select.append(self.graph.nodes[model.get_value(iter, 0)-1])
        context.application.main.select_nodes(to_select)

    def on_dialog_response(self, dialog, response_id):
        FieldsDialogSimple.on_dialog_response(self, dialog, response_id)
        if self.valid:
            self.atom_expression.variables = ("atom", "graph")
            self.atom_expression.compile_as("<atom_expression>")
            if response_id == RESPONSE_EVALUATE:
                self.evaluate()
                self.hide = False
            if response_id == RESPONSE_SELECT:
                self.select()
                self.hide = True
            elif response_id == RESPONSE_SAVE:
                self.save()
                self.hide = False

    def do_expressions(self):
        atom_values = []
        try:
            for atom in self.graph.nodes:
                atom_values.append(self.atom_expression(atom, self.graph))
        except:
            exc_type, exc_value, tb = sys.exc_info()
            err_msg = "".join(traceback.format_exception(exc_type, exc_value, tb))
            ok_error(
                "An error occured while evaluating the shell and atom expressions.",
                err_msg, line_wrap=False
            )
            self.hide = False
            return None
        return atom_values

    def evaluate(self):
        atom_values = self.do_expressions()
        if atom_values is not None:
            for index, value in enumerate(atom_values):
                self.list_store[index][3] = value

    def select(self):
        atom_values = self.do_expressions()
        if atom_values is not None:
            to_select = [atom for atom, value in zip(self.graph.nodes, atom_values) if value]
            context.application.main.select_nodes(to_select)

    def save(self):
        atom_values = self.do_expressions()
        if atom_values is not None:
            filename = context.application.model.filename
            if filename is None:
                filename = ""
            else:
                filename = filename[:filename.rfind(".")]
            filename = ask_save_filename("Save shell data", filename)
            if filename is not None:
                if not filename.endswith(".txt"):
                    filename += ".txt"
                f = file(filename, "w")
                for atom, value in zip(self.graph.nodes, atom_values):
                    print >> f, atom.get_name(), value
                f.close()


neighbor_shells_dialog = NeighborShellsDialog()


class AnalyzeNieghborShells(Immediate):
    description = "Analyze the neighbor shells"
    menu_info = MenuInfo("default/_Object:tools/_Molecular:info", "_Neighbor shells", order=(0, 4, 1, 5, 2, 2))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        if not Immediate.analyze_selection(): return False
        if len(context.application.cache.nodes) == 0: return False
        return True

    def do(self):
        graph, foo = create_graph_bonds(context.application.cache.nodes)
        graph.init_distances()
        graph.init_trees_and_shells
        max_shell_size = graph.distances.ravel().max()

        def yield_rows():
            for index, node in enumerate(graph.nodes):
                yield [index+1, node.number, node.name, ""] + [
                    "%i: %s" % chemical_formula(atoms, True) for atoms in
                    graph.shells[node][1:]
                ]

        neighbor_shells_dialog.run(max_shell_size, yield_rows(), graph)


def combinations(items, n):
    if len(items) < n: return
    if n == 0: yield set([])
    for index in xrange(len(items)):
        selected = items[index]
        for combination in combinations(items[index+1:], n-1):
            combination_copy = copy.copy(combination)
            combination_copy.add(selected)
            yield combination_copy
combinations.authors=[authors.toon_verstraelen]


def first(l):
    if hasattr(l, "next"):
        try:
            return l.next()
        except StopIteration:
            return None
    elif len(l) > 0:
        return l[0]
    else:
        return None
first.authors=[authors.toon_verstraelen]


class CloneOrder(Immediate):
    description = "Apply the order of the first selection to the second."
    menu_info = MenuInfo("default/_Object:tools/_Molecular:rearrange", "_Clone order", order=(0, 4, 1, 5, 0, 3))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        if not Immediate.analyze_selection(): return False
        cache = context.application.cache
        if len(cache.nodes) != 2: return False
        Frame = context.application.plugins.get_node("Frame")
        for cls in cache.classes:
            if not issubclass(cls, Frame): return False
        return True

    def do(self):
        frame1, frame2 = context.application.cache.nodes

        graph1, foo = create_graph_bonds([frame1])
        graph2, foo = create_graph_bonds([frame2])
        del foo

        try:
            match_generator = MatchGenerator(ExactMatchDefinition(graph1))
        except MatchDefinitionError, e:
            raise UserError("Can not apply the order of the first selection to the second.")

        try:
            match = match_generator(graph2).next()
        except StopIteration:
            raise UserError("The connectivity of the two selections differs.")

        moves = [
            (graph1.index[atom1], atom2)
            for atom1, atom2
            in match.forward.iteritems()
        ]
        moves.sort()

        for new_index, atom2 in moves:
            primitive.Move(atom2, frame2, new_index)


class RingDistributionWindow(GladeWrapper):
    def __init__(self):
        GladeWrapper.__init__(self, "plugins/molecular/gui.glade", "wi_ring_distribution", "window")
        self.window.hide()
        self.init_callbacks(RingDistributionWindow)
        self.init_proxies(["al_image", "cb_filter", "tv_rings"])

        import zeobuilder.mplwrap as mplwrap
        import pylab
        self.figure = pylab.figure(figsize=(4, 4), dpi=100)
        self.mpl_widget = mplwrap.FigureCanvas(self.figure)
        self.mpl_widget.set_size_request(400, 400)
        #self.mpl_widget.set_border_width(6) TODO
        self.al_image.add(self.mpl_widget)

        self.filter_store = gtk.ListStore(str, object)
        self.cb_filter.set_model(self.filter_store)
        cell_renderer = gtk.CellRendererText()
        self.cb_filter.pack_start(cell_renderer)
        self.cb_filter.add_attribute(cell_renderer, "text", 0)
        self.cb_filter.connect("changed", self.on_filter_changed)

        self.ring_store = gtk.ListStore(int, str, str, str, object)
        self.tv_rings.set_model(self.ring_store)
        self.tv_rings.append_column(gtk.TreeViewColumn("Size", gtk.CellRendererText(), text=0))
        self.tv_rings.append_column(gtk.TreeViewColumn("Av. diameter", gtk.CellRendererText(), text=1))
        self.tv_rings.append_column(gtk.TreeViewColumn("Min. diameter", gtk.CellRendererText(), text=2))
        self.tv_rings.append_column(gtk.TreeViewColumn("Label", gtk.CellRendererText(), text=3))
        self.tv_rings.get_selection().connect("changed", self.on_ring_selection_changed)

        context.application.action_manager.connect("model-changed", self.on_model_changed)

    def show(self, rings, graph, bonds_by_pair):
        self.rings = rings
        self.graph = graph
        for ring in rings:
            ring.bonds = [
                bonds_by_pair[frozenset([ring.forward[index], ring.forward[(index+1)%(ring.length+1)]])]
                for index in xrange(ring.length+1)
            ]

        self.fill_stores()
        self.calculate_properties()
        self.create_image()
        self.window.show_all()

    def fill_stores(self):
        self.filter_store.clear()
        self.filter_store.append(["All", None])
        for node in self.graph.nodes:
            self.filter_store.append([node.get_name(), node])
        self.cb_filter.set_active(0)

        self.fill_ring_store()

    def fill_ring_store(self):
        self.ring_store.clear()
        filter_node = self.filter_store.get_value(self.cb_filter.get_active_iter(), 1)
        for ring in self.rings:
            center = sum(
                node.get_absolute_frame().t
                for node in ring.forward.itervalues()
            )/len(ring.forward)
            radii = [
                numpy.linalg.norm(node.get_absolute_frame().t - center)
                for node in ring.forward.itervalues()
            ]
            av_radius = 2*sum(radii)/len(radii)
            min_radius = 2*min(radii)
            if filter_node is None or filter_node in ring.backward:
                self.ring_store.append([
                    len(ring),
                    express_measure(av_radius, "Length"),
                    express_measure(min_radius, "Length"),
                    str([node.get_name() for index, node in sorted(ring.forward.iteritems())]),
                    ring,
                ])
        self.ring_store.set_sort_column_id(0, gtk.SORT_ASCENDING)

    def calculate_properties(self):
        ring_sizes = {}
        for ring in self.rings:
            size = ring.size
            if size in ring_sizes:
                ring_sizes[size] += 1
            else:
                ring_sizes[size] = 1
        self.max_size = max(ring_sizes.iterkeys())
        self.ring_distribution = numpy.zeros(self.max_size, int)
        for ring_size, count in ring_sizes.iteritems():
            self.ring_distribution[ring_size-1] = count

    def create_image(self):
        import pylab, matplotlib
        pylab.figure(self.figure.number)
        pylab.clf()
        pylab.axes([0.08, 0.1, 0.9, 0.85])

        args = zip(
            numpy.arange(self.max_size)+0.5,
            numpy.zeros(self.max_size),
            numpy.ones(self.max_size),
            self.ring_distribution
        )
        for l, b, w, h in args:
            patch_hist = matplotlib.patches.Rectangle((l, b), w, h, facecolor="w", edgecolor="#AAAAAA")
            pylab.gca().add_patch(patch_hist)
            if h > 0:
                pylab.text(l+0.5*w, h, str(h), horizontalalignment='center')

        pylab.ylim([0, self.ring_distribution.max()*1.2])
        pylab.xlim([0.5, self.max_size+1.5])
        pylab.xlabel("Ring size")
        pylab.ylabel("Count")

        self.mpl_widget.draw()

    def cleanup(self):
        self.window.hide()
        self.rings = None
        self.graph = None
        self.ring_distribution = None
        self.filter_store.clear()
        self.ring_store.clear()
        import pylab
        pylab.figure(self.figure.number)
        pylab.clf()

    def on_window_delete_event(self, window, event):
        self.cleanup()
        return True

    def on_model_changed(self, manager):
        self.cleanup()

    def on_filter_changed(self, cb_filter):
        self.fill_ring_store()

    def on_ring_selection_changed(self, selection):
        model, iter = selection.get_selected()
        if iter is None:
            context.application.main.select_nodes([])
        else:
            ring = model.get_value(iter, 4)
            context.application.main.select_nodes(
                ring.forward.values() + ring.bonds
            )


class StrongRingDistribution(Immediate):
    description = "Ring distribution"
    menu_info = MenuInfo("default/_Object:tools/_Molecular:info", "_Strong ring distribution", order=(0, 4, 1, 5, 2, 3))
    required_modules = ["pylab", "matplotlib"]
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        if not Immediate.analyze_selection(): return False
        if len(context.application.cache.nodes) == 0: return False
        return True

    def do(self):
        graph, bonds_by_pair = create_graph_bonds(context.application.cache.nodes)
        match_generator = MatchGenerator(
            RingMatchDefinition(10),
        )
        rings = list(match_generator(graph))

        ring_distribution_window = RingDistributionWindow()
        ring_distribution_window.show(rings, graph, bonds_by_pair)


class FrameMolecules(Immediate):
    description = "Frame molecules"
    menu_info = MenuInfo("default/_Object:tools/_Molecular:rearrange", "_Frame molecules", order=(0, 4, 1, 5, 0, 4))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        if not Immediate.analyze_selection(): return False
        if not isinstance(context.application.cache.node, ContainerMixin): return False
        return True

    def calc_new_positions(self, atoms, graph, parent):
        positions = dict((atom, atom.get_frame_up_to(parent).t) for atom in atoms)

        # find the atom that is the closest to the origin
        closest = atoms[0]
        closest_distance = numpy.linalg.norm(positions[closest])
        for atom, position in positions.iteritems():
            distance = numpy.linalg.norm(position)
            if distance < closest_distance:
                closest_distance = distance
                closest = atom

        #
        result = {}
        moved = [closest]
        not_moved = set(atoms)
        not_moved.discard(closest)
        while len(moved) > 0:
            subject = moved.pop(0)
            for neighbor in graph.neighbors[subject]:
                if neighbor in not_moved:
                    not_moved.discard(neighbor)
                    moved.append(neighbor)
                    delta = positions[neighbor] - positions[subject]
                    delta = parent.shortest_vector(delta)
                    positions[neighbor] = positions[subject] + delta
        return positions



    def do(self):
        cache = context.application.cache

        graph, bonds_by_pair = create_graph_bonds(cache.nodes)
        molecules = graph.get_nodes_per_independent_graph()
        parent = cache.node

        Frame = context.application.plugins.get_node("Frame")
        for atoms in molecules:
            new_positions = self.calc_new_positions(atoms, graph, parent)
            frame = Frame(name=chemical_formula(atoms)[1])
            primitive.Add(frame, parent, index=0)
            for atom in atoms:
                primitive.Move(atom, frame, select=False)
                new_position = new_positions[atom]
                translation = Translation()
                translation.t = atom.get_parentframe_up_to(parent).vector_apply_inverse(new_position)
                primitive.SetProperty(atom, "transformation", translation)
            for atom in atoms:
                # take a copy of the references since they are going to be
                # refreshed (changed and reverted) during the loop.
                for reference in copy.copy(atom.references):
                    referent = reference.parent
                    if referent.parent != frame:
                        has_to_move = True
                        for child in referent.children:
                            if child.target.parent != frame:
                                has_to_move = False
                                break
                        if has_to_move:
                            primitive.Move(referent, frame, select=False)


class SelectBondedNeighbors(Immediate):
    description = "Select bonded neighbors"
    menu_info = MenuInfo("default/_Select:default", "_Bonded neighbors", order=(0, 3, 0, 5))
    authors = [authors.bartek_szyja]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        if len(context.application.cache.nodes) == 0: return False
        # C) passed all tests:
        return True

    def do(self):

        Atom = context.application.plugins.get_node("Atom")

        to_select = []

        for node in context.application.cache.nodes:
            if isinstance(node, Atom):
                to_select.append(node)
                for bond in node.yield_bonds():
                    if bond.children[0].target not in context.application.cache.nodes:
                        to_select.append(bond.children[0].target)
                    if bond.children[1].target not in context.application.cache.nodes:
                        to_select.append(bond.children[1].target)
        context.application.main.select_nodes(to_select)


actions = {
    "ChemicalFormula": ChemicalFormula,
    "CenterOfMass": CenterOfMass,
    "CenterOfMassAndPrincipalAxes": CenterOfMassAndPrincipalAxes,
    "SaturateWithHydrogens": SaturateWithHydrogens,
    "AnalyzeNieghborShells": AnalyzeNieghborShells,
    "CloneOrder": CloneOrder,
    "StrongRingDistribution": StrongRingDistribution,
    "FrameMolecules": FrameMolecules,
    "SelectBondedNeighbors": SelectBondedNeighbors,
}


utility_functions = {
    "combinations": combinations,
    "first": first,
}



