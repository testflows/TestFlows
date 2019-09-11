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
from setuptools import setup

setup(
    name="testflows.core",
    version="__VERSION__",
    description="TestFlows - Core",
    author="Vitaliy Zakaznikov",
    author_email="vzakaznikov@testflows.com",
    url="http://testflows.com",
    license="Apache-2.0",
    packages=[
        "testflows.settings",
        "testflows.core",
        "testflows.core.contrib",
        "testflows.core.utils",
        "testflows.core.transform",
        "testflows.core.transform.log",
        "testflows.core.cli",
        "testflows.core.cli.arg",
        "testflows.core.cli.arg.handlers",
        "testflows.core.cli.arg.handlers.log"
        ],
    scripts=[
        "testflows/core/bin/tfs",
    ],
    zip_safe=False,
    install_requires=[
    ],
    extras_require={
        "dev": [
            "sphinx",
        ]
    }
)
