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
import sys
import time
import types
import inspect
import functools
import tempfile
import importlib

import testflows.settings as settings

from .exceptions import DummyTestException, ArgumentError, ResultException
from .flags import Flags, SKIP, TE, FAIL_NOT_COUNTED, ERROR_NOT_COUNTED, NULL_NOT_COUNTED
from .flags import CFLAGS
from .testtype import TestType
from .objects import get, Null, OK, Fail, Skip, Error, Argument
from .constants import name_sep, id_sep
from .io import TestIO, LogWriter
from .name import join, depth, match, absname
from .funcs import current_test, main, skip, ok, fail, error, exception
from .init import init
from .cli.arg.parser import ArgumentParser
from .cli.arg.exit import ExitWithError, ExitException
from .cli.text import danger, warning
from .exceptions import exception as get_exception

class xfails(dict):
    """xfails container.

    xfails = {
        "filter": [("result", "reason")],
        ...
        }
    """
    pass

class xflags(dict):
    """xflags container.

    xflags = {
        "filter": (set_flags, clear_flags),
        ... 
    }
    """
    pass

class DummyTest(object):
    """Base class for dummy tests.
    """
    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        def dummy(*args, **kwargs):
            pass

        self.trace = sys.gettrace()
        sys.settrace(dummy)
        sys._getframe(1).f_trace = self.__skip__

    def __skip__(self, *args):
        sys.settrace(self.trace)
        raise DummyTestException()

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if isinstance(exception_value, DummyTestException):
            return True


