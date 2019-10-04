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
from testflows._core.transform.log import message
from testflows._core.cli.colors import color

width = 70
count = 0

def color_result(result):
    if result.startswith("X"):
        return color(".", "blue", attrs=["bold"])
    elif result == "OK":
        return color(".", "green", attrs=["bold"])
    elif result == "Skip":
        return color("-", "white", attrs=["dim"])
    # Error, Fail, Null
    elif result == "Error":
        return color("E", "yellow", attrs=["bold"])
    elif result == "Fail":
         return color("F", "red", attrs=["bold"])
    elif result == "Null":
        return color("N", "magenta", attrs=["bold"])
    else:
        raise ValueError(f"unknown result {result}")

def format_result(msg, result):
    global count
    flags = Flags(msg.p_flags)
    if flags & SKIP and settings.show_skipped is False:
        return

    count += 1
    _result = f"\b{color_result(result)} "
    # wrap if we hit max width
    if count >= width:
        count = 0
        _result += "\n"

    return _result

formatters = {
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

def transform(stop_event):
    """Transform parsed log line into a short format.
    """
    n = 0
    line = None
    progress = ["\\", "|", "/"]
    while True:
        if line is not None:
            formatter = formatters.get(type(line), None)
            if formatter:
                line = formatter[0](line, *formatter[1:])
                n = 0
            else:
                line = "\b" + color(progress[n % 3], "white", attrs=["dim"])
                n += 1

        if stop_event.is_set():
            if line is None:
                line = ""
            line += "\n"
        line = yield line