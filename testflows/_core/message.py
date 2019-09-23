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
    ATTRIBUTE = 7
    ARGUMENT = 8
    DESCRIPTION = 9
    REQUIREMENT = 10
    EXCEPTION = 11
    VALUE = 12
    NOTE = 13
    DEBUG = 14
    TRACE = 15
    XOK = 16
    XFAIL = 17
    XERROR = 18
    XNULL = 19

MessageMap = namedtuple(
        "MessageMap",
        "NONE TEST NULL OK FAIL SKIP ERROR ATTRIBUTE ARGUMENT "
        "DESCRIPTION REQUIREMENT EXCEPTION VALUE NOTE DEBUG TRACE "
        "XOK XFAIL XERROR XNULL"
    )