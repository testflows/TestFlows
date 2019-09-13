# Copyright 2019 Vitaliy Zakaznikov
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
# to the end flag
import copy

from .name import absname
from .baseobject import TestObject

class Operator(object):
    Invert, And, Or = (0,1,2)


class Filter(TestObject):
    """Base class for all filter objects.
    """
    def __init__(self):
        self.expr = None

    def match(self, test):
        return False

    def __and__(self, o):
        self.expr = [Operator.And, copy.deepcopy(self), copy.deepcopy(o)]
        return self
    
    def __or__(self, o):
        self.expr = [Operator.Or, copy.deepcopy(self), copy.deepcopy(o)]
        return self
    
    def __invert__(self):
        self.expr = [Operator.Invert, copy.deepcopy(self)]
        return self
    
    def __repr__(self):
        s = ""
        args = ",".join([repr(arg) for arg in self.initargs.args])
        kwargs = ",".join([name + "=" + repr(value) for name, value in self.initargs.kwargs.items()])
        if args and kwargs:
            args += ","
        name = self.__class__.__name__ 
        if not self.expr:
            s += "%s(%s%s)" % (name, args, kwargs)
        else:
            op, args = self.expr[0], self.expr[1:]
            if op == Operator.Invert:
                s += "~(%s)" % repr(args[0])
            elif op == Operator.Or:
                s += "(%s | %s)" % (repr(args[0]), repr(args[1]))
            elif op == Operator.And:
                s += "(%s & %s)" % (repr(args[0]), repr(args[1]))
            else:
                raise ValueError("unknown operator %s" % repr(op))
        return s
            

class tag(Filter):
    """Tag test filter object.
    """
    _fields = ("name")
    
    def __init__(self, name):
        self.name = name
        super(tag, self).__init__()
    
    def match(self, test):
        return False
  

class the(Filter):
    """The `only`, `start` and `end` test filer object.
    """
    _fields = ("suite", "test", "tags")
    
    def __init__(self, suite, test, tags=[]):
        self.suite = suite
        self.test = test
        self.tags = tags
        super(the, self).__init__()

    def at(self, at):
        """Anchor filter by converting all suite patterns to be absolute.
        """
        new = the(absname(self.suite, at), self.test, self.tags)
        if self.expr:
            new.expr = [self.expr[0]]
            for i,a in enumerate(self.expr[1:]):
                new.expr.append(self.expr[i].at(at))
        return new

    def match(self, test):
        return False
