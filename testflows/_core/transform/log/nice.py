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
import re
import textwrap

from testflows._core.flags import Flags
from testflows._core.testtype import TestType
from testflows._core.transform.log import message
from testflows._core.utils.timefuncs import strftime, strftimedelta
from testflows._core.utils.timefuncs import localfromtimestamp
from testflows._core.name import split
from testflows._core.cli.colors import color
from testflows._core import __version__

strip_nones = re.compile(r'( None)+$')
indent = " " * 2

class Counts(object):
    def __init__(self, name, units, ok, fail, skip, error, null, xok, xfail, xerror, xnull):
        self.name = name
        self.units = units
        self.ok = ok
        self.fail = fail
        self.skip = skip
        self.error = error
        self.null = null
        self.xok = xok
        self.xfail = xfail
        self.xerror = xerror
        self.xnull = xnull

    def __bool__(self):
        return self.units > 0

    def __str__(self):
        s = f"{self.name} {self.units}"
        if self.ok > 0:
            s += f" ok {self.ok}"
        if self.fail > 0:
            s += f" fail {self.fail}"
        if self.skip > 0:
            s += f" skip {self.skip}"
        if self.error > 0:
            s += f" error {self.error}"
        if self.null > 0:
            s += f" null {self.null}"
        if self.xok > 0:
            s += f" xok {self.xok}"
        if self.xfail > 0:
            s += f" xfail {self.xfail}"
        if self.xerror > 0:
            s += f" xerror {self.xerror}"
        if self.xnull > 0:
            s += f" xnull {self.xnull}"
        return s + "\n"

def color_keyword(keyword):
    return color(split(keyword)[-1], "white", attrs=["bold"])

def color_other(other):
    return color(other, "white", attrs=["dim"])

def color_result(prefix, result):
    if result.startswith("X"):
        return color(prefix + result, "blue", attrs=["bold"])
    elif result.endswith("OK"):
        return color(prefix + result, "green", attrs=["bold"])
    elif result.endswith("Skip"):
        return color(prefix + result, "cyan", attrs=["bold"])
    # Error, Fail, Null
    return color(prefix + result, "red", attrs=["bold"])

def format_test(msg, keyword, counts):
    flags = Flags(msg.flags)

    if msg.p_type == TestType.Module:
        keyword += "Module"
        counts["module"].units += 1
    elif msg.p_type == TestType.Suite:
        keyword += "Suite"
        counts["suite"].units += 1
    elif msg.p_type == TestType.Step:
        keyword += "Step"
        counts["step"].units += 1
    else:
        keyword += "Test"
        counts["test"].units += 1

    started = strftime(localfromtimestamp(msg.started))
    _keyword = color_keyword(keyword)
    _name = color_other(split(msg.name)[-1])
    out = color_other(f"{started:>20}") + f"{'':3}{indent * (msg.p_id.count('/') - 1)}{_keyword} {_name}{color_other(', flags:' + str(flags) if flags else '')}\n"
    return out

def format_result(msg, prefix, result, counts):
    _result = color_result(prefix, result)
    _test = color_other(split(msg.test)[-1])

    _result_name_map = {
        message.RawResultOK: "ok",
        message.RawResultFail: "fail",
        message.RawResultNull: "null",
        message.RawResultError: "error",
        message.RawResultXOK: "xok",
        message.RawResultXFail: "xfail",
        message.RawResultXNull: "xnull",
        message.RawResultXError: "xerror",
        message.RawResultSkip: "skip"
    }

    _name = _result_name_map[type(msg)]

    if msg.p_type == TestType.Module:
        setattr(counts["module"], _name, getattr(counts["module"], _name) + 1)
    elif msg.p_type == TestType.Suite:
        setattr(counts["suite"], _name, getattr(counts["suite"], _name) + 1)
    elif msg.p_type == TestType.Step:
        setattr(counts["step"], _name, getattr(counts["step"], _name) + 1)
    else:
        setattr(counts["test"], _name, getattr(counts["test"], _name) + 1)

    return (color_other(f"{strftimedelta(msg.p_time):>20}") +
        f"{'':3}{indent * (msg.p_id.count('/') - 1)}{_result} "
        f"{_test}{color_other((', ' + msg.message) if msg.message else '')}"
        f"{color_other((', ' + msg.reason) if msg.reason else '')}\n")

def format_other(msg, keyword, counts):
    fields = ' '.join([str(f) for f in msg[message.Prefix.time + 1:]])
    if msg.p_stream:
        fields = f"[{msg.p_stream}] {fields}"
    fields = strip_nones.sub("", fields)

    fields = textwrap.indent(fields, prefix=(indent * (msg.p_id.count('/') - 1) + " " * 30))
    fields = fields.lstrip(" ")

    return color_other(f"{strftimedelta(msg.p_time):>20}{'':3}{indent * (msg.p_id.count('/') - 1)}{keyword} {fields}\n")

mark = "\u27e5"
result_mark = "\u27e5\u27e4"

formatters = {
    message.RawTest: (format_test, f"{mark}  "),
    message.RawDescription: (format_other, f"{mark}    :"),
    message.RawArgument: (format_other, f"{mark}    @"),
    message.RawAttribute: (format_other, f"{mark}    -"),
    message.RawRequirement: (format_other, f"{mark}    ?"),
    message.RawValue: (format_other, f"{mark}    ="),
    message.RawException: (format_other, f"{mark}    Exception:"),
    message.RawNote: (format_other, f"{mark}    [note]"),
    message.RawDebug: (format_other, f"{mark}    [debug]"),
    message.RawTrace: (format_other, f"{mark}    [trace]"),
    message.RawNone: (format_other, "    "),
    message.RawResultOK: (format_result, f"{result_mark} ", "OK"),
    message.RawResultFail: (format_result, f"{result_mark} ", "Fail"),
    message.RawResultError: (format_result, f"{result_mark} ", "Error"),
    message.RawResultSkip: (format_result, f"{result_mark} ", "Skip"),
    message.RawResultNull: (format_result, f"{result_mark} ", "Null"),
    message.RawResultXOK: (format_result, f"{result_mark} ", "XOK"),
    message.RawResultXFail: (format_result, f"{result_mark} ", "XFail"),
    message.RawResultXError: (format_result, f"{result_mark} ", "XError"),
    message.RawResultXNull: (format_result, f"{result_mark} ", "XNull")
}

def transform(stop):
    """Transform parsed log line into a nice format.

    :param stop: stop event
    """
    counts = {
        "module": Counts("modules", *([0] * 10)),
        "suite": Counts("suites", *([0] * 10)),
        "test": Counts("tests", *([0] * 10)),
        "step": Counts("steps", *([0] * 10))
    }
    n = 0
    line = None
    divider = "\u2500" * 20

    while True:
        if line is not None:
            msg = line
            formatter = formatters.get(type(line), None)
            if formatter:
                line = formatter[0](line, *formatter[1:], counts=counts)
            else:
                line = None

            if n < 1:
                line = color_other(f"TestFlows Test Framework v{__version__}\n{divider}\n") + line

            if stop.is_set():
                0
                line_icon = "\u27a4 "
                line += color_other(f"{divider}\n")
                if counts["module"]:
                    line += color_other(line_icon + str(counts["module"]))
                if counts["suite"]:
                    line += color_other(line_icon + str(counts["suite"]))
                if counts["test"]:
                    line += color_other(line_icon + str(counts["test"]))
                if counts["step"]:
                    line += color_other(line_icon + str(counts["step"]))
                line += color_other(f"\nTotal time {strftimedelta(msg.p_time)}\n")
            n += 1
        line = yield line
