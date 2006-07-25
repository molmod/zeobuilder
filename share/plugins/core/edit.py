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
from zeobuilder.actions.collections.menu import MenuInfo, MenuInfoBase
from zeobuilder.nodes.parent_mixin import ContainerMixin
from zeobuilder.gui.fields_dialogs import FieldsDialogSimple
from zeobuilder.zml import dump_to_file, load_from_string, load_from_file
import zeobuilder.actions.primitive as primitive
import zeobuilder.gui.fields as fields

import gtk

import copy, StringIO


class UndoMenuInfo(MenuInfoBase):
    def __init__(self):
        MenuInfoBase.__init__(self, "default/_Edit:actions", ord("z"), image_name=gtk.STOCK_UNDO, order=(0, 1, 0, 0))

    def get_label(self):
        undo_stack = context.application.action_manager.undo_stack
        if len(undo_stack) > 0:
            return "_Undo '%s'" % undo_stack[-1].description
        else:
            return "_Undo"


class Undo(Immediate):
    description = "Undo"
    menu_info = UndoMenuInfo()
    repeatable = False

    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        undo_stack = context.application.action_manager.undo_stack
        if len(undo_stack) == 0: return False
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)

    def do(self):
        context.application.action_manager.undo()


class RedoMenuInfo(MenuInfoBase):
    def __init__(self):
        MenuInfoBase.__init__(self, "default/_Edit:actions", ord("z"), accel_shift=True, image_name=gtk.STOCK_REDO, order=(0, 1, 0, 1))

    def get_label(self):
        redo_stack = context.application.action_manager.redo_stack
        if len(redo_stack) > 0:
            return "_Redo '%s'" % redo_stack[-1].description
        else:
            return "_Redo"


class Redo(Immediate):
    description = "Redo"
    menu_info = RedoMenuInfo()
    repeatable = False

    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        redo_stack = context.application.action_manager.redo_stack
        if len(redo_stack) == 0: return False
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)

    def do(self):
        context.application.action_manager.redo()


class RepeatMenuInfo(MenuInfoBase):
    def __init__(self):
        MenuInfoBase.__init__(self, "default/_Edit:actions", ord("y"), image_name=gtk.STOCK_REFRESH, order=(0, 1, 0, 2))

    def get_label(self):
        last_action = context.application.action_manager.last_action
        if last_action is None:
            return "Re_peat"
        else:
            return "Re_peat '%s'" % last_action.description


class Repeat(Immediate):
    description = "Repeat"
    menu_info = RepeatMenuInfo()
    repeatable = False

    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        last_action = context.application.action_manager.last_action
        if last_action is None: return False
        if not last_action.want_repeat(): return False
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)

    def do(self):
        context.application.action_manager.repeat()


def delete(nodes):
    for dupe in nodes:
        if dupe.model is not None: # this check must be made because a dupe
                               # might get deleted by the consequence of the
                               # deletion of one of the former dupes.
            primitive.Delete(dupe)


def copy_to_clipboard(nodes):
    serialized = StringIO.StringIO()
    if dump_to_file(serialized, nodes) > 0:
        def get_func(clipboard, selection_data, info, user_data):
            selection_data.set("ZML", 8, serialized.getvalue())

        def clear_func(clipboard, user_data):
            serialized.close()

        clipboard = gtk.clipboard_get()
        clipboard.set_with_data([("ZML", 0, 0)], get_func, clear_func)


class Cut(Immediate):
    description = "Cut the selection to the clipboard"
    menu_info = MenuInfo("default/_Edit:clipboard", "Cu_t", accel_key=ord("x"), image_name=gtk.STOCK_CUT, order=(0, 1, 1, 0))
    repeatable = False

    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        if len(cache.nodes) == 0: return False
        if cache.some_nodes_without_indirect_children_fixed: return False
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)

    def do(self):
        source = copy.copy(context.application.cache.nodes_without_indirect_children)
        copy_to_clipboard(source)
        delete(source)


class Copy(Immediate):
    description = "Copy the selection to the clipboard"
    menu_info = MenuInfo("default/_Edit:clipboard", "_Copy", accel_key=ord("c"), image_name=gtk.STOCK_COPY, order=(0, 1, 1, 1))
    repeatable = False

    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        if len(cache.nodes) == 0: return False
        if cache.some_nodes_without_indirect_children_fixed: return False
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)

    def do(self):
        source = copy.copy(context.application.cache.nodes_without_indirect_children)
        copy_to_clipboard(source)


class Paste(Immediate):
    description = "Paste the contents of the clipboard"
    menu_info = MenuInfo("default/_Edit:clipboard", "_Paste", accel_key=ord("v"), image_name=gtk.STOCK_PASTE, order=(0, 1, 1, 2))
    repeatable = False

    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        if not isinstance(cache.node, ContainerMixin): return False
        clipboard = gtk.clipboard_get()
        if not clipboard.wait_is_target_available("ZML"): return False
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)

    def do(self):
        parent = context.application.cache.node

        def load_func(clipboard, selection_data, user_data):
            string_representation = selection_data.data
            if string_representation is None:
                return
            nodes = load_from_string(string_representation)
            for node in nodes:
                if parent.check_add(node.__class__):
                    primitive.Add(node, parent)

        clipboard = gtk.clipboard_get()
        clipboard.request_contents("ZML", load_func)


class Delete(Immediate):
    description = "Delete the selected object(s)"
    menu_info = MenuInfo("default/_Edit:deldup", "_Delete", 65535, False, image_name=gtk.STOCK_DELETE, order=(0, 1, 2, 0))

    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        if len(context.application.cache.nodes) == 0: return False
        if context.application.cache.some_nodes_without_indirect_children_fixed: return False
        # C) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)

    def do(self):
        dupes = copy.copy(context.application.cache.nodes_without_indirect_children)
        delete(dupes)


class Duplicate(Immediate):
    description = "Duplicate nodes"
    menu_info = MenuInfo("default/_Edit:deldup", "_Duplicate", ord("d"), order=(0, 1, 2, 1))

    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating
        cache = context.application.cache
        if cache.some_nodes_fixed: return False
        if not isinstance(cache.parent, ContainerMixin): return False
        # D) passed all tests:
        return True
    analyze_selection = staticmethod(analyze_selection)

    def do(self):
        cache = context.application.cache
        originals = cache.nodes
        parent = cache.parent
        highest_index = cache.highest_index

        # Lazy solution for the moment: could use deepcopy here
        serialized = StringIO.StringIO()
        dump_to_file(serialized, originals)
        serialized.seek(0)
        #print serialized.getvalue()
        duplicates = load_from_file(serialized)

        for duplicate in duplicates:
            highest_index += 1
            primitive.Add(duplicate, parent, index=highest_index)


class EditConfiguration(Immediate):
    description = "Edit configuration"
    menu_info = MenuInfo("default/_Edit:preferences", "_Configuration", image_name=gtk.STOCK_PREFERENCES, order=(0, 1, 3, 0))

    edit_config = FieldsDialogSimple(
        "Zeobuilder configuration",
        fields.composed.Units(
            label_text="Default units",
            attribute_name="default_units",
        ),
        ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL), (gtk.STOCK_OK, gtk.RESPONSE_OK))
    )

    def do(self):
        self.edit_config.run(context.application.configuration)


actions = {
    "Undo": Undo,
    "Redo": Redo,
    "Repeat": Repeat,
    "Cut": Cut,
    "Copy": Copy,
    "Paste": Paste,
    "Delete": Delete,
    "Duplicate": Duplicate,
    "EditConfiguration": EditConfiguration,
}
