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


from zeobuilder import context
from zeobuilder.actions.composed import ImmediateWithMemory, Immediate, UserError, Parameters
from zeobuilder.actions.abstract import CenterAlignBase
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.conversion import express_measure
from zeobuilder.nodes.parent_mixin import ContainerMixin
from zeobuilder.nodes.glmixin import GLTransformationMixin
from zeobuilder.nodes.glcontainermixin import GLContainerMixin
from zeobuilder.gui.simple import ok_information, ok_error, ask_save_filename
from zeobuilder.gui.fields_dialogs import FieldsDialogSimple
from zeobuilder.gui.glade_wrapper import GladeWrapper
from zeobuilder.expressions import Expression
from zeobuilder.moltools import iter_atoms, chemical_formula, create_molecular_graph
import zeobuilder.gui.fields as fields
import zeobuilder.actions.primitive as primitive
import zeobuilder.authors as authors

from molmod.periodic import periodic
from molmod.bonds import bonds, BOND_SINGLE, BOND_DOUBLE, BOND_TRIPLE
from molmod import Translation, Complete, Rotation, EqualPattern, RingPattern, \
    GraphSearch, random_orthonormal, deg

import numpy, gtk, sys, traceback


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
        total, formula = chemical_formula(iter_atoms(context.application.cache.nodes), True)
        if total > 0:
            answer = "Chemical formula: %s" % formula
            answer += "\nNumber of atoms: %i" % total
        else:
            answer = "No atoms found."
        ok_information(answer, markup=True)


def iter_particles(node, parent=None):
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
            for particle in iter_particles(child, parent):
                yield particle


def compute_center_of_mass(particles):
    weighted_center = numpy.zeros(3, float)
    total_mass = 0.0
    for mass, coordinate in particles:
        weighted_center += mass*coordinate
        total_mass += mass
    if total_mass == 0.0:
        return total_mass, weighted_center
    else:
        return total_mass, weighted_center/total_mass


def compute_inertia_tensor(particles, center):
    tensor = numpy.zeros((3,3), float)
    for mass, coordinate in particles:
        delta = coordinate - center
        tensor += mass*(
            numpy.dot(delta, delta)*numpy.identity(3, float)
           -numpy.outer(delta, delta)
        )
    return tensor


def align_rotation_matrix(inertia_tensor):
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
        for node in cache.nodes:
            if not isinstance(node, ContainerMixin): return False
        # C) passed all tests:
        return True

    def do(self):
        cache = context.application.cache
        for node in cache.nodes:
            translated_children = []
            for child in node.children:
                if isinstance(child, GLTransformationMixin) and isinstance(child.transformation, Translation):
                    if child.get_fixed():
                        translated_children = []
                        break
                    translated_children.append(child)
            if len(translated_children) == 0:
                continue

            mass, com = compute_center_of_mass(iter_particles(node))
            if mass == 0.0:
                continue

            CenterAlignBase.do(self, node, translated_children, Translation(com))


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
        for node in cache.nodes:
            if not isinstance(node, ContainerMixin): return False
        # C) passed all tests:
        return True

    def do(self):
        cache = context.application.cache
        for node in cache.nodes:
            translated_children = []
            for child in node.children:
                if isinstance(child, GLTransformationMixin) and isinstance(child.transformation, Translation):
                    if child.get_fixed():
                        translated_children = []
                        break
                    translated_children.append(child)
            if len(translated_children) == 0:
                continue

            mass, com = compute_center_of_mass(iter_particles(node))
            if mass == 0.0:
                continue

            tensor = compute_inertia_tensor(iter_particles(node), com)
            transformation = Complete(align_rotation_matrix(tensor), com)
            CenterAlignBase.do(self, node, translated_children, transformation)


