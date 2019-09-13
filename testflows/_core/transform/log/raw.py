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

from testflows._core.transform.log import message
from testflows._core.message import Message
from testflows._core.constants import id_sep

def transform(stop=None):
    """Transform raw message into raw format.
    """
    msg = None
    stop_id = f"{id_sep}{settings.test_id}"
    prefix = message.RawFormat.prefix

    while True:
        if msg is not None:
            try:
                if stop:
                    fields = json.loads(f"[{msg}]")
                    if fields[prefix.keyword] \
                            in (Message.SKIP, Message.NULL, Message.FAIL,
                                Message.ERROR, Message.OK) \
                            and fields[prefix.id] == stop_id:
                        stop.set()
            except (IndexError, Exception):
                raise Exception(f"invalid message: {msg}\n")
        msg = yield msg
