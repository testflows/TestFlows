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
from testflows._core.cli.colors import color

def primary(text, eol="\n"):
    return color(text + eol, "white", attrs=["bold"])

def secondary(text, eol="\n"):
    return color(text + eol, "white", attrs=["dim"])

def danger(text, eol="\n"):
    return color(text + eol, "red", attrs=["bold"])

def success(text, eol="\n"):
    return color(text + eol, "green", attrs=["bold"])

def warning(text, eol="\n"):
    return color(text + eol, "yellow", attrs=["bold"])

def info(text, eol="\n"):
    return color(text + eol, "blue", attrs=["bold"])