class SaturateWithHydrogens(Immediate):
    description = "Saturate with hydrogens"
    menu_info = MenuInfo("default/_Object:tools/_Molecular:add", "S_aturate with hydrogens", ord("s"), False, order=(0, 4, 1, 5, 1, 2))
    authors = [authors.toon_verstraelen]
    opening_angles = {
        # (hybr, numsit): angle
          (2,    1): 0.0,
          (3,    1): 0.0,
          (4,    1): 0.0,
          (3,    2): 60.0*deg,
          (4,    2): 54.74*deg,
          (4,    3): 70.53*deg,
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
            existing_bonds = list(atom.iter_bonds())
            num_bonds = len(existing_bonds)
            bond_length = bonds.get_length(atom.number, 1, BOND_SINGLE)

            if num_bonds == 0:
                t = atom.transformation.t + numpy.array([0,bond_length,0])
                H = Atom(name="auto H", number=1, transformation=Translation(t))
                primitive.Add(H, atom.parent)
                bond = Bond(name="aut H bond", targets=[atom, H])
                primitive.Add(bond, atom.parent)
                existing_bonds.append(bond)
                num_bonds = 1

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
            rotation = Rotation.from_properties(2*numpy.pi / float(num_sites), oposite_direction, False)
            opening_key = (hybride_count, num_sites)
            opening_angle = self.opening_angles.get(opening_key)
            if opening_angle is None:
                return

            if num_bonds == 1:
                first_bond = existing_bonds[0]
                other_atom = first_bond.children[0].target
                if other_atom == atom:
                    other_atom = first_bond.children[1].target
                other_bonds = [bond for bond in other_atom.iter_bonds() if bond != first_bond]
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

            h_pos = bond_length*(oposite_direction*numpy.cos(opening_angle) + normal*numpy.sin(opening_angle))

            for i in range(num_hydrogens):
                t = atom.transformation.t + h_pos
                H = Atom(name="auto H", number=1, transformation=Translation(t))
                primitive.Add(H, atom.parent)
                bond = Bond(name="aut H bond", targets=[atom, H])
                primitive.Add(bond, atom.parent)
                h_pos = rotation * h_pos

        def hydrogenate_unsaturated_atoms(nodes):
            for node in nodes:
                if isinstance(node, Atom):
                    add_hydrogens(node)
                elif isinstance(node, ContainerMixin):
                    hydrogenate_unsaturated_atoms(node.children)

        hydrogenate_unsaturated_atoms(context.application.cache.nodes)


class SaturateHydrogensManual(ImmediateWithMemory):
    description = "Saturate with hydrogens (fixed number)"
    menu_info = MenuInfo("default/_Object:tools/_Molecular:add", "S_aturate with hydrogens (fixed number)", order=(0, 4, 1, 5, 1, 3))
    authors = [authors.toon_verstraelen]

    parameters_dialog = FieldsDialogSimple(
        "Parameters for hydrogen saturation",
        fields.group.Table(fields=[
            fields.faulty.Int(
                attribute_name="num_hydrogens",
                label_text="Number of hydrogens per atom",
                minimum=1,
            ),
            fields.faulty.MeasureEntry(
                attribute_name="valence_angle",
                measure="Angle",
                label_text="Valence angle (X-Y-H)",
                scientific=False,
                low=0.0, high=180*deg,
            ),
        ]),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK))
    )

    @staticmethod
    def analyze_selection(parameters=None):
        # A) calling ancestor
        if not ImmediateWithMemory.analyze_selection(): return False
        # B) validating
        if len(context.application.cache.nodes) == 0: return False
        # C) passed all tests:
        return True

    @classmethod
    def default_parameters(cls):
        result = Parameters()
        result.num_hydrogens = 2
        result.valence_angle = 109.4*deg
        return result

    def do(self):
        Atom = context.application.plugins.get_node("Atom")
        Bond = context.application.plugins.get_node("Bond")

        def add_hydrogens(atom):
            existing_bonds = list(atom.iter_bonds())
            bond_length = bonds.get_length(atom.number, 1, BOND_SINGLE)
            num_hydrogens = self.parameters.num_hydrogens

            if len(existing_bonds) == 0:
                t = atom.transformation.t + numpy.array([0,bond_length,0])
                H = Atom(name="auto H", number=1, transformation=Translation(t))
                primitive.Add(H, atom.parent)
                bond = Bond(name="aut H bond", targets=[atom, H])
                primitive.Add(bond, atom.parent)
                existing_bonds.append(bond)
                num_hydrogens -= 1

            main_direction = numpy.zeros(3, float)
            for bond in existing_bonds:
                shortest_vector = bond.shortest_vector_relative_to(atom.parent)
                if bond.children[1].target == atom:
                    shortest_vector *= -1
                main_direction += shortest_vector

            main_direction /= numpy.linalg.norm(main_direction)
            normal = random_orthonormal(main_direction)

            rotation = Rotation.from_properties(2*numpy.pi / float(num_hydrogens), main_direction, False)


            h_pos = bond_length*(
                main_direction*numpy.cos(self.parameters.valence_angle) +
                normal*numpy.sin(self.parameters.valence_angle)
            )

            for i in range(num_hydrogens):
                t = atom.transformation.t + h_pos
                H = Atom(name="auto H", number=1, transformation=Translation(t))
                primitive.Add(H, atom.parent)
                bond = Bond(name="aut H bond", targets=[atom, H])
                primitive.Add(bond, atom.parent)
                h_pos = rotation * h_pos

        for node in context.application.cache.nodes:
            if isinstance(node, Atom):
                add_hydrogens(node)


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


