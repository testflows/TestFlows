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
from .name import absname, match
from .baseobject import TestObject

class the(TestObject):
    """The `only`, `skip`, `start` and `end` test filer object.
    """
    _fields = ("pattern", "tags")
    _defaults = (None,)

    def __init__(self, pattern, tags=None):
        self.pattern = pattern
        self.tags = set(tags if tags is not None else [])
        super(the, self).__init__()

    def at(self, at):
        """Anchor filter by converting all patterns to be absolute.
        """
        self.pattern = absname(self.pattern, at)
        return self

    def match(self, name, tags=None, prefix=True):
        if tags is None:
            tags = set()

        if match(name, self.pattern, prefix=prefix):
            if self.tags:
                if tags.issubset(self.tags):
                    return True
                return False
            return True
