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
from enum import IntEnum
from collections import namedtuple

class Message(IntEnum):
    NONE = 0
    TEST = 1
    NULL = 2
    OK = 3
    FAIL = 4
    SKIP = 5
    ERROR = 6
    EXCEPTION = 7
    VALUE = 8
    NOTE = 9
    DEBUG = 10
    TRACE = 11
    XOK = 12
    XFAIL = 13
    XERROR = 14
    XNULL = 15
    PROTOCOL = 16
    INPUT = 17

MessageMap = namedtuple(
        "MessageMap",
        "NONE TEST NULL OK FAIL SKIP ERROR "
        "EXCEPTION VALUE NOTE DEBUG TRACE "
        "XOK XFAIL XERROR XNULL PROTOCOL INPUT"
    )