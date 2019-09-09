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
from argparse import ArgumentParser as ArgumentParserBase

from testflows.core.cli.arg.common import epilog
from testflows.core.cli.arg.common import description
from testflows.core.cli.arg.common import RawDescriptionHelpFormatter
from testflows.core.cli.arg.handlers.log.handler import Handler as log_handler

class ArgumentParser(ArgumentParserBase):
    """Customized argument parser.
    """
    def __init__(self, *args, **kwargs):
        kwargs["epilog"] = kwargs.pop("epilog", epilog())
        kwargs["description"] = kwargs.pop("description", description())
        kwargs["formatter_class"] = kwargs.pop("formatter_class", RawDescriptionHelpFormatter)
        return super(ArgumentParser, self).__init__(*args, **kwargs)

parser = ArgumentParser(prog="tfs")

commands = parser.add_subparsers(title='commands', metavar='command', description=None, help=None)
log_handler.add_command(commands)