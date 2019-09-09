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
from .objects import *
from .exceptions import exception as get_exception
from .exceptions import ArgumentError
from .name import *
from .flags import *
from .funcs import *
from .message import *
from .settings import *
from .constants import *
from .test import *

__version__ = "1.2.__VERSION__"

def main():
    """Return true if caller is the main module.
    """
    frame = inspect.currentframe().f_back
    return frame.f_globals["__name__"] == "__main__"


