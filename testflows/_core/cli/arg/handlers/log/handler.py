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
from testflows._core.cli.arg.common import epilog
from testflows._core.cli.arg.common import RawDescriptionHelpFormatter
from testflows._core.cli.arg.handlers.handler import Handler as HandlerBase
from testflows._core.cli.arg.handlers.log.nice import Handler as nice_handler
from testflows._core.cli.arg.handlers.log.short import Handler as short_handler

class Handler(HandlerBase):
    @classmethod
    def add_command(cls, commands):
        parser = commands.add_parser("log", help="log processing", epilog=epilog(),
            description="Work with logs.",
            formatter_class=RawDescriptionHelpFormatter)

        log_commands = parser.add_subparsers(title="commands", metavar="command",
            description=None, help=None)
        log_commands.required = True
        nice_handler.add_command(log_commands)
        short_handler.add_command(log_commands)
