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
class Handler(object):
    def __init__(self):
        pass

    def __call__(self, args):
        return self.handle(args)

    @classmethod
    def add_arguments(cls, parser):
        pass

    @classmethod
    def add_command(self, commands):
        raise NotImplementedError

    def handle(self):
        pass
