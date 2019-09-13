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
import json
import importlib

from json import JSONEncoder

from .baseobject import TestArg

class Encoder(JSONEncoder):
    """Argument value encoder.
    """
    def default(self, o):
        if isinstance(o, TestArg):
            objtype = ".".join([o.__class__.__module__, o.__class__.__name__])
            args = list(o.initargs.args)
            args.append(o.initargs.kwargs)
            return {"@py:%s" % objtype : args}
        return super(Encoder, self).default(o)

def object_hook(o):
    if not o:
        return o
    key = next(iter(o))
    if key.startswith("@py:"):
        initargs = o.get(key)
        objtype = key[4:]
        return decode_argument(objtype, initargs)
    return o
    
def decode_argument(objtype, initargs):
    module, cls = objtype.rsplit('.',1)
    args = initargs[:-1] 
    kwargs = initargs[-1]
    return getattr(importlib.import_module(module), cls)(*args, **kwargs)

def dumps(o, *args, **kwargs):
    """Serialize argument value to a JSON formatted string.
    """
    cls = kwargs.pop('cls', Encoder)
    return json.dumps(o, cls=cls, separators=(',', ':'), *args, **kwargs)

def loads(s, *args, **kwargs):
    """Deserializes JSON string to argument value.
    """
    hook = kwargs.pop('object_hook', object_hook)
    return json.loads(s, object_hook=hook, *args, **kwargs)
