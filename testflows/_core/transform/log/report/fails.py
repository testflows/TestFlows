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
import testflows.settings as settings

from testflows._core.flags import Flags, SKIP
from testflows._core.testtype import TestType
from testflows._core.transform.log import message
from testflows._core.name import split
from testflows._core.cli.colors import color

indent = " " * 2

def color_result(result, attrs=None):
    if attrs is None:
        attrs = ["bold"]
    if result.startswith("X"):
        return functools.partial(color, color="blue", attrs=attrs)
    elif result == "OK":
        return functools.partial(color, color="green", attrs=attrs)
    elif result == "Skip":
        return functools.partial(color, color="cyan", attrs=attrs)
    # Error, Fail, Null
    elif result == "Error":
        return functools.partial(color, color="yellow", attrs=attrs)
    elif result == "Fail":
        return functools.partial(color, color="red", attrs=attrs)
    elif result == "Null":
        return functools.partial(color, color="magenta", attrs=attrs)
    else:
        raise ValueError(f"unknown result {result}")

def add_result(msg, results, result):
    flags = Flags(msg.p_flags)
    if flags & SKIP and settings.show_skipped is False:
        return
    if not result in ("OK", "Skip"):
        results[msg.p_id] = (msg, result)

processors = {
    message.RawResultOK: (add_result, f"OK"),
    message.RawResultFail: (add_result, f"Fail"),
    message.RawResultError: (add_result, f"Error"),
    message.RawResultSkip: (add_result, f"Skip"),
    message.RawResultNull: (add_result, f"Null"),
    message.RawResultXOK: (add_result, f"XOK"),
    message.RawResultXFail: (add_result, f"XFail"),
    message.RawResultXError: (add_result, f"XError"),
    message.RawResultXNull: (add_result, f"XNull")
}

def generate(results):
    """Generate report"""
    if not results:
        return

    xfails = ""
    fails = ""

    for entry in results:
        msg, result = results[entry]
        _color = color_result(result)
        if not result.startswith("X"):
            continue
        xfails += _color('\u2718') + f" [ { _color(result) } ] {msg.test}\n"

    if xfails:
        xfails = color("\nKnown failing tests\n\n", "white", attrs=["bold"]) + xfails

    for entry in results:
        msg, result = results[entry]
        _color = color_result(result)
        if result.startswith("X"):
            continue
        fails += _color("\u2718") + f" [ {_color(result)} ] {msg.test}\n"
    if fails:
        fails = color("\nFailing tests\n\n", "white", attrs=["bold"]) + fails

    report = f"{xfails}{fails}"

    return report or None

def transform(stop):
    """Transform parsed log line into a short format.
    """
    line = None
    results = {}
    while True:
        if line is not None:
            processor = processors.get(type(line), None)
            if processor:
                processor[0](line, results, *processor[1:])
            if stop.is_set():
                line = generate(results)
            else:
                line = None
        line = yield line