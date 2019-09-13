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
import inspect
import threading

from .exceptions import ResultException
from .serialize import dumps
from .message import Message
from .objects import OK, Fail, Error, Skip, Null

#: current test handle
current_test = threading.local()
current_test.object = None
current_test.main = None

def main(frame=None):
    """Return true if caller is the main module.

    :param frame: caller frame
    """
    if frame is None:
        frame = inspect.currentframe().f_back
    return frame.f_globals["__name__"] == "__main__"

def note(message, test=None):
    if test is None:
        test = current_test.object
    test.io.output.note(message)

def debug(message, test=None):
    if test is None:
        test = current_test.object
    test.io.output.debug(message)

def trace(message, test=None):
    if test is None:
        test = current_test.object
    test.io.output.trace(message)

def message(message, test=None):
    if test is None:
        test = current_test.object
    test.io.output.message(Message.NONE, dumps(str(message)))

def value(name, value, test=None):
    if test is None:
        test = current_test.object
    test.io.output.value(name, value)
    return value

def exception(test=None):
    if test is None:
        test = current_test.object
    test.io.output.exception()

def ok(message=None, test=None):
    if test is None:
        test = current_test.object
    test.result = OK(test.name, message)
    return ResultException(test.result)

def fail(message=None, test=None):
    if test is None:
        test = current_test.object
    test.result = Fail(test.name, message)
    return ResultException(test.result)

def skip(message=None, test=None):
    if test is None:
        test = current_test.object
    test.result = Skip(test.name, message)
    return ResultException(test.result)

def error(message=None, test=None):
    if test is None:
        test = current_test.object
    test.result = Error(test.name, message)
    return ResultException(test.result)

def null(test=None):
    if test is None:
        test = current_test.object
    test.result = Null(test.name)
    return ResultException(test.result)