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
from collections import namedtuple as namedtuple

import testflows.core.objects as objects


def namedtuple_with_defaults(*args, defaults=()):
    nt = namedtuple(*args)
    nt.__new__.__defaults__ = defaults
    return nt

class Message(object):
    __slots__ = ()

class NoteMessage(Message):
    pass

class DebugMessage(Message):
    pass

class TraceMessage(Message):
    pass

class NoneMessage(Message):
    pass

class UserMessage(Message):
    pass

class ExceptionMessage(Message):
    pass

class ValueMessage(Message):
    pass

class TestMessage(Message):
    pass

class DescriptionMessage(Message):
    pass

class ArgumentMessage(Message):
    pass

class AttributeMessage(Message):
    pass

class RequirementMessage(Message):
    pass

class ResultMessage(Message):
    pass

class OKMessage(ResultMessage):
    pass

class FailMessage(ResultMessage):
    pass

class SkipMessage(ResultMessage):
    pass

class ErrorMessage(ResultMessage):
    pass

class NullMessage(ResultMessage):
    pass

class Prefix(object):
    __slots__ = ()
    fields = "p_keyword p_hash p_num p_id p_name p_flags p_stream p_time "
    keyword, hash, num, id, name, flags, stream, time = list(range(0, 8))

class RawFormat():
    prefix = Prefix

class RawNone(RawFormat, NoneMessage, namedtuple_with_defaults(
        "RawNoneMessage",
        RawFormat.prefix.fields + "message")):
    pass

class RawValue(RawFormat, ValueMessage, namedtuple_with_defaults(
        "RawValueMessage",
        RawFormat.prefix.fields + "name value")):
    pass

class RawException(RawFormat, ExceptionMessage, namedtuple_with_defaults(
        "RawExceptionMessage",
        RawFormat.prefix.fields + "exception")):
    pass

class RawTest(RawFormat, TestMessage, namedtuple_with_defaults(
        "RawTestMessage",
        RawFormat.prefix.fields + "name started flags uid description attributes requirements args",
        defaults=(None, None, None, [], [], []))):
    pass

class RawDescription(RawFormat, DescriptionMessage, namedtuple_with_defaults(
        "RawDescriptionMessage",
        RawFormat.prefix.fields + "description")):
    pass

class RawArgument(RawFormat, ArgumentMessage, namedtuple_with_defaults(
        "RawArgumentMessage",
        RawFormat.prefix.fields + " ".join(objects.Argument._fields),
        defaults=objects.Argument._defaults)):
    pass

class RawAttribute(RawFormat, AttributeMessage, namedtuple_with_defaults(
        "RawAttributeMessage",
        RawFormat.prefix.fields + " ".join(objects.Attribute._fields),
        defaults=objects.Attribute._defaults)):
    pass

class RawRequirement(RawFormat, RequirementMessage, namedtuple_with_defaults(
        "RawRequirementMessage",
        RawFormat.prefix.fields + " ".join(objects.Requirement._fields),
        defaults=objects.Requirement._defaults)):
    pass

class RawResultOK(RawFormat, OKMessage, namedtuple_with_defaults(
        "RawResultOKMessage",
        RawFormat.prefix.fields + " ".join(objects.OK._fields),
        defaults=objects.OK._defaults)):
    pass

class RawResultFail(RawFormat, FailMessage, namedtuple_with_defaults(
        "RawResultFailMessage",
        RawFormat.prefix.fields + " ".join(objects.Fail._fields),
        defaults=objects.Fail._defaults)):
    pass

class RawResultSkip(RawFormat, SkipMessage, namedtuple_with_defaults(
        "RawResultSKIPMessage",
        RawFormat.prefix.fields + " ".join(objects.Skip._fields),
        defaults=objects.Skip._defaults)):
    pass

class RawResultError(RawFormat, ErrorMessage, namedtuple_with_defaults(
        "RawResultERRORMessage",
        RawFormat.prefix.fields + " ".join(objects.Error._fields),
        defaults=objects.Error._defaults)):
    pass

class RawResultNull(RawFormat, NullMessage, namedtuple_with_defaults(
        "RawResultNULLMessage",
        RawFormat.prefix.fields + " ".join(objects.Null._fields),
        defaults=objects.Null._defaults)):
    pass

class RawNote(RawFormat, NoteMessage, namedtuple_with_defaults(
        "RawNoteMessage",
        RawFormat.prefix.fields + "message")):
    pass

class RawTrace(RawFormat, TraceMessage, namedtuple_with_defaults(
        "RawTraceMessage",
        RawFormat.prefix.fields + "message")):
    pass

class RawDebug(RawFormat, DebugMessage, namedtuple_with_defaults(
        "RawDebugMessage",
        RawFormat.prefix.fields + "message")):
    pass