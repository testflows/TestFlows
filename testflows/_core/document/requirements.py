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
from testflows.contrib.arpeggio import RegExMatch as _
from testflows.contrib.arpeggio import OneOrMore, EOF
from testflows.contrib.arpeggio import ParserPython as PEGParser
from testflows.contrib.arpeggio import PTNodeVisitor, visit_parse_tree

from testflows.core import Requirement

template = """
%(pyname)s = Requirement(
        name=%(name)s,
        revision=%(revision)s,
        description=%(description)s,
        link=%(link)s
    )
"""

class Visitor(PTNodeVisitor):
    def __init__(self, *args, **kwargs):
        self.output = "# Auto generated requirements"
        super(Visitor, self).__init__(*args, **kwargs)

    def visit_line(self, node, children):
        pass

    def visit_requirement(self, node, children):
        pass

    def document(self, node, children):
        return self.output

def Parser():
    """Returns markdown requirements parser.
    """
    def line():
        return _(r".*")

    def heading():
        return [
            (_(r"\n\s{0:3}#[\s]+"), name, _(r"\n")),
            (name, _(r"\n[-=]+\n)"))
            ]

    def name():
        return _(r"RQ\.*.+")

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
        return heading, OneOrMore(version, priority, type, group, uid), _(r"\n")

    def document():
        return OneOrMore(requirement, line), EOF

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

    destination.write(destination_data)