def combinations(items, n):
    if len(items) < n: return
    if n == 0: yield set([])
    for index in xrange(len(items)):
        selected = items[index]
        for combination in combinations(items[index+1:], n-1):
            combination_copy = combination.copy()
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
    description = "Apply the order of the first selection to all the other."
    menu_info = MenuInfo("default/_Object:tools/_Molecular:rearrange", "_Clone order", order=(0, 4, 1, 5, 0, 3))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        if not Immediate.analyze_selection(): return False
        cache = context.application.cache
        if len(cache.nodes) < 2: return False
        Frame = context.application.plugins.get_node("Frame")
        for cls in cache.classes:
            if not issubclass(cls, Frame): return False
        return True

    def do(self):
        frame_ref = context.application.cache.nodes[0]
        graph_ref = create_molecular_graph([frame_ref])
        try:
            match_generator = GraphSearch(EqualPattern(graph_ref))
        except PatternError, e:
            raise UserError("Could not setup a graph match definition to clone the order.")

        some_failed = False
        all_failed = True
        for frame_other in context.application.cache.nodes[1:]:
            graph_other = create_molecular_graph([frame_other])

            try:
                match = match_generator(graph_other).next()
                all_failed = False
            except (StopIteration, PatternError):
                some_failed = True
                continue

            moves = [
                (index1, graph_other.molecule.atoms[index2])
                for index1, index2
                in match.forward.iteritems()
            ]
            moves.sort()

            for new_index, atom2 in moves:
                primitive.Move(atom2, frame_other, new_index)
        if all_failed:
            raise UserError("None of the atom orders could be cloned.")
        elif some_failed:
            ok_error("Some molecules/frames did not match the first frame, so they are not reordered.")


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

        self.filter_store = gtk.ListStore(str, int)
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

    def show(self, rings, graph):
        self.rings = rings
        self.graph = graph

        # A few usefull attributes
        for ring in rings:
            vertices = ring.ring_vertices
            ring.atoms = [graph.molecule.atoms[vertex] for vertex in vertices]
            ring.bonds = [
                graph.bonds[graph.edge_index[frozenset([
                    vertices[index], vertices[(index+1)%len(ring)]
                ])]]
                for index in xrange(len(vertices))
            ]

        self.compute_properties()
        self.fill_filter_store()
        self.fill_ring_store()
        self.create_image()
        self.window.show_all()

    def compute_properties(self):
        ring_sizes = {}
        for ring in self.rings:
            size = len(ring)
            if size in ring_sizes:
                ring_sizes[size] += 1
            else:
                ring_sizes[size] = 1
            ring.center = sum(
                atom.get_absolute_frame().t
                for atom in ring.atoms
            )/len(ring)
            ring.radii = numpy.array([
                numpy.linalg.norm(atom.get_absolute_frame().t - ring.center)
                for atom in ring.atoms
            ])
            ring.av_diameter = 2*ring.radii.mean()
            ring.min_diameter = 2*ring.radii.min()
            ring.label = ", ".join(atom.get_name() for atom in ring.atoms),
        # for the histogram
        self.max_size = max(ring_sizes.iterkeys())
        self.ring_distribution = numpy.zeros(self.max_size, int)
        for ring_size, count in ring_sizes.iteritems():
            self.ring_distribution[ring_size-1] = count

    def fill_filter_store(self):
        self.filter_store.clear()
        self.filter_store.append(["All", -1])
        for index, atom in enumerate(self.graph.molecule.atoms):
            self.filter_store.append([atom.get_name(), index])
        self.cb_filter.set_active(0)

    def fill_ring_store(self):
        self.ring_store.clear()
        filter_index = self.filter_store.get_value(self.cb_filter.get_active_iter(), 1)
        for ring in self.rings:
            if filter_index == -1 or filter_index in ring.reverse:
                self.ring_store.append([
                    len(ring),
                    express_measure(ring.av_diameter, "Length"),
                    express_measure(ring.min_diameter, "Length"),
                    ring.label,
                    ring,
                ])
        self.ring_store.set_sort_column_id(0, gtk.SORT_ASCENDING)

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
            context.application.main.select_nodes(ring.atoms + ring.bonds)


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
        graph = create_molecular_graph(context.application.cache.nodes)
        match_generator = GraphSearch(RingPattern(20))
        rings = list(match_generator(graph))

        ring_distribution_window = RingDistributionWindow()
        ring_distribution_window.show(rings, graph)


