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
import inspect
import functools
import tempfile

import testflows.settings as settings

from .exceptions import DummyTestException, ArgumentError, ResultException
from .flags import Flags, SKIP, TE, FAIL_NOT_COUNTED, ERROR_NOT_COUNTED, NULL_NOT_COUNTED
from .flags import CFLAGS, PAUSE_BEFORE, PAUSE_AFTER
from .testtype import TestType, TestSubType
from .objects import get, Null, OK, Fail, Skip, Error, Argument
from .constants import name_sep, id_sep
from .io import TestIO, LogWriter
from .name import join, depth, match, absname
from .funcs import current_test, main, skip, ok, fail, error, exception, pause, load
from .init import init
from .cli.arg.parser import ArgumentParser
from .cli.arg.exit import ExitWithError, ExitException
from .cli.text import danger, warning
from .exceptions import exception as get_exception
from .filters import the

class xfails(dict):
    """xfails container.

    xfails = {
        "pattern": [("result", "reason")],
        ...
        }
    """
    def add(self, pattern, *results):
        """Add an entry to the xfails.

        :param pattern: test name pattern to match
        :param *results: one or more results to cross out
            where each result is a two-tuple of (result, reason)
        """
        self[pattern] = results
        return self

class xflags(dict):
    """xflags container.

    xflags = {
        "filter": (set_flags, clear_flags),
        ... 
    }
    """
    def add(self, pattern, set_flags=0, clear_flags=0):
        """Add an entry to the xflags.

        :param pattern: test name pattern to match
        :param set_flags: flags to set
        :param clear_flags: flags to clear, default: None
        """
        self[pattern] = [Flags(set_flags), Flags(clear_flags)]
        return self

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
    type = TestType.Test
    subtype = TestSubType.Empty

    @classmethod
    def argparser(cls):
        """Command line argument parser.

        :return: argument parser
        """
        definitions_description = """
        
        Option values
        
        pattern 
          used to match test names using a unix-like file path pattern that supports wildcards
            '/' path level separator
            '*' matches everything
            '?' matches any single character
            '[seq]' matches any character in seq
            '[!seq]' matches any character not in seq
            ':' matches anything at the current path level
          for example: "suiteA/*" selects all the tests in 'suiteA'
        """
        parser = ArgumentParser(
                prog=sys.argv[0],
                description=((cls.description or "") + definitions_description),
                description_prog="Test - Framework"
            )
        parser.add_argument("--only", dest="_only", metavar="pattern", nargs="+",
            help="run only selected tests", type=str, required=False)
        parser.add_argument("--skip", dest="_skip", metavar="pattern", nargs="+",
            help="skip selected tests", type=str, required=False)
        parser.add_argument("--start", dest="_start", metavar="pattern", nargs=1,
            help="start at the selected test", type=str, required=False)
        parser.add_argument("--end", dest="_end", metavar="pattern", nargs=1,
            help="end at the selected test", type=str, required=False)
        parser.add_argument("--pause-before", dest="_pause_before", metavar="pattern", nargs="+",
            help="pause before executing selected tests", type=str, required=False)
        parser.add_argument("--pause-after", dest="_pause_after", metavar="pattern", nargs="+",
            help="pause after executing selected tests", type=str, required=False)
        parser.add_argument("--debug", dest="_debug", action="store_true",
            help="enable debugging mode", default=False)
        parser.add_argument("--no-colors", dest="_no_colors", action="store_true",
            help="disable terminal color highlighting", default=False)
        parser.add_argument("--id", metavar="id", dest="_id", type=str, help="custom test id")
        parser.add_argument("-o", "--output", dest="_output", metavar="format", type=str,
            choices=["nice", "quiet", "short", "dots", "raw", "silent"], default="nice",
            help="""stdout output format, choices are: ['nice','short','dots','quiet','raw','silent'],
                default: 'nice'""")
        parser.add_argument("-l", "--log", dest="_log", metavar="file", type=str,
            help="path to the log file where test output will be stored, default: uses temporary log file")
        parser.add_argument("--show-skipped", dest="_show_skipped", action="store_true",
            help="show skipped tests, default: False", default=False)
        return parser

    def parse_cli_args(self, xflags=None, only=None, skip=None, start=None, end=None):
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

            if args.get("_show_skipped"):
                settings.show_skipped = True
                args.pop("_show_skipped")

            if args.get("_pause_before"):
                if not xflags:
                    xflags = globals()["xflags"]()
                for pattern in args.get("_pause_before"):
                    pattern = absname(pattern, self.name)
                    xflags[pattern] = xflags.get(pattern, [0, 0])
                    xflags[pattern][0] |= PAUSE_BEFORE
                args.pop("_pause_before")

            if args.get("_pause_after"):
                if not xflags:
                    xflags = globals()["xflags"](xflags)
                for pattern in args.get("_pause_after"):
                    pattern = absname(pattern, self.name)
                    xflags[pattern] = xflags.get(pattern, [0, 0])
                    xflags[pattern][0] |= PAUSE_AFTER
                args.pop("_pause_after")

            if args.get("_only"):
                only = [] # clear whatever was passed
                for pattern in args.get("_only"):
                    only.append(the(pattern).at(self.name))
                args.pop("_only")

            if args.get("_skip"):
                skip = [] # clear whatever was passed
                for pattern in args.get("_skip"):
                    only.append(the(pattern).at(self.name))
                args.pop("_skip")

            if args.get("_start"):
                start = the(args.get("_start")[0]).at(self.name)
                args.pop("_start")

            if args.get("_end"):
                end = the(args.get("_end")[0]).at(self.name)
                args.pop("_end")

        except (ExitException, KeyboardInterrupt, Exception) as exc:
            #if settings.debug:
            sys.stderr.write(warning(get_exception(), eol='\n'))
            sys.stderr.write(danger("error: " + str(exc).strip()))
            if isinstance(exc, ExitException):
                sys.exit(exc.exitcode)
            else:
                sys.exit(1)

        return args, xflags, only, skip, start, end

    def __init__(self, name=None, flags=None, cflags=None, type=None, subtype=None,
                 uid=None, tags=None, attributes=None, requirements=None,
                 users=None, tickets=None, description=None, parent=None,
                 xfails=None, xflags=None, only=None, skip=None,
                 start=None, end=None, args=None, id=None, _frame=None):
        global current_test

        self.name = name
        if self.name is None:
            raise TypeError("name must be specified")

        cli_args = {}
        if current_test.object is None:
            if current_test.main is not None:
                raise RuntimeError("only one top level test is allowed")
            current_test.main = self
            frame = get(_frame, inspect.currentframe().f_back.f_back.f_back)
            if main(frame):
                cli_args, xflags, only, skip, start, end = self.parse_cli_args(xflags, only, skip, start, end)

        self.child_count = 0
        self.start_time = time.time()
        self.parent = parent
        self.id = get(id, [settings.test_id])
        self.tags = tags
        self.requirements = get(requirements, self.requirements)
        self.attributes = get(attributes, self.attributes)
        self.users = get(users, self.users)
        self.tickets = get(tickets, self.tickets)
        self.description = get(description, self.description)
        self.args = get(args, {})
        self.args.update({k:v for k, v in cli_args.items() if not k.startswith("_")})
        self._process_args()
        self.result = Null(self.name)
        if flags is not None:
            self.flags = Flags(flags)
        self.type = get(type, self.type)
        self.subtype = get(subtype, self.subtype)
        self.cflags = Flags(cflags) | (self.flags & CFLAGS)
        self.uid = get(uid, self.uid)
        self.xfails = get(xfails, {})
        self.xflags = get(xflags, {})
        self.only = get(only, [])
        self.skip = get(skip, [])
        self.start = get(start, None)
        self.end = get(end, None)
        self.caller_test = None

    @classmethod
    def make_name(cls, name, parent=None):
        """Make full name.

        :param name: name
        :param parent: parent name
        """
        name = name % {"name": cls.name} if name is not None else cls.name
        name = name.replace(name_sep, "\\" + name_sep)
        return join(get(parent, name_sep), name)

    @classmethod
    def make_tags(cls, tags):
        return set(get(tags, cls.tags))

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
        if current_test.main is self:
            self.io.output.protocol()
        self.io.output.test_message()

        if self.flags & PAUSE_BEFORE:
            pause()

        self.caller_test = current_test.object
        current_test.object = self

        if self.flags & SKIP:
            raise ResultException(Skip(self.name, "skip flag set"))
        else:
            if current_test.main is self:
                init()
            self.run(**{name: arg.value for name, arg in self.args.items()})
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
                    if isinstance(exception_value, KeyboardInterrupt):
                        raise self.result
            else:
                if isinstance(self.result, Null):
                    self.result = OK(self.name)
        finally:
            self._apply_xfails()
            self.io.output.result(self.result)
            self.io.close()

            if self.flags & PAUSE_AFTER:
                pause()

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

    def run(self, **args):
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
            # propagate xfails, xflags, only and skip that prefix match the name of the test
            kwargs["xfails"] = xfails({
                    k: v for k, v in parent.xfails.items() if match(name, k, prefix=True)
                }) or kwargs.get("xfails")
            kwargs["xflags"] = xflags({
                    k: v for k, v in parent.xflags.items() if match(name, k, prefix=True)
                }) or kwargs.get("xflags")
            kwargs["only"] = parent.only or kwargs.get("only")
            kwargs["skip"] = parent.skip or kwargs.get("skip")
            kwargs["start"] = parent.start or kwargs.get("start")
            kwargs["end"] = parent.end or kwargs.get("end")
            # handle parent test type propagation
            self._parent_type_propagation(parent, kwargs)
            parent.child_count += 1
        else:
            name = test.make_name(name)
        tags = test.make_tags(kwargs.get("tags"))

        # anchor all patterns
        kwargs["xfails"] = xfails({
                absname(k, name if name else name_sep): v for k, v in (kwargs.get("xfails") or {}).items()
            }) or None
        kwargs["xflags"] = xflags({
                absname(k, name if name else name_sep): v for k, v in (kwargs.get("xflags") or {}).items()
            }) or None
        kwargs["only"] = [f.at(name if name else name_sep) for f in kwargs.get("only") or []] or None
        kwargs["skip"] = [f.at(name if name else name_sep) for f in kwargs.get("skip") or []] or None
        kwargs["start"] = kwargs.get("start").at(name if name else name_sep) if kwargs.get("start") else None
        kwargs["end"] = kwargs.get("end").at(name if name else name_sep) if kwargs.get("end") else None

        self.parent = parent
        self._apply_xflags(name, kwargs)
        self._apply_only(name, tags, kwargs)
        self._apply_skip(name, tags, kwargs)
        self._apply_start(name, tags, parent, kwargs)
        self._apply_end(name, tags, parent, kwargs)
        self.test = test(name, tags=tags, **kwargs)

    def _apply_end(self, name, tags, parent, kwargs):
        end = kwargs.get("end")
        if not end:
            return

        if end.match(name, tags):
            if parent:
                parent.end = None
                parent.skip = [the("/*")]

    def _apply_start(self, name, tags, parent, kwargs):
        start = kwargs.get("start")
        if not start:
            return

        if not start.match(name, tags):
            kwargs["flags"] = Flags(kwargs.get("flags")) | SKIP
        else:
            kwargs["flags"] = Flags(kwargs.get("flags")) & ~SKIP
            if parent:
                parent.start = None

    def _apply_only(self, name, tags, kwargs):
        only = kwargs.get("only")
        if not only:
            return

        found = False
        for item in only:
            if item.match(name, tags):
                found = True
                break

        if not found:
            kwargs["flags"] = Flags(kwargs.get("flags")) | SKIP
        else:
            kwargs["flags"] = Flags(kwargs.get("flags")) & ~SKIP

    def _apply_skip(self, name, tags, kwargs):
        skip = kwargs.get("skip")
        if not skip:
            return

        for item in skip:
            if item.match(name, tags, prefix=False):
                kwargs["flags"] = Flags(kwargs.get("flags")) | SKIP
                break

    def _apply_xflags(self, name, kwargs):
        xflags = kwargs.get("xflags")
        if not xflags:
            return
        for pattern, item in xflags.items():
            if match(name, pattern):
                set_flags, clear_flags = item
                kwargs["flags"] = (Flags(kwargs.get("flags")) & ~Flags(clear_flags)) | Flags(set_flags)

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

