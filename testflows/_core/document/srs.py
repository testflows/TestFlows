# Copyright 2019 Vitaliy Zakaznikov, TestFlows Test Framework (http://testflows.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import re

from testflows._core.contrib.arpeggio import RegExMatch as _
from testflows._core.contrib.arpeggio import OneOrMore, ZeroOrMore, EOF, Optional, Not
from testflows._core.contrib.arpeggio import ParserPython as PEGParser
from testflows._core.contrib.arpeggio import PTNodeVisitor, visit_parse_tree

template = """
%(pyname)s = Requirement(
        name='%(name)s',
        version='%(version)s',
        priority=%(priority)s,
        group=%(group)s,
        type=%(type)s,
        uid=%(uid)s,
        description=%(description)s,
        link=%(link)s
    )

"""

class Visitor(PTNodeVisitor):
    def __init__(self, *args, **kwargs):
        self.output = (
            "# These are auto generated requirements from an SRS document.\n"
            "# Do not edit by hand but re-generate instead\n"
            "# using \"tfs requirement generate\" command.\n"
            "#\n"
            "from testflows.core import Requirement\n\n"
            )
        self.pyname_fmt = re.compile(r"[^a-zA-Z0-9]")
        super(Visitor, self).__init__(*args, **kwargs)

    def visit_line(self, node, children):
        pass

    def visit_requirement(self, node, children):
        name = node.requirement_heading.requirement_name.value
        pyname = re.sub(r"_+", "_", self.pyname_fmt.sub("_", name))
        description = None
        group = None
        priority = None
        type = None
        uid = None
        link = None

        try:
            description = "\n".join([f'{"":8}{repr(line.value)}' for lines in node.requirement_description for line in lines])
            description = f"(\n{description}\n{'':8})"
        except:
            pass
        try:
            priority = node.priority.word
        except:
            pass
        try:
            group = f"\"{node.group.word}\""
        except:
            pass
        try:
            type = f"\"{node.type.word}\""
        except:
            pass
        try:
            uid = f"\"{node.uid.word}\""
        except:
            pass

        self.output += template.lstrip() % {
            "pyname": pyname,
            "name": node.requirement_heading.requirement_name.value,
            "version": node.version.word,
            "description": str(description),
            "priority": str(priority),
            "group": str(group),
            "type": str(type),
            "uid": str(uid),
            "link": str(link)
        }

    def visit_document(self, node, children):
        return self.output.rstrip() + "\n"

def Parser():
    """Returns markdown requirements parser.
    """
    def line():
        return _(r"[^\n]*\n")

    def not_heading():
        return Not(heading)

    def heading():
        return [
            (_(r"\s?\s?\s?#+\s+"), heading_name, _(r"\n?")),
            (heading_name, _(r"[-=]+\n?"))
        ]

    def requirement_heading():
        return [
            (_(r"\s?\s?\s?#+\s+"), requirement_name, _(r"\n?")),
            (requirement_name, _(r"[-=]+\n?"))
        ]

    def heading_name():
        return _(r"[^\n]+")

    def requirement_name():
        return _(r"RQ\.[^\n]+")

    def requirement_description():
        return ZeroOrMore((not_heading, line))

    def word():
        return _(r"[^\s]+")

    def version():
        return _(r"\s*version:\s*"), word

    def priority():
        return _(r"\s*priority:\s*"), word

    def type():
        return _(r"\s*type:\s*"), word

    def group():
        return _(r"\s*group:\s*"), word

    def uid():
        return _(r"\s*uid:\s*"), word

    def requirement():
        return requirement_heading, version, ZeroOrMore([priority, type, group, uid]), Optional(requirement_description), _(r"\n?")

    def document():
        return Optional(OneOrMore([requirement, heading, line])), EOF

    return PEGParser(document)


def generate(source, destination):
    """Generate requirements from markdown source.

    :param source: source file-like object
    :param destination: destination file-like object
    """
    parser = Parser()
    source_data = source.read()
    tree = parser.parse(source_data)
    destination_data = visit_parse_tree(tree, Visitor())
    if destination_data:
        destination.write(destination_data)
