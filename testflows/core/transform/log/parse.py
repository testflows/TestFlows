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
import sys
import json

from testflows.core import Message, MessageMap
from testflows.core.transform.log import message

def transform(lines):
    """Transform log lines into parsed list.

    :param lines: lines to process
    """
    prefix = message.RawFormat.prefix

    message_map = MessageMap(
        message.RawNone, # NONE
        message.RawTest, # TEST
        message.RawResultNull, # NULL
        message.RawResultOK, # OK
        message.RawResultFail, # FAIL
        message.RawResultSkip, # SKIP
        message.RawResultError, # ERROR
        message.RawAttribute, # ATTRIBUTE
        message.RawArgument, # ARGUMENT
        message.RawDescription, # DESCRIPTION
        message.RawRequirement, # REQUIREMENT
        message.RawException, # EXCEPTION
        message.RawValue, # VALUE
        message.RawNote, # NOTE
        message.RawDebug, # DEBUG
        message.RawTrace # TRACE
    )

    for line in lines:
        try:
            fields = json.loads(f"[{line}]")
            keyword = fields[prefix.keyword]
            yield message_map[keyword](*fields)
        except (IndexError, Exception):
            raise Exception(f"invalid message: {line}\n")
