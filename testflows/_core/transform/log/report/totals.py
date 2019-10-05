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
import testflows.settings as settings

from testflows._core.flags import Flags, SKIP
from testflows._core.testtype import TestType, TestSubType
from testflows._core.transform.log import message
from testflows._core.utils.timefuncs import strftimedelta
from testflows._core.cli.colors import color

def color_line(line):
    return color(line, "white", attrs=["dim"])

def color_result(result, text):
    if result.startswith("X"):
        return color(text, "blue", attrs=["bold"])
    elif result == "OK":
        return color(text, "green", attrs=["bold"])
    elif result == "Skip":
        return color(text, "white", attrs=["dim"])
    # Error, Fail, Null
    elif result == "Error":
        return color(text, "yellow", attrs=["bold"])
    elif result == "Fail":
         return color(text, "red", attrs=["bold"])
    elif result == "Null":
        return color(text, "magenta", attrs=["bold"])
    else:
        raise ValueError(f"unknown result {result}")

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
        s = f"{self.units} {self.name if self.units != 1 else self.name.rstrip('s')} ("
        s = color(s, "white", attrs=["bold"])
        r = []
        if self.ok > 0:
            r.append(color_result("OK", f"{self.ok} ok"))
        if self.fail > 0:
            r.append(color_result("Fail", f"{self.fail} failed"))
        if self.skip > 0:
            r.append(color_result("Skip", f"{self.skip} skipped"))
        if self.error > 0:
            r.append(color_result("Error", f"{self.error} errored"))
        if self.null > 0:
            r.append(color_result("Null", f"{self.null} null"))
        if self.xok > 0:
            r.append(color_result("XOK", f"{self.xok} xok"))
        if self.xfail > 0:
            r.append(color_result("XFail", f"{self.xfail} xfail"))
        if self.xerror > 0:
            r.append(color_result("XError", f"{self.xerror} xerror"))
        if self.xnull > 0:
            r.append(color_result("XNull", f"{self.xnull} xnull"))
        s += color(", ", "white", attrs=["bold"]).join(r)
        s += color(")\n", "white", attrs=["bold"])
        return s

def format_test(msg, counts):
    flags = Flags(msg.p_flags)
    if flags & SKIP and settings.show_skipped is False:
        return
    if msg.p_type == TestType.Module:
        counts["module"].units += 1
    elif msg.p_type == TestType.Suite:
        counts["suite"].units += 1
    elif msg.p_type == TestType.Step:
        counts["step"].units += 1
    else:
        if msg.p_subtype == TestSubType.Feature:
            counts["feature"].units += 1
        elif msg.p_subtype == TestSubType.Scenario:
            counts["scenario"].units += 1
        else:
            counts["test"].units += 1

def format_result(msg, counts):
    if Flags(msg.p_flags) & SKIP and settings.show_skipped is False:
        return

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
        if msg.p_subtype == TestSubType.Feature:
            setattr(counts["feature"], _name, getattr(counts["feature"], _name) + 1)
        elif msg.p_subtype == TestSubType.Scenario:
            setattr(counts["scenario"], _name, getattr(counts["scenario"], _name) + 1)
        else:
            setattr(counts["test"], _name, getattr(counts["test"], _name) + 1)

formatters = {
    message.RawTest: (format_test,),
    message.RawResultOK: (format_result,),
    message.RawResultFail: (format_result,),
    message.RawResultError: (format_result,),
    message.RawResultSkip: (format_result,),
    message.RawResultNull: (format_result,),
    message.RawResultXOK: (format_result,),
    message.RawResultXFail: (format_result,),
    message.RawResultXError: (format_result,),
    message.RawResultXNull: (format_result,)
}

def transform(stop):
    """Totals report.

    :param stop: stop event
    """
    counts = {
        "module": Counts("modules", *([0] * 10)),
        "suite": Counts("suites", *([0] * 10)),
        "test": Counts("tests", *([0] * 10)),
        "step": Counts("steps", *([0] * 10)),
        "feature": Counts("features", *([0] * 10)),
        "scenario": Counts("scenarios", *([0] * 10))
    }
    line = None

    while True:
        if line is not None:
            msg = line
            formatter = formatters.get(type(line), None)
            if formatter:
                formatter[0](line, *formatter[1:], counts=counts)
            line = None

            if stop.is_set():
                if line is None:
                    line = ""
                line += "\n"
                line_icon = "" #"\u27a4 "
                if counts["module"]:
                    line += line_icon + str(counts["module"])
                if counts["suite"]:
                    line += line_icon + str(counts["suite"])
                if counts["test"]:
                    line += line_icon + str(counts["test"])
                if counts["feature"]:
                    line += line_icon + str(counts["feature"])
                if counts["scenario"]:
                    line += line_icon + str(counts["scenario"])
                if counts["step"]:
                    line += line_icon + str(counts["step"])
                line += color_line(f"\nTotal time {strftimedelta(msg.p_time)}\n")
        line = yield line