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
# limitations under the License
__all__ = ["ExitException", "ExitWithError", "ExitWithWarning", "ExitWithSuccess"]

class ExitException(Exception):
    """Base class for all exit exceptions.

    :param exitcode: exit code
    """
    def __init__(self, exitcode, message):
        self.exitcode = exitcode
        self.message = message
        super(ExitException, self).__init__(message)

class ExitWithError(ExitException):
    """Exit with error exception."""
    def __init__(self, message, exitcode=1):
        super(ExitWithError, self).__init__(exitcode, message)

class ExitWithWarning(ExitException):
    """Exit with warning exception."""
    def __init__(self, message, exitcode=0):
        super(ExitWithWarning, self).__init__(exitcode, message)

class ExitWithSuccess(ExitException):
    """Exit with success exception."""
    def __init__(self, message, exitcode=0):
        super(ExitWithSuccess, self).__init__(exitcode, message)