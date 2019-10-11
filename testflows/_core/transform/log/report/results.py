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
from testflows._core.transform.log import message

def process_test(msg, results):
    results[msg.name] = {"test": msg}

def process_result(msg, results):
    results[msg.test]["result"] = msg

processors = {
    message.RawTest: process_test,
    message.RawResultOK: process_result,
    message.RawResultFail: process_result,
    message.RawResultError: process_result,
    message.RawResultSkip: process_result,
    message.RawResultNull: process_result,
    message.RawResultXOK: process_result,
    message.RawResultXFail: process_result,
    message.RawResultXError: process_result,
    message.RawResultXNull: process_result,
}

def transform(results, stop_event):
    """Transform parsed log line into a short format.
    """
    line = None
    while True:
        if line is not None:
            processor = processors.get(type(line), None)
            if processor:
                processor(line, results)
        line = yield line