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
import time

class Timer(object):
    """Simple timer."""
    def __init__(self, timeout):
        self.timeout = timeout
        self.started = time.time()
        self.stopped = False
        self.stopped_time = None

    def reset(self):
        """Reset timer."""
        self.stopped = False
        self.stopped_time = None
        self.started = time.time()

    def stop(self):
        """Stop timer."""
        self.stopped_time = self.time()
        self.stopped = True

    def time(self):
        """Return timer value."""
        if self.stopped:
            return self.stopped_time
        elapsed = time.time() - self.started
        value = max(self.timeout - elapsed, 0)
        return value