# support for BDD
class feature(test):
    def __init__(self, name, **kwargs):
        kwargs["subtype"] = TestSubType.Feature
        return super(feature, self).__init__(name,  _frame=inspect.currentframe().f_back, **kwargs)

class scenario(test):
    def __init__(self, name, **kwargs):
        kwargs["subtype"] = TestSubType.Scenario
        return super(scenario, self).__init__(name, _frame=inspect.currentframe().f_back, **kwargs)

class given(step):
    def __init__(self, name, **kwargs):
        kwargs["subtype"] = TestSubType.Given
        return super(given, self).__init__(name,  _frame=inspect.currentframe().f_back, **kwargs)

class when(step):
    def __init__(self, name, **kwargs):
        kwargs["subtype"] = TestSubType.When
        return super(when, self).__init__(name,  _frame=inspect.currentframe().f_back, **kwargs)

class then(step):
    def __init__(self, name, **kwargs):
        kwargs["subtype"] = TestSubType.Then
        return super(then, self).__init__(name,  _frame=inspect.currentframe().f_back, **kwargs)

# decorators
class _testdecorator(object):
    type = test
    def __init__(self, func):
        func.name = getattr(func, "name", func.__name__.replace("_", " "))
        func.description = getattr(func, "description", func.__doc__)
        self.func = func
        functools.update_wrapper(self, func)

    def __call__(self, args=None, **kwargs):
        if args is None:
            args = {}
        frame = kwargs.pop("_frame", inspect.currentframe().f_back)
        _kwargs = dict(vars(self.func))
        _name = kwargs.pop("name", None)
        if _name is not None:
            kwargs["name"] = _name % (_kwargs)
        _kwargs.update(kwargs)
        with self.type(**_kwargs, args=args, _frame=frame) as testcase:
            self.func(**args)
        return testcase

