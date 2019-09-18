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
from .flags import Flags, SKIP, TE
from .objects import get, Null, OK, Fail, Error, Argument
from .constants import name_sep, id_sep
from .io import TestIO, LogWriter
from .name import join, depth, match
from .funcs import current_test, main, skip, ok, fail, error, exception
from .init import init
from .cli.arg.parser import ArgumentParser
from .cli.arg.exit import ExitWithError, ExitException
from .cli.text import danger, warning
from .exceptions import exception as get_exception

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

    def __init__(self, name=None, flags=None, uid=None, tags=None, attributes=None, requirements=None,
                 users=None, tickets=None, description=None, parent=None,
                 only=None, start=None, end=None, args=None, id=None, _frame=None):
        global current_test

        cli_args = {}
        if current_test.object is None:
            if current_test.main is not None:
                raise RuntimeError("only one top level test is allowed")
            current_test.main = self
            frame = _frame
            if frame is None:
                frame = inspect.currentframe().f_back
            if main(frame):
                cli_args = self.parse_cli_args()

        self.child_count = 0
        self.start_time = time.time()
        self.parent = parent
        self.id = get(id, [settings.test_id])
        self.name = get(name, self.name)

        if self.name is None:
            raise TypeError("name must be specified")

        self.name = self.name.replace(name_sep, "\\" + name_sep)
        self.tags = get(tags, self.tags)
        self.requirements = get(requirements, self.requirements)
        self.attributes = get(attributes, self.attributes)
        self.users = get(users, self.users)
        self.tickets = get(tickets, self.tickets)
        self.description = get(description, self.description)
        self.args = get(args, {})
        self.args.update(cli_args)
        self._process_args()
        self.name = join(get(self.parent, name_sep), self.name)
        self.result = Null(self.name)
        if not flags is None:
            self.flags = Flags(flags)
        self.uid = get(uid, self.uid)

        self.only = [o.at(self.name) for o in get(only, [])]
        self.start = [s.at(self.name) for s in get(start, [])]
        self.end = [e.at(self.name) for e in get(end, [])]
        self.caller_test = None

        self.init(**self.args)

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

        def dummy(*args, **kwargs):
            pass

        if self.flags & SKIP:
            self.trace = sys.gettrace()
            sys.settrace(dummy)
            sys._getframe(1).f_trace = self.__skip__
        else:
            self.caller_test = current_test.object
            current_test.object = self
            try:
                if current_test.main is self:
                    init()
                self.run_return = self.run()
                if type(self.run_return) is types.GeneratorType:
                    next(self.run_return)
            except (KeyboardInterrupt, Exception):
                self.trace = sys.gettrace()
                sys.settrace(dummy)
                sys._getframe(1).f_trace = self.__nop__
                self.__exit__(*sys.exc_info(), frame=inspect.currentframe().f_back)
            return self

    def __nop__(self, *args):
        sys.settrace(self.trace)

    def __skip__(self, *args):
        self.io.close()
        sys.settrace(self.trace)
        raise skip("skip flag set", test=self)

    def __exit__(self, exception_type, exception_value, exception_traceback, frame=None):
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
                if type(self.run_return) is types.GeneratorType:
                    for i in self.run_return:
                        pass

                if isinstance(self.result, Null):
                    self.result = OK(self.name)
        finally:
            self.io.output.result(self.result)
            self.io.close()

            # main cleanup
            if current_test.main is self:
                LogWriter().fd.close()

            if not TE in self.flags and not self.result:
                if frame is None:
                    frame = inspect.currentframe().f_back
                if frame.f_locals.get("__name__", frame.f_globals.get("__name__")) == "__main__" \
                    and depth(self.name) == 1:
                    sys.exit(1)
                raise ResultException(self.result)

        return True

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


def test(*args, **kwargs):
    parent = kwargs.pop("parent", None) or current_test.object
    TestClass = kwargs.pop("testclass", None) or Test

    callargs = inspect.getcallargs(TestClass.__init__, None, *args, **kwargs)
    callargs.pop('self')

    if parent:
        callargs["parent"] = parent.name
        callargs["id"] = parent.id + [parent.child_count]
        parent.child_count += 1

    if not parent and not current_test.main:
        callargs["_frame"] = inspect.currentframe().f_back

    return TestClass(**callargs)

def run(path, test=None, *args, **kwargs):
    """Run a test case specified by module path
    and optional test class or method.

    :param path: test case module path
    :param test: test case object, default: None
    :param *args: *args
    :param **kwargs: **kwargs
    """
    module = importlib.import_module(path)
    if test:
        test = getattr(module, test, None)
    if test is None:
        test = getattr(module, "TestCase", None)
    if test is None:
        test = getattr(module, "TestSuite", None)
    if test is None:
        test = getattr(module, "Test", None)

    callargs = inspect.getcallargs(test.__init__, None, *args, **kwargs)
    callargs.pop('self')

    name = callargs["name"]
    if name:
        callargs["name"] = name % {"name": test.name}

    with globals()["test"](**callargs, testclass=test):
        pass


