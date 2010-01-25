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
from zeobuilder.undefined import Undefined
from zeobuilder.filters import Indenter, FilterError
from zeobuilder.nodes.parent_mixin import ParentMixin, ContainerMixin, ReferentMixin
from zeobuilder.nodes.model_object import ModelObject
from zeobuilder.expressions import Expression

from molmod import Translation, Rotation, Complete, UnitCell

import xml.sax.handler, xml.sax.saxutils, base64, gzip, bz2, numpy, types
import StringIO, string, gobject


__all__ = ["dump_to_file", "load_from_file", "load_from_string"]


def dump_to_file(f, node):

    identifiers = {}

    def dump_stage1(node):
        cls = node.__class__
        if issubclass(cls, ModelObject):
            identifiers[node] = len(identifiers)
            if issubclass(cls, ContainerMixin):
                for child in node.children:
                    dump_stage1(child)
        elif cls == list:
            for item in node:
                dump_stage1(item)


    def dump_stage2():
        deleted_some = True
        while deleted_some:
            to_be_deleted = []
            for model_object in identifiers.iterkeys():
                if isinstance(model_object, ReferentMixin):
                    for child in model_object.children:
                        if not child.target in identifiers:
                            to_be_deleted.append(model_object)
                            break
            deleted_some = len(to_be_deleted) > 0
            for model_object in to_be_deleted:
                del identifiers[model_object]


    def dump_stage3(indenter, node, use_references, name=None):
        cls = type(node)
        if cls == types.InstanceType: cls = node.__class__ # For old style stuff

        if name is None: name_key = ""
        else: name_key = " label=" + xml.sax.saxutils.quoteattr(name)

        if issubclass(cls, str):
            indenter.write_line("<str%s>%s</str>" % (name_key, xml.sax.saxutils.escape(node)))
        elif issubclass(cls, float):
            indenter.write_line("<float%s>%s</float>" % (name_key, str(node)))
        elif issubclass(cls, bool):
            indenter.write_line("<bool%s>%s</bool>" % (name_key, str(node)))
        elif issubclass(cls, int):
            indenter.write_line("<int%s>%s</int>" % (name_key, str(node)))
        elif cls == Undefined:
            pass
        elif cls == list:
            indenter.write_line("<list%s>" % name_key, 1)
            for item in node: dump_stage3(indenter, item, use_references)
            indenter.write_line("</list>", -1)
        elif cls == dict:
            indenter.write_line("<dict%s>" % name_key, 1)
            for key, val in node.iteritems():
                if not isinstance(key, str):
                    raise FilterError("ZML supports only strings as dictionary keys.")
                dump_stage3(indenter, val, use_references, key)
            indenter.write_line("</dict>", -1)
        elif cls == tuple:
            indenter.write_line("<tuple%s>" % name_key, 1)
            for item in node: dump_stage3(indenter, item, use_references)
            indenter.write_line("</tuple>", -1)
        elif cls == numpy.ndarray:
            shape = node.shape
            indenter.write_line("<array%s>" % name_key, 1)
            indenter.write("<shape>")
            for value in node.shape:
                indenter.write("%s " % value)
            indenter.write("</shape>", True)
            indenter.write("<cells>")
            for value in numpy.ravel(node):
                indenter.write("%s " % value)
            indenter.write("</cells>", True)
            indenter.write_line("</array>", -1)
        elif cls == StringIO.StringIO:
            indenter.write("<binary%s>" % name_key)
            node.seek(0)
            base64.encode(node, f)
            indenter.write("</binary>", True)
        elif cls == Translation:
            indenter.write_line("<translation%s>" % name_key, 1)
            dump_stage3(indenter, node.t, use_references, name="translation_vector")
            indenter.write_line("</translation>", -1)
        elif cls == Rotation:
            indenter.write_line("<rotation%s>" % name_key, 1)
            dump_stage3(indenter, node.r, use_references, name="rotation_matrix")
            indenter.write_line("</rotation>", -1)
        elif cls == Complete:
            indenter.write_line("<transformation%s>" % name_key, 1)
            dump_stage3(indenter, node.t, use_references, name="translation_vector")
            dump_stage3(indenter, node.r, use_references, name="rotation_matrix")
            indenter.write_line("</transformation>", -1)
        elif cls == UnitCell:
            indenter.write_line("<unit_cell%s>" % name_key, 1)
            dump_stage3(indenter, node.matrix, use_references, name="matrix")
            dump_stage3(indenter, node.active, use_references, name="active")
            indenter.write_line("</unit_cell>", -1)
        elif cls == Expression:
            indenter.write_line("<expression%s>%s</expression>" % (name_key, xml.sax.saxutils.escape(node.code)))
        elif issubclass(cls, ModelObject):
            if node in identifiers:
                if use_references:
                    indenter.write_line("<reference to='%i' />" % identifiers[node])
                else:
                    indenter.write_line("<model_object%s id='%i' class='%s'>" % (name_key, identifiers[node], node.class_name()), 1)
                    for key, item in node.__getstate__().iteritems():
                        dump_stage3(indenter, item, key!="children", key)
                    indenter.write_line("</model_object>", -1)
        else:
            raise FilterError, "Can not handle node %s of class %s" % (node, cls)

    indenter = Indenter(f)
    dump_stage1(node)
    dump_stage2()
    indenter.write_line("<?xml version='1.0'?>")
    indenter.write_line("<zml_file version='0.2'>", 1)
    dump_stage3(indenter, node, False)
    indenter.write_line("</zml_file>", -1)

    # this is usefull when the caller wants to know if there were actually
    # model_objects pickled.
    return len(identifiers)

