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
import threading

from .read import transform as read_transform
from .parse import transform as parse_transform
from .nice import transform as nice_transform
from .write import transform as write_transform
from .stop import transform as stop_transform
from .raw import transform as raw_transform
from .short import transform as short_transform

class Pipeline(object):
    """Combines multiple steps into a pipeline
    that can be executed.
    """
    def __init__(self, steps):
        self.steps = steps
        # start all the generators
        for step in self.steps:
            next(step)

    def run(self):
        """Execute pipeline.
        """
        item = None
        while True:
            try:
                for step in self.steps:
                    item = step.send(item)
                    if item is None:
                        break
            except StopIteration:
                break

class RawLogPipeline(Pipeline):
    def __init__(self, input, output, tail=False):
        stop_event = threading.Event()

        steps = [
            read_transform(input, tail=tail),
            raw_transform(stop_event),
            write_transform(output),
            stop_transform(stop_event)
        ]
        super(RawLogPipeline, self).__init__(steps)

class ShortLogPipeline(Pipeline):
    def __init__(self, input, output, tail=False):
        stop_event = threading.Event()

        steps = [
            read_transform(input, tail=tail),
            parse_transform(stop_event),
            short_transform(),
            write_transform(output),
            stop_transform(stop_event)
        ]
        super(ShortLogPipeline, self).__init__(steps)

class NiceLogPipeline(Pipeline):
    def __init__(self, input, output, tail=False):
        stop_event = threading.Event()

        steps = [
            read_transform(input, tail=tail),
            parse_transform(stop_event),
            nice_transform(),
            write_transform(output),
            stop_transform(stop_event)
        ]
        super(NiceLogPipeline, self).__init__(steps)
