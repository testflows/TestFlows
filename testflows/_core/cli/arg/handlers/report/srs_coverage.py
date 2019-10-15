# Copyright 2019 Vitaliy Zakaznikov (TestFlows Test Framework http://testflows.com)
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
import functools
import testflows._core.cli.arg.type as argtype

from testflows._core.cli.colors import color
from testflows._core.cli.arg.common import epilog
from testflows._core.cli.arg.common import HelpFormatter
from testflows._core.cli.arg.handlers.handler import Handler as HandlerBase
from testflows._core.document.srs import Parser, visit_parse_tree
from testflows._core.document.toc import Visitor as VisitorBase
from testflows._core.transform.log.pipeline import ResultsLogPipeline
from testflows._core.utils.timefuncs import strftimedelta

def color_secondary():
    return functools.partial(color, color="white", attrs=["dim"])

def color_primary():
    return functools.partial(color, color="white")

def result_priority(result):
    if result.startswith("X"):
        return 2
    elif result == "OK":
        return 1
    elif result == "Skip":
        return 3
    # Error, Fail, Null
    return 4

def color_result(result):
    if result.startswith("X"):
        return functools.partial(color, color="blue", attrs=["bold"])
    elif result == "OK":
        return functools.partial(color, color="green", attrs=["bold"])
    elif result == "Skip":
        return functools.partial(color, color="cyan", attrs=["bold"])
    # Error, Fail, Null
    return functools.partial(color, color="red", attrs=["bold"])

def color_counts(result):
    if result == "Satisfied":
        return functools.partial(color, color="green", attrs=["bold"])
    elif result == "Unsatisfied":
        return functools.partial(color, color="grey", attrs=["bold"])
    # Unverified
    return functools.partial(color, color="red", attrs=["bold"])

class Counts(object):
    def __init__(self, name, units, ok, nok, untested):
        self.name = name
        self.units = units
        self.ok = ok
        self.nok = nok
        self.untested = untested

    def __bool__(self):
        return self.units > 0

    def __str__(self):
        s = f"{self.units} {self.name if self.units != 1 else self.name.rstrip('s')} ("
        s = color(s, "white", attrs=["bold"])
        r = []
        if self.ok > 0:
            r.append(color_counts("Satisfied")(f"{self.ok} satisfied {(self.ok / self.units) * 100:.1f}%"))
        if self.nok > 0:
            r.append(color_counts("Unsatisfied")(f"{self.nok} unsatisfied {(self.nok / self.units) * 100:.1f}%"))
        if self.untested > 0:
            r.append(color_counts("Untested")(f"{self.untested} untested {(self.untested / self.units) * 100:.1f}%"))
        s += color(", ", "white", attrs=["bold"]).join(r)
        s += color(")\n", "white", attrs=["bold"])
        return s

class Heading(object):
    def __init__(self, name, level, num):
        self.name = name
        self.level = level
        self.num = num

class Requirement(Heading):
    def __init__(self, name, version, uid, level, num):
        self.version = version
        self.uid = uid
        return super(Requirement, self).__init__(name, level, num)

class Visitor(VisitorBase):
    def __init__(self, *args, **kwargs):
        self.headings = []
        super(Visitor, self).__init__(*args, **kwargs)

    def visit_line(self, node, children):
        pass

    def visit_requirement(self, node, children):
        name = node.requirement_heading.requirement_name.value
        description = None
        uid = None
        version = None
        try:
            uid = f"\"{node.uid.word}\""
        except:
            pass
        try:
            version = f"\"{node.version.word}\""
        except:
            pass
        res = self.process_heading(node, children)
        if res:
            level, num = res
            self.headings.append(Requirement(name, version, uid, level, num))

    def visit_heading(self, node, children):
        res = self.process_heading(node, children)
        if res:
            level, num = res
            name = node.heading_name.value
            self.headings.append(Heading(name, level, num))

    def visit_document(self, node, children):
        return self.headings

class Handler(HandlerBase):
    @classmethod
    def add_command(cls, commands):
        parser = commands.add_parser("srs-coverage", help="SRS (Software Requirements Specification) coverage report", epilog=epilog(),
            description="Generate SRS (Software Requirements Specification) coverage report.",
            formatter_class=HelpFormatter)

        parser.add_argument("srs", metavar="srs", type=argtype.file("r", bufsize=1, encoding="utf-8"),
                nargs=1, help="source file")
        parser.add_argument("input", metavar="input", type=argtype.file("r", bufsize=1, encoding="utf-8"),
                nargs="?", help="input log, default: stdin", default="-")
        parser.add_argument("output", metavar="output", type=argtype.file("w", bufsize=1, encoding="utf-8"),
                nargs="?", help='output file, default: stdout', default="-")
        parser.add_argument("--only", metavar="status", type=str, nargs="+", help="verification status",
            choices=["satisfied", "unsatisfied", "untested"],
            default=["satisfied", "unsatisfied", "untested"])
        parser.set_defaults(func=cls())

    def generate(self, output, headings, tested, only):
        counts = Counts("requirements", *([0] * 4))

        for heading in headings:
            counts.units += 1
            indent = "  " * (heading.level - 1)
            if isinstance(heading, Requirement):
                if tested.get(heading.name) is None:
                    counts.untested += 1
                    if "untested" in only:
                        output.write(color(f"{indent}\u270E ", "grey", attrs=["bold"]) + color_primary()(f"{heading.num} {heading.name}\n"))
                        output.write(color(f"{indent}  no tests\n", "white", attrs=["dim"]))
                else:
                    _tests = []
                    _color = None
                    _priority = 0
                    for test, result in tested.get(heading.name):
                        _tests.append(f"{indent}  [ {color_result(result.name)(result.name)} ] "
                            f"{color_secondary()(strftimedelta(result.p_time))} "
                            f"{color_secondary()(test.name)}\n")
                        if result_priority(result.name) > _priority:
                            _color = color_result(result.name)
                            _priority = result_priority(result.name)
                    icon = "\u2714"
                    _include = True
                    if _priority > 2:
                        icon = "\u2718"
                        counts.nok += 1
                        if "unsatisfied" not in only:
                            _include = False
                    else:
                        if "satisfied" not in only:
                            _include = False
                        counts.ok += 1

                    if _include:
                        output.write(_color(f"{indent}{icon} ") + color_primary()(f"{heading.num} {heading.name}\n") + "".join(_tests))

            else:
                output.write(color(f"{indent}\u27e5 {heading.num} {heading.name}\n", "white", attrs=["dim"]))

        # print summary
        output.write(f"\n{counts}\n")

    def handle(self, args):
        parser = Parser()
        with args.srs[0] as requirements:
            requirements_data = requirements.read()

        tree = parser.parse(requirements_data)
        headings = visit_parse_tree(tree, Visitor())
        results = {}
        ResultsLogPipeline(args.input, results).run()
        # map result requirements to tests
        tested = {}
        for result in results:
            test, result = results[result].values()
            for req in test.requirements:
                if tested.get(req.name) is None:
                    tested[req.name] = []
                tested[req.name].append((test, result))
        # generate report
        with args.output as output:
            self.generate(output, headings, tested, args.only)

