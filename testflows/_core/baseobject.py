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
import copy

from hashlib import sha1
from collections import namedtuple

InitArgs = namedtuple("InitArgs", "args kwargs")

def get(a, b):
    """a if not a is None else b.
    """
    return a if not a is None else b

def hash(*s):
    """Calculate standard hash.
    
    :param s: strings
    """
    return sha1(''.join(s).encode("utf-8")).hexdigest()[:32]


class TestObject(object):
    """Base class for all the test objects.
    """
    #: object fields used to represent state of the object
    _fields = ()
    #: defaults for the fields
    _defaults = ()

    def __new__(cls, *args, **kwargs):
        obj = super(TestObject, cls).__new__(cls)
        obj.initargs=InitArgs(
            args=[copy.deepcopy(a) for a in args],
            kwargs={k: copy.deepcopy(v) for k,v in kwargs.items()})
        return obj

    @property
    def id(self):
        return hash(*[repr(getattr(self, field)) for field in self._fields if field != "id"])

    def __repr__(self):
        """Custom object representation.
        """
        args = ",".join([repr(arg) for arg in self.initargs.args])
        kwargs = ",".join([name + "=" + repr(value) for name, value in self.initargs.kwargs.items()])
        name = self.__class__.__name__ 
        if args and kwargs:
            args += ","
        return "%s(%s%s)" % (name, args, kwargs)


class TestArg(TestObject):
    """Base class for all test argument object.
    """
    pass