class Test(object):
    """Base class for all the tests.

    :param name: name
    :param flags: flags
    :param parent: parent name
    :param only: tests to run
    :param start: name of the starting test
    :param end: name of the last test
    """
    uid = None
    tags = set()
    attributes = []
    requirements = []
    users = []
    tickets = []
    name = None
    description = None
    flags = Flags()
    name_sep = "."

    @classmethod
    def argparser(cls):
        """Command line argument parser.

        :return: argument parser
        """
        parser = ArgumentParser(
                prog=sys.argv[0],
                description=(cls.description or ""),
                description_prog="Test - Framework"
            )
        parser.add_argument("--debug", dest="_debug", action="store_true",
            help="enable debugging mode", default=False)
        parser.add_argument("--no-colors", dest="_no_colors", action="store_true",
            help="disable terminal color highlighting", default=False)
        parser.add_argument("--id", metavar="id", dest="_id", type=str, help="custom test id")
        parser.add_argument("-o", "--output", dest="_output", metavar="format", type=str,
            choices=["nice", "quiet", "short", "raw", "silent"], default="nice",
            help="""stdout output format, choices are: ['nice','short','quiet','raw','silent'],
                default: 'nice'""")
        parser.add_argument("-l", "--log", dest="_log", metavar="file", type=str,
            help="path to the log file where test output will be stored, default: uses temporary log file")

        return parser

    def parse_cli_args(self):
        """Parse command line arguments.

        :return: parsed known arguments
        """
        try:
            parser = self.argparser()
            args, unknown = parser.parse_known_args()
            args = vars(args)

            if args.get("_debug"):
                settings.debug = True
                args.pop("_debug")

            if args.get("_no_colors"):
                settings.no_colors = True
                args.pop("_no_colors")

            if unknown:
                raise ExitWithError(f"unknown argument {unknown}")

            if args.get("_id"):
                settings.test_id = args.get("_id")
                args.pop("_id")

            if args.get("_log"):
                logfile = os.path.abspath(args.get("_log"))
                settings.write_logfile = logfile
                args.pop("_log")
            else:
                settings.write_logfile = os.path.join(tempfile.gettempdir(), f"testflows.{os.getpid()}.log")

            settings.read_logfile = settings.write_logfile
            if os.path.exists(settings.write_logfile):
                os.remove(settings.write_logfile)

            settings.output_format = args.pop("_output")

        except (ExitException, KeyboardInterrupt, Exception) as exc:
            #if settings.debug:
            sys.stderr.write(warning(get_exception(), eol='\n'))
            sys.stderr.write(danger("error: " + str(exc).strip()))
            if isinstance(exc, ExitException):
                sys.exit(exc.exitcode)
            else:
                sys.exit(1)
        return args

    def __init__(self, name=None, flags=None, cflags=None, type=None,
                 uid=None, tags=None, attributes=None, requirements=None,
                 users=None, tickets=None, description=None, parent=None,
                 xfails=None, xflags=None, only=None, skip=None, start=None, end=None, args=None, id=None):
        global current_test

        cli_args = {}
        if current_test.object is None:
            if current_test.main is not None:
                raise RuntimeError("only one top level test is allowed")
            current_test.main = self
            frame = inspect.currentframe().f_back.f_back.f_back
            if main(frame):
                cli_args = self.parse_cli_args()

        self.child_count = 0
        self.start_time = time.time()
        self.parent = parent
        self.id = get(id, [settings.test_id])
        self.name = name
        if self.name is None:
            raise TypeError("name must be specified")

        self.tags = get(tags, self.tags)
        self.requirements = get(requirements, self.requirements)
        self.attributes = get(attributes, self.attributes)
        self.users = get(users, self.users)
        self.tickets = get(tickets, self.tickets)
        self.description = get(description, self.description)
        self.args = get(args, {})
        self.args.update(cli_args)
        self._process_args()
        self.result = Null(self.name)
        if flags is not None:
            self.flags = Flags(flags)
        self.type = get(type, TestType.Test)
        self.cflags = Flags(cflags) | (self.flags & CFLAGS)
        self.uid = get(uid, self.uid)

        self.xfails = get(xfails, globals()["xfails"]())
        self.xflags = get(xflags, globals()["xflags"]())

        self.only = [o.at(self.name) for o in get(only, [])]
        self.skip = [o.at(self.name) for o in get(skip, [])]
        self.start = [s.at(self.name) for s in get(start, [])]
        self.end = [e.at(self.name) for e in get(end, [])]
        self.caller_test = None

        self.init(**self.args)

    @classmethod
    def make_name(cls, name, parent=None):
        """Make full name.

        :param name: name
        :param parent: parent name
        """
        name = name % {"name": cls.name} if name is not None else cls.name
        name = name.replace(name_sep, "\\" + name_sep)
        return join(get(parent, name_sep), name)

    def _process_args(self):
        """Process arguments by converting
        them into a dictionary of
        "name:Argument" pairs
        """
        args = []
        try:
            try:
                for name in dict(self.args):
                    value = self.args.get(name)
                    if not isinstance(value, Argument):
                        value = Argument(name=name, value=value)
                    args.append(value)
            except TypeError:
                args = self.args

            self.args = {}

            for arg in args:
                if not isinstance(arg, Argument):
                    raise ValueError(f"not an argument {arg}")
                self.args[arg.name] = arg
        except ArgumentError:
            raise
        except Exception as e:
            raise ArgumentError(str(e))

    def __enter__(self):
        self.io = TestIO(self)
        self.io.output.test_message()

        self.caller_test = current_test.object
        current_test.object = self

        if self.flags & SKIP:
            raise ResultException(Skip(self.name, "skip flag set"))
        else:
            if current_test.main is self:
                init()
            self.run()
            return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        global current_test
        current_test.object = self.caller_test

        try:
            if exception_value:
                if isinstance(exception_value, ResultException):
                    self.result = exception_value.result
                elif isinstance(exception_value, AssertionError):
                    exception(test=self)
                    self.result = Fail(self.name, str(exception_value).split('\n', 1)[0])
                else:
                    exception(test=self)
                    self.result = Error(self.name,
                        "unexpected %s: %s" % (exception_type.__name__, str(exception_value).split('\n', 1)[0]))
            else:
                if isinstance(self.result, Null):
                    self.result = OK(self.name)
        finally:
            self._apply_xfails()
            self.io.output.result(self.result)
            self.io.close()

        return True

    def _apply_xfails(self):
        """Apply xfails to self.result.
        """
        for pattern, xouts in self.xfails.items():
            if match(self.name, pattern):
                for xout in xouts:
                    result, reason = xout
                    if isinstance(self.result, result):
                        self.result = self.result.xout(reason)

    def init(self, **args):
        pass

    def run(self):
        pass

    def bind(self, func):
        """Bind function to the current test.

        :param func: function that takes an instance of test
            as the argument named 'test'
        :return: partial function with the 'test' argument set to self
        """
        return functools.partial(func, test=self)

    def message_io(self, name=""):
        """Return an instance of test's message IO
        used to write messages using print() method
        or other methods that takes a file-like
        object.

        Note: only write() and flush() methods
        are supported.

        :param name: name of the stream, default: None
        """
        return self.io.message_io(name=name)

