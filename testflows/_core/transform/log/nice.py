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

import testflows.settings as settings

from testflows._core.flags import Flags, SKIP
from testflows._core.testtype import TestType, TestSubType
from testflows._core.transform.log import message
from testflows._core.utils.timefuncs import strftime, strftimedelta
from testflows._core.utils.timefuncs import localfromtimestamp
from testflows._core.name import split, basename
from testflows._core.cli.colors import color, cursor_up

strip_nones = re.compile(r'( None)+$')
indent = " " * 2

def color_keyword(keyword):
    return color(split(keyword)[-1], "white", attrs=["bold"])

def color_secondary_keyword(keyword):
    return color(split(keyword)[-1], "white", attrs=["bold", "dim"])

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

def format_input(msg, keyword):
    flags = Flags(msg.p_flags)
    if flags & SKIP and settings.show_skipped is False:
        return
    out = color_other(f"{strftimedelta(msg.p_time):>20}{'':3}{indent * (msg.p_id.count('/') - 1)}{keyword}")
    out += color("\u270b " + msg.message, "yellow", attrs=["bold"]) + cursor_up() + "\n"
    return out

def format_description(msg, indent):
    first, rest = msg.description.description.split("\n", 1)
    first = first.strip()
    if first:
        first += "\n"
    desc = f"{first.strip()}{textwrap.dedent(rest.rstrip())}"
    desc = textwrap.indent(desc, indent + "  ")
    desc = color(desc, "white", attrs=["dim"])
    return desc + "\n"

def format_requirements(msg, indent):
    out = [f"{indent}{' ' * 2}{color_secondary_keyword('Requirements')}"]
    for req in msg.requirements:
        out.append(color(f"{indent}{' ' * 4}{req.name}", "white", attrs=["dim"]))
        out.append(color(f"{indent}{' ' * 6}version {req.version}", "white", attrs=["dim"]))
    return "\n".join(out) + "\n"

def format_attributes(msg, indent):
    out = [f"{indent}{' ' * 2}{color_secondary_keyword('Attributes')}"]
    for attr in msg.attributes:
        out.append(color(f"{indent}{' ' * 4}{attr.name}", "white", attrs=["dim"]))
        out.append(color(f"{indent}{' ' * 6}{attr.value}", "white", attrs=["dim"]))
    return "\n".join(out) + "\n"

def format_tags(msg, indent):
    out = [f"{indent}{' ' * 2}{color_secondary_keyword('Tags')}"]
    for tag in msg.tags:
        out.append(color(f"{indent}{' ' * 4}{tag.value}", "white", attrs=["dim"]))
    return "\n".join(out) + "\n"

def format_arguments(msg, indent):
    out = [f"{indent}{' ' * 2}{color_secondary_keyword('Arguments')}"]
    for arg in msg.args:
        out.append(color(f"{indent}{' ' * 4}{arg.name}", "white", attrs=["dim"]))
        out.append(color(f"{indent}{' ' * 6}{arg.value}", "white", attrs=["dim"]))
    return "\n".join(out) + "\n"

def format_users(msg, indent):
    out = [f"{indent}{' ' * 2}{color_secondary_keyword('Users')}"]
    for user in msg.users:
        out.append(color(f"{indent}{' ' * 4}{user.name}", "white", attrs=["dim"]))
    return "\n".join(out) + "\n"

def format_tickets(msg, indent):
    out = [f"{indent}{' ' * 2}{color_secondary_keyword('Tickets')}"]
    for ticket in msg.tickets:
        out.append(color(f"{indent}{' ' * 4}{ticket.name}", "white", attrs=["dim"]))
    return "\n".join(out) + "\n"

def format_test(msg, keyword):
    flags = Flags(msg.p_flags)
    if flags & SKIP and settings.show_skipped is False:
        return
    if msg.p_type == TestType.Module:
        keyword += "Module"
    elif msg.p_type == TestType.Suite:
        keyword += "Suite"
    elif msg.p_type == TestType.Step:
        if msg.p_subtype == TestSubType.Given:
            keyword += "Given"
        elif msg.p_subtype == TestSubType.When:
            keyword += "When"
        elif msg.p_subtype == TestSubType.Then:
            keyword += "Then"
        else:
            keyword += "Step"
    else:
        if msg.p_subtype == TestSubType.Feature:
            keyword += "Feature"
        elif msg.p_subtype == TestSubType.Scenario:
            keyword += "Scenario"
        elif msg.p_subtype == TestSubType.Background:
            keyword += "Background"
        else:
            keyword += "Test"

    started = strftime(localfromtimestamp(msg.started))
    _keyword = color_keyword(keyword)
    _name = color_other(split(msg.name)[-1])
    _indent = f"{started:>20}" + f"{'':3}{indent * (msg.p_id.count('/') - 1)}"
    out = f"{color_other(_indent)}{_keyword} {_name}{color_other(', flags:' + str(flags) if flags else '')}\n"
    # convert indent to just spaces
    _indent = len(_indent) * " "
    if msg.description:
        out += format_description(msg, _indent)
    if msg.tags:
        out += format_tags(msg, _indent)
    if msg.requirements:
        out += format_requirements(msg, _indent)
    if msg.attributes:
        out += format_attributes(msg, _indent)
    if msg.users:
        out += format_users(msg, _indent)
    if msg.tickets:
        out += format_tickets(msg, _indent)
    if msg.args:
        out += format_arguments(msg, _indent)
    return out

def format_result(msg, prefix, result):
    if Flags(msg.p_flags) & SKIP and settings.show_skipped is False:
        return
    _result = color_result(prefix, result)
    _test = color_other(basename(msg.test))

    return (color_other(f"{strftimedelta(msg.p_time):>20}") +
        f"{'':3}{indent * (msg.p_id.count('/') - 1)}{_result} "
        f"{_test}{color_other(', ' + msg.test)}{color_other((', ' + msg.message) if msg.message else '')}"
        f"{color_other((', ' + msg.reason) if msg.reason else '')}\n")

def format_other(msg, keyword):
    if Flags(msg.p_flags) & SKIP and settings.show_skipped is False:
        return
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
    message.RawInput: (format_input, f"{mark} "),
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
    line = None

    while True:
        if line is not None:
            msg = line
            formatter = formatters.get(type(line), None)
            if formatter:
                line = formatter[0](line, *formatter[1:])
            else:
                line = None

        line = yield line
