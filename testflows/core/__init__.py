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
from .constants import *
from .test import *

__version__ = "1.2.__VERSION__"

def cleanup():
    """Clean up old temporary log files.
    """
    import os
    import re
    import glob
    import tempfile

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

def stdout_handler():
    import threading

    from testflows.core.transform.log.read import transform as read_transform
    from testflows.core.transform.log.parse import transform as parse_transform
    from testflows.core.transform.log.nice import transform as nice_transform
    from testflows.core.transform.log.write import transform as write_transform
    from testflows.core.transform.log.stop import transform as stop_transform

    stop_event = threading.Event()

    def pipeline(input, output):
        steps = [
            read_transform(input, tail=True),
            parse_transform(stop_event),
            nice_transform(),
            write_transform(output),
            stop_transform(stop_event)
        ]
        # start all the generators
        for step in steps:
            next(step)
        return steps

    tmp_logfile = os.path.join(tempfile.gettempdir(), f"testflows.{os.getpid()}.log")

    with open(tmp_logfile, "a+", buffering=1) as log:
        log.seek(0)
        steps = pipeline(log, sys.stdout)
        item = None
        while True:
            try:
                for step in steps:
                    while True:
                        item = step.send(item)
                        if item is not None:
                            break
            except StopIteration:
                break

def main():
    """Return true if caller is the main module.
    """
    import threading
    cleanup()

    handler = threading.Thread(target=stdout_handler)
    handler.name = "tfs-output"
    handler.start()

    frame = inspect.currentframe().f_back
    return frame.f_globals["__name__"] == "__main__"