class _test(object):
    """Test definition.

    :param name: name of the test
    :param test: test class (optional), default: Test
    :param **kwargs: test class arguments
    """
    def __init__(self, name, **kwargs):
        parent = kwargs.pop("parent", None) or current_test.object
        test = kwargs.pop("test", None)

        test = test if test is not None else Test

        if parent:
            name = test.make_name(name, parent.name)
            kwargs["parent"] = parent.name
            kwargs["id"] = parent.id + [parent.child_count]
            kwargs["cflags"] = parent.cflags
            # only propagate xfails that prefix match the name of the test
            kwargs["xfails"] = {
                    k: v for k, v in parent.xfails.items() if match(name, k, prefix=True)
                } or kwargs.get("xfails")
            # handle parent test type propagation
            self._parent_type_propagation(parent, kwargs)
            parent.child_count += 1
        else:
            name = test.make_name(name)

        # anchor all xfails patterns
        kwargs["xfails"] = {
                absname(k, parent.name if parent else name_sep): v for k, v in (kwargs.get("xfails") or {}).items()
            } or None

        self.parent = parent
        self.test = test(name, **kwargs)

    def _parent_type_propagation(self, parent, kwargs):
        """Propagate parent test type if lower.

        :param parent: parent
        :param kwargs: test's kwargs
        """
        type = kwargs.pop("type", TestType.Test)
        if int(parent.type) < int(type):
            type = parent.type
        kwargs["type"] = type

    def __enter__(self):
        def dummy(*args, **kwargs):
            pass
        try:
            return self.test.__enter__()
        except (KeyboardInterrupt, Exception):
            self.trace = sys.gettrace()
            sys.settrace(dummy)
            sys._getframe(1).f_trace = functools.partial(self.__nop__, *sys.exc_info())

    def __nop__(self, exc_type, exc_value, exc_tb, *args):
        sys.settrace(self.trace)
        raise exc_value.with_traceback(exc_tb)

    def __exit__(self, exception_type, exception_value, exception_traceback):
        try:
            test__exit__ = self.test.__exit__(exception_type, exception_value, exception_traceback)
        except (KeyboardInterrupt, Exception):
            raise

        # if test did not handle the exception in __exit__ then re-raise it
        if exception_value and not test__exit__:
            raise exception_value.with_traceback(exception_traceback)

        if not self.test.result:
            if not self.parent:
                sys.exit(1)

            if isinstance(self.test.result, Fail):
                result = Fail(self.parent.name, self.test.result.message)
            else:
                # convert Null into an Error
                result = Error(self.parent.name, self.test.result.message)

            if TE not in self.test.flags:
                raise ResultException(result)
            else:
                if isinstance(self.parent.result, Error):
                    pass
                elif isinstance(self.test.result, Error) and ERROR_NOT_COUNTED not in self.test.flags:
                    self.parent.result = result
                elif isinstance(self.test.result, Null) and NULL_NOT_COUNTED not in self.test.flags:
                    self.parent.result = result
                elif isinstance(self.parent.result, Fail):
                    pass
                elif isinstance(self.test.result, Fail) and FAIL_NOT_COUNTED not in self.test.flags:
                    self.parent.result = result
                else:
                    pass
        return True

class module(_test):
    """Module definition."""
    def __init__(self, name, **kwargs):
        kwargs["type"] = TestType.Module
        return super(module, self).__init__(name, **kwargs)

class suite(_test):
    """Suite definition."""
    def __init__(self, name, **kwargs):
        kwargs["type"] = TestType.Suite
        return super(suite, self).__init__(name, **kwargs)

class test(_test):
    """Test definition."""
    def __init__(self, name, **kwargs):
        kwargs["type"] = TestType.Test
        return super(test, self).__init__(name, **kwargs)

class step(_test):
    """Step definition."""
    def __init__(self, name, **kwargs):
        kwargs["type"] = TestType.Step
        return super(step, self).__init__(name, **kwargs)

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

def run(test, **kwargs):
    """Run a test.

    :param test: test class, test function or test module path
    :param cls: if test is a module path, cls can
       specify test definition to load (optional)
    """
    cls = kwargs.pop("cls", None)

    if inspect.isclass(test) and issubclass(test, Test):
        test = test
    elif type(test) is str:
        return run(load(test, cls), **kwargs)
    elif inspect.isfunction(test):
        return test(**kwargs)
    elif inspect.ismethod(test):
        return test(**kwargs)
    else:
        raise TypeError(f"invalid test type '{type(test)}'")

    with globals()["test"](test=test, name=kwargs.pop("name", None), **kwargs) as test:
        pass

    return test.result