# ---


class ZMLTag(object):
    def __init__(self, name, attributes):
        self.name = name
        if "label" in attributes: self.label = str(attributes["label"])
        else: self.label = None
        self.attributes = attributes
        if self.name == "binary":
            self.binary_content = True
            self.content = StringIO.StringIO()
        else:
            self.binary_content = False
            self.content = ""
        self.value = None
        self.being_processed = True

    def add_content(self, content):
        if self.binary_content: self.content.write(content)
        else: self.content += content

    def close(self):
        self.being_processed = False


class ZMLHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.root = None
        self.model_object_tags = {}
        self.target_ids = {}

        self.hierarchy = []
        # contains a recursive list of nodes being produced, based on the parsed XML
        # each item is a list/dict and the last subitem is related to tag not yet closed
        # in the xml file. The rest of the subitems are completed tags at the same tag-depth. Each
        # subitem is a ZMLtag object where name may be None or a string.

    def startElement(self, name, attrs):
        if name == "zml_file":
            if attrs.getValue("version") != "0.2": raise FilterError, "Only format 0.2 is supported in this version of Zeobuilder. Use zml-upgrade to convert older zml files to the zml 0.2 format"
        else:
            new_tag = ZMLTag(name, dict((name, attrs.getValue(name)) for name in attrs.getNames()))
            if (len(self.hierarchy) == 0) or (self.hierarchy[-1][-1].being_processed):
                self.hierarchy.append([new_tag])
            else:
                self.hierarchy[-1].append(new_tag)

    def characters(self, content):
        if len(content) > 0 and len(self.hierarchy) > 0 and len(self.hierarchy[-1]) > 0 and self.hierarchy[-1][-1].being_processed:
            #print "\"" + content + "\"", len(self.hierarchy), len(self.hierarchy[-1]), self.hierarchy[-1][-1].name
            self.hierarchy[-1][-1].add_content(content)

    def endElement(self, name):
        if name == "zml_file": return
        # now that we have gatherd all information of this tag, create an appropriate object

        # first find the tags involved in this operation
        current_tag = self.hierarchy[-1][-1]
        child_tags = []
        if not current_tag.being_processed:
            current_tag = self.hierarchy[-2][-1]
            child_tags = self.hierarchy[-1]

        # do it
        if name == "str": current_tag.value = str(current_tag.content)
        elif name == "float": current_tag.value = float(current_tag.content)
        elif name == "int": current_tag.value = int(current_tag.content)
        elif name == "bool":
            temp = current_tag.content.lower().strip()
            if temp == 'true': current_tag.value = True
            else: current_tag.value = False
        elif name == "list": current_tag.value = [tag.value for tag in child_tags]
        elif name == "dict": current_tag.value = dict((tag.label, tag.value) for tag in child_tags)
        elif name == "tuple": current_tag.value = tuple(tag.value for tag in child_tags)
        elif name == "shape":
            current_tag.value = tuple(int(item) for item in current_tag.content.split())
        elif name == "cells":
            current_tag.value = numpy.array([eval(item) for item in current_tag.content.split()])
        elif name == "array":
            child_dict = dict((tag.name, tag.value) for tag in child_tags)
            current_tag.value = numpy.reshape(child_dict["cells"], child_dict["shape"])
        elif name == "grid": current_tag.value = numpy.reshape(numpy.array([eval(item) for item in current_tag.content.split()]), (int(current_tag.attributes["rows"]), int(current_tag.attributes["cols"]), -1))
        elif name == "binary":
            current_tag.value = StringIO.StringIO()
            current_tag.content.seek(0)
            base64.decode(current_tag.content, current_tag.value)
        elif name == "translation":
            current_tag.value = Translation(child_tags[0].value)
        elif name == "rotation":
            current_tag.value = Rotation(child_tags[0].value)
        elif name == "transformation":
            child_dict = dict((tag.label, tag.value) for tag in child_tags)
            current_tag.value = Complete(
                child_dict["rotation_matrix"],
                child_dict["translation_vector"],
            )
        elif name == "unit_cell":
            child_dict = dict((tag.label, tag.value) for tag in child_tags)
            current_tag.value = UnitCell(
                child_dict["matrix"],
                child_dict["active"],
            )
        elif name == "expression":
            current_tag.value = Expression(current_tag.content)
        elif name == "reference":
            current_tag.value = None
            referent_tag = self.hierarchy[-3][-1]
            target_ids = self.target_ids.get(referent_tag)
            if target_ids is None:
                target_ids = []
                self.target_ids[referent_tag] = target_ids
            target_ids.append(int(current_tag.attributes["to"]))
        elif name == "model_object":
            Class = context.application.plugins.get_node(str(current_tag.attributes["class"]))
            current_tag.state = dict((tag.label, tag.value) for tag in child_tags)
            current_tag.value = Class()
            self.model_object_tags[int(current_tag.attributes["id"])] = current_tag
        else: pass

        # close the door
        current_tag.content = None
        current_tag.close()
        if len(child_tags) > 0: self.hierarchy.pop()

    def endDocument(self):
        self.root = self.hierarchy[0][0].value
        self.hierarchy = []

        # fix the targets:
        for referent_tag, target_ids in self.target_ids.iteritems():
            referent_tag.state["targets"] = [
                self.model_object_tags[target_id].value for target_id in target_ids
            ]

        # set the states of all the model_objects:
        for model_object_tag in self.model_object_tags.itervalues():
            model_object_tag.value.initstate(**model_object_tag.state)


def load_from_file(f):
    content_handler = ZMLHandler()
    f.seek(0)
    xml.sax.parse(f, content_handler)
    root = content_handler.root
    for node in root:
        if isinstance(node, ParentMixin):
            node.reparent()
    return root


def load_from_string(s):
    content_handler = ZMLHandler()
    xml.sax.parseString(s, content_handler)
    root = content_handler.root
    for node in root:
        if isinstance(node, ParentMixin):
            node.reparent()
    return root


