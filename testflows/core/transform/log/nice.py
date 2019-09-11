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

from testflows.core import Message
from testflows.core import Flags
from testflows.core.transform.log import message
from testflows.core.utils.timefuncs import strftime, strftimedelta
from testflows.core.utils.timefuncs import localfromtimestamp

strip_nones = re.compile(r'( None)+$')
indent = " " * 2

def format_test(msg, keyword):
    started = strftime(localfromtimestamp(msg.started))
    return f"{started:>20}{'':3}{indent * (msg.p_id.count('/') - 1)}{keyword} {msg.name} {Flags(msg.flags)}\n"

def format_result(msg, result):
    return f"{strftimedelta(msg.p_time):>20}{'':3}{indent * (msg.p_id.count('/') - 1)}{result} {msg.test}\n"

def format_other(msg, keyword):
    fields = ' '.join([str(f) for f in msg[message.Prefix.time + 1:]])
    if msg.p_stream:
        fields = f"[{msg.p_stream}] {fields}"
    fields = strip_nones.sub("", fields)

    fields = textwrap.indent(fields, prefix=(indent * (msg.p_id.count('/') - 1) + " " * 30))
    fields = fields.lstrip(" ")

    return f"{strftimedelta(msg.p_time):>20}{'':3}{indent * (msg.p_id.count('/') - 1)}{keyword} {fields}\n"

mark = "\u27e5"
result_mark = "\u27e5\u27e4"

formatters = {
    message.RawTest: (format_test, f"{mark}  Test"),
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
    message.RawResultOK: (format_result, f"{result_mark} OK"),
    message.RawResultFail: (format_result, f"{result_mark} Fail"),
    message.RawResultError: (format_result, f"{result_mark} Error"),
    message.RawResultSkip: (format_result, f"{result_mark} Skip"),
    message.RawResultNull: (format_result, f"{result_mark} Null")
}

def transform():
    """Transform parsed log line into a nice format.
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