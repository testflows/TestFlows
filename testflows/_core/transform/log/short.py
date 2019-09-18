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
from testflows._core.flags import Flags
from testflows._core.transform.log import message

indent = " " * 2

def format_test(msg, keyword):
    return f"{indent * (msg.p_id.count('/') - 1)}{keyword} {msg.name} {Flags(msg.flags)}\n"

def format_result(msg, result):
    return f"{indent * (msg.p_id.count('/') - 1)}{result} {msg.test}\n"

formatters = {
    message.RawTest: (format_test, f"Test"),
    message.RawResultOK: (format_result, f"OK"),
    message.RawResultFail: (format_result, f"Fail"),
    message.RawResultError: (format_result, f"Error"),
    message.RawResultSkip: (format_result, f"Skip"),
    message.RawResultNull: (format_result, f"Null")
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