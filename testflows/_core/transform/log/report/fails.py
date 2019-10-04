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
from testflows._core.testtype import TestType
from testflows._core.transform.log import message
from testflows._core.name import split
from testflows._core.cli.colors import color

indent = " " * 2

def color_result(result, text):
    if result.startswith("X"):
        return color(text, "blue", attrs=["bold"])
    elif result == "OK":
        return color(text, "green", attrs=["bold"])
    elif result == "Skip":
        return color(text, "cyan", attrs=["bold"])
    # Error, Fail, Null
    elif result == "Error":
        return color("\u2718 " + text, "yellow", attrs=["bold"])
    elif result == "Fail":
         return color("\u2718 " + text, "red", attrs=["bold"])
    elif result == "Null":
        return color("\u2718 " + text, "magenta", attrs=["bold"])
    else:
        raise ValueError(f"unknown result {result}")

def format_test(msg, keyword):
    flags = Flags(msg.p_flags)
    if flags & SKIP and settings.show_skipped is False:
        return

    if msg.p_type == TestType.Module:
        keyword += "Module"
    elif msg.p_type == TestType.Suite:
        keyword += "Suite"
    elif msg.p_type == TestType.Step:
        keyword += "Step"
    else:
        keyword += "Test"

    _keyword = color_keyword(keyword)
    _name = color_test_name(split(msg.name)[-1])
    return f"{indent * (msg.p_id.count('/') - 1)}{_keyword} {_name}\n"

def add_result(msg, results, result):
    flags = Flags(msg.p_flags)
    if flags & SKIP and settings.show_skipped is False:
        return
    if not result.startswith("X") and not result in ("OK", "Skip"):
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
    report = color("\nFailing tests\n\n", "red", attrs=["bold"])
    for entry in results:
        msg, result = results[entry]
        report += f"{color_result(result, result + ' ' + msg.test)}\n"
    return report

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