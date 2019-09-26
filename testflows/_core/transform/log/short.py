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

def color_keyword(keyword):
    return color(split(keyword)[-1], "white", attrs=["bold"])

def color_test_name(name):
    return color(split(name)[-1], "white", attrs=["dim"])

def color_result(result):
    if result.startswith("X"):
        return color(result, "blue", attrs=["bold"])
    elif result == "OK":
        return color(result, "green", attrs=["bold"])
    elif result == "Skip":
        return color(result, "cyan", attrs=["bold"])
    # Error, Fail, Null
    return color(result, "red", attrs=["bold"])

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

def format_result(msg, result):
    flags = Flags(msg.p_flags)
    if flags & SKIP and settings.show_skipped is False:
        return

    _result = color_result(result)
    return f"{indent * (msg.p_id.count('/') - 1)}{_result}\n"

formatters = {
    message.RawTest: (format_test, f""),
    message.RawResultOK: (format_result, f"OK"),
    message.RawResultFail: (format_result, f"Fail"),
    message.RawResultError: (format_result, f"Error"),
    message.RawResultSkip: (format_result, f"Skip"),
    message.RawResultNull: (format_result, f"Null"),
    message.RawResultXOK: (format_result, f"XOK"),
    message.RawResultXFail: (format_result, f"XFail"),
    message.RawResultXError: (format_result, f"XError"),
    message.RawResultXNull: (format_result, f"XNull")
}

def transform():
    """Transform parsed log line into a short format.
    """
    line = None
    while True:
        if line is not None:
            formatter = formatters.get(type(line), None)
            if formatter:
                line = formatter[0](line, *formatter[1:])
            else:
                line = None
        line = yield line