class FrameMolecules(Immediate):
    description = "Frame molecules"
    menu_info = MenuInfo("default/_Object:tools/_Molecular:rearrange", "_Frame molecules", order=(0, 4, 1, 5, 0, 4))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        if not Immediate.analyze_selection(): return False
        if not isinstance(context.application.cache.node, ContainerMixin): return False
        return True

    def calc_new_positions(self, group, atoms, graph, parent):
        positions = dict((node, atom.get_frame_up_to(parent).t) for node, atom in zip(group, atoms))

        Universe = context.application.plugins.get_node("Universe")
        if isinstance(parent, Universe) and parent.cell.active.any():
            # find the atom that is the closest to the origin
            closest = group[0]
            closest_distance = numpy.linalg.norm(positions[closest])
            for node, position in positions.iteritems():
                distance = numpy.linalg.norm(position)
                if distance < closest_distance:
                    closest_distance = distance
                    closest = node

            # translate the atoms in such a way that they are not split over
            # several periodic images
            result = {}
            moved = [closest]
            not_moved = set(group)
            not_moved.discard(closest)
            while len(moved) > 0:
                subject = moved.pop()
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

        graph = create_molecular_graph(cache.nodes)
        parent = cache.node

        Frame = context.application.plugins.get_node("Frame")
        for group in graph.independent_vertices:
            atoms = [graph.molecule.atoms[i] for i in group]
            new_positions = self.calc_new_positions(group, atoms, graph, parent)
            frame = Frame(name=chemical_formula(atoms)[1])
            primitive.Add(frame, parent, index=0)
            for node, atom in zip(group, atoms):
                primitive.Move(atom, frame)
                new_position = new_positions[node]
                translation = Translation(atom.get_parentframe_up_to(parent).inv * new_position)
                primitive.SetProperty(atom, "transformation", translation)
            for atom in atoms:
                # take a copy of the references since they are going to be
                # refreshed (changed and reverted) during the loop.
                for reference in list(atom.references):
                    referent = reference.parent
                    if referent.parent != frame:
                        has_to_move = True
                        for child in referent.children:
                            if child.target.parent != frame:
                                has_to_move = False
                                break
                        if has_to_move:
                            primitive.Move(referent, frame)


class SelectBondedNeighbors(Immediate):
    description = "Select bonded neighbors"
    menu_info = MenuInfo("default/_Select:default", "_Bonded neighbors", ord("n"), False, order=(0, 3, 0, 5))
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
                for bond in node.iter_bonds():
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
    "CloneOrder": CloneOrder,
    "StrongRingDistribution": StrongRingDistribution,
    "FrameMolecules": FrameMolecules,
    "SelectBondedNeighbors": SelectBondedNeighbors,
    "SaturateHydrogensManual": SaturateHydrogensManual,
}


utility_functions = {
    "combinations": combinations,
    "first": first,
}


