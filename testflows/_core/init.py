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
import re
import sys
import glob
import tempfile
import threading

import testflows.settings as settings

from .transform.log.pipeline import RawLogPipeline
from .transform.log.pipeline import NiceLogPipeline
from .transform.log.pipeline import DotsLogPipeline
from .transform.log.pipeline import ShortLogPipeline

def cleanup():
    """Clean up old temporary log files.
    """
    parser = re.compile(r".*testflows.(?P<pid>\d+).log")

    def pid_exists(pid):
        """Check if pid is alive on UNIX.

        :param pid: pid
        """
        # NOTE: pid == 0 returns True
        if pid < 0: return False
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            # errno.ESRCH - no such process
            return False
        except PermissionError:
            # errno.EPERM - operation not permitted (i.e., process exists)
            return True
        else:
            #  no error, we can send a signal to the process
            return True

    for file in glob.glob(os.path.join(tempfile.gettempdir(), "testflows.*.log")):
        match = parser.match(file)
        if not match:
            continue
        pid = int(match.groupdict()['pid'])
        if not pid_exists(pid):
            try:
                os.remove(file)
            except OSError:
                raise

def stdout_raw_handler():
    """Handler to output messages to sys.stdout
    using "raw" format.
    """
    with open(settings.read_logfile, "a+", buffering=1, encoding="utf-8") as log:
        log.seek(0)
        RawLogPipeline(log, sys.stdout, tail=True).run()

def stdout_short_handler():
    """Handler to output messages to sys.stdout
    using "short" format.
    """
    with open(settings.read_logfile, "a+", buffering=1, encoding="utf-8") as log:
        log.seek(0)
        ShortLogPipeline(log, sys.stdout, tail=True).run()

def stdout_nice_handler():
    """Handler to output messages to sys.stdout
    using "nice" format.
    """
    with open(settings.read_logfile, "a+", buffering=1, encoding="utf-8") as log:
        log.seek(0)
        NiceLogPipeline(log, sys.stdout, tail=True).run()

def stdout_dots_handler():
    """Handler to output messages to sys.stdout
    using "dots" format.
    """
    with open(settings.read_logfile, "a+", buffering=1, encoding="utf-8") as log:
        log.seek(0)
        DotsLogPipeline(log, sys.stdout, tail=True).run()

def stdout_silent_handler():
    """Handler that prints no output to sys.stdout.
    """
    pass

def init():
    """Initialization before we run the first test.
    """
    cleanup()

    output_handler_map = {
        "raw": stdout_raw_handler,
        "nice": stdout_nice_handler,
        "silent": stdout_silent_handler,
        "quiet": stdout_silent_handler,
        "short": stdout_short_handler,
        "dots": stdout_dots_handler,
    }
    # start stdout output handler
    handler = threading.Thread(target=output_handler_map[settings.output_format])
    handler.name = "tfs-output"
    handler.start()
