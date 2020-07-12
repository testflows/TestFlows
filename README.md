# TestFlows Open-Source Software Testing Framework

**TestFlows is still work in progress and is currently under development.
Please use it only for reference.**

![TestFlows](https://raw.githubusercontent.com/testflows/TestFlows-ArtWork/master/images/logo.png)

## Introduction

[TestFlows] is a **flow** oriented test framework that can be used for functional,
integration, acceptance and unit testing. It uses **everything is a test** approach
with the focus on providing test designers flexibility in writing and running their tests.

## Documentation

You can find [TestFlows]'s documentation at https://testflows.com.

## Supported environment

* [Ubuntu] 18.04
* [Python 3] >= 3.6

## Installation

You can install [TestFlows] using [pip3]

```bash
$ pip3 install testflows
```

or from sources

```bash
$ git clone https://github.com/testflows/TestFlows.git
$ cd TestFlows
$ ./build ; ./install
```

## Styles

[TestFlows] supports defining tests using either the traditional keywords

*  **Module**, **Suite**, **Test**, and **Step**

or using keywords such as

* **Module**, **Feature**, **Scenario**, **Given**, **When**, **Then**, **But**, **And**, **By** and **Finally**

## Hello TestFlows

An inline test scenario can be defined as follows

```python
from testflows.core import Scenario

with Scenario("Hello TestFlows!"):
    pass
```

then just run it using `python3` command

```bash
$ python3 ./test.py 
Jul 12,2020 14:30:20   ⟥  Scenario Hello TestFlows!
                 1ms   ⟥⟤ OK Hello TestFlows!, /Hello TestFlows!

Passing

✔ [ OK ] /Hello TestFlows!

1 scenario (1 ok)

Total time 2ms

Executed on Jul 12,2020 14:30
TestFlows Test Framework v1.6.200712.1132037
```

## What to know more?

Find more information about [TestFlows] at https://testflows.com.   
Join our channel on [Telegram] or follow us on [Twitter].

[TestFlows]: https://testflows.com
[Telegram]: https://telegram.me/testflows
[Twitter]: https://twitter.com/TestFlowsTF
[TestFlows]: https://github.com/testflows/testflows
[pip3]: https://github.com/pypa/pip
[Python 3]: https://www.python.org/
[Ubuntu]: https://ubuntu.com/ 
