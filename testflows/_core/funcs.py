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
import os
import inspect
import importlib
import threading

from .exceptions import ResultException
from .serialize import dumps
from .message import Message
from .objects import OK, Fail, Error, Skip, Null
from .objects import XOK, XFail, XError, XNull
from .cli.text import warning
from .cli.colors import reset as reset_colors
from .cli.colors import cursor_up as move_cursor_up

#: current test handle
current_test = threading.local()
current_test.object = None
current_test.main = None

def thetest():
    return current_test.object

def load(module, test=None):
    """Load test from module path.

    :param module: module path
    :param test: test class or method to load (optional)
    """
    module = importlib.import_module(module)
    if test:
        test = getattr(module, test, None)
    if test is None:
        test = getattr(module, "TestCase", None)
    if test is None:
        test = getattr(module, "TestSuite", None)
    if test is None:
        test = getattr(module, "Test", None)
    return test

def append_path(pathlist, path, *rest, **kwargs):
    """Append path relative to the caller
    to the path list.

    :param pathlist: path list
    :param path: path relative to the caller
    :param *rest: rest of the path
    :param pos: insert at given position,
       default: append to the end of the list
    """
    pos = kwargs.pop("pos", None)
    frame = inspect.currentframe().f_back
    dir = os.path.join(os.path.dirname(os.path.abspath(frame.f_globals["__file__"])), path, *rest)
    if dir not in pathlist:
        if pos is None:
            pathlist.append(dir)
        else:
            pathlist.insert(pos, dir)
    return pathlist

def main(frame=None):
    """Return true if caller is the main module.

    :param frame: caller frame
    """
    if frame is None:
        frame = inspect.currentframe().f_back
    return frame.f_globals["__name__"] == "__main__"

class args(dict):
    pass

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
    raise ResultException(test.result)

def fail(message=None, test=None):
    if test is None:
        test = current_test.object
    test.result = Fail(test.name, message)
    raise ResultException(test.result)

def skip(message=None, test=None):
    if test is None:
        test = current_test.object
    test.result = Skip(test.name, message)
    raise ResultException(test.result)

def error(message=None, test=None):
    if test is None:
        test = current_test.object
    test.result = Error(test.name, message)
    raise ResultException(test.result)

def null(test=None):
    if test is None:
        test = current_test.object
    test.result = Null(test.name)
    raise ResultException(test.result)

def xok(message=None, test=None):
    if test is None:
        test = current_test.object
    test.result = XOK(test.name, message)
    raise ResultException(test.result)

def xfail(message=None, test=None):
    if test is None:
        test = current_test.object
    test.result = XFail(test.name, message)
    raise ResultException(test.result)

def xerror(message=None, test=None):
    if test is None:
        test = current_test.object
    test.result = XError(test.name, message)
    raise ResultException(test.result)

def xnull(test=None):
    if test is None:
        test = current_test.object
    test.result = XNull(test.name)
    raise ResultException(test.result)

def pause(test=None):
    if test is None:
        test = current_test.object
    test.io.output.input("Paused, enter any key to continue...")
    input()
