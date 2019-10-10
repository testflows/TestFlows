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
import json

import testflows.settings as settings

from testflows._core.message import MessageMap
from testflows._core.transform.log import message
from testflows._core.constants import id_sep

def transform(stop=None):
    """Transform log line into parsed list.

    :param stop: stop event, default: None
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
        message.RawException, # EXCEPTION
        message.RawValue, # VALUE
        message.RawNote, # NOTE
        message.RawDebug, # DEBUG
        message.RawTrace, # TRACE
        message.RawResultXOK, #XOK
        message.RawResultXFail, # XFAIL
        message.RawResultXError, # XERROR
        message.RawResultXNull, # XNULL
        message.RawProtocol, # PROTOCOL
        message.RawInput, # INPUT
        message.RawVersion, # VERSION
    )
    msg = None
    stop_id = None

    while True:
        if msg is not None:
            try:
                fields = json.loads(f"[{msg}]")
                keyword = fields[prefix.keyword]
                msg = message_map[keyword](*fields)
                if stop_id is None:
                    stop_id = f"{msg.p_id}"
                if isinstance(msg, message.ResultMessage):
                    if stop and msg.p_id == stop_id:
                        stop.set()
            except (IndexError, Exception):
                raise Exception(f"invalid message: {msg}\n")
        msg = yield msg