class testcase(_testdecorator):
    type = test

class testscenario(testcase):
    type = scenario

class testfeature(testcase):
    type = feature

class testsuite(_testdecorator):
    type = suite

class testmodule(_testdecorator):
    type = module

class name(object):
    def __init__(self, name):
        self.name = name

    def __call__(self, func):
        func.name = self.name
        return func

class description(object):
    def __init__(self, description):
        self.description = description

    def __call__(self, func):
        func.description = self.description
        return func

class attributes(object):
    def __init__(self, *attributes):
        self.attributes = attributes

    def __call__(self, func):
        func.attributes = self.attributes
        return func

class requirements(object):
    def __init__(self, *requirements):
        self.requirements = requirements

    def __call__(self, func):
        func.requirements = self.requirements
        return func

class tags(object):
    def __init__(self, *tags):
        self.tags = tags

    def __call__(self, func):
        func.tags = self.tags
        return func

class uid(object):
    def __init__(self, uid):
        self.uid = uid

    def __call__(self, func):
        func.uid = self.uid
        return func

class users(object):
    def __init__(self, *users):
        self.users = users

    def __call__(self, func):
        func.users = self.users
        return func

class tickets(object):
    def __init__(self, *tickets):
        self.tickets = tickets

    def __call__(self, func):
        func.tickets = self.tickets
        return func

def run(test, **kwargs):
    """Run a test.

    :param test: test class, test function or test module path
    :param cls: if test is a module path, cls can
       specify test definition to load (optional)
    """
    cls = kwargs.pop("cls", None)

    if inspect.isclass(test) and issubclass(test, Test):
        test = test
    elif issubclass(type(test), _testdecorator):
        return test(**kwargs, _frame=inspect.currentframe().f_back)
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
