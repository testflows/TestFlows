# TestFlows.com Open-Source Software Testing Framework

**TestFlows.com Open-Source Software Testing Framework is still work in progress and is currently under development.
Please use it only for reference.**

![TestFlows.com Open-Source Software Testing Framework](https://raw.githubusercontent.com/testflows/TestFlows-ArtWork/master/images/logo.png)

## Introduction

[TestFlows.com Open-Source Software Testing Framework] is a **flow** oriented test framework that can be used for functional,
integration, acceptance and unit testing. It uses **everything is a test** approach
with the focus on providing test designers flexibility in writing and running their tests.

## Documentation

You can find [TestFlows.com Open-Source Software Testing Framework]'s documentation at https://testflows.com.

## Supported environment

* [Ubuntu] 20.04
* [Python 3] >= 3.8

## Installation

You can install [TestFlows.com Open-Source Software Testing Framework] using [pip3]

```bash
$ pip3 install testflows
```

or from sources

```bash
$ git clone https://github.com/testflows/TestFlows.git
$ cd TestFlows
$ ./build && ./install
```

## Styles

[TestFlows.com Open-Source Software Testing Framework] supports defining tests using either the traditional keywords

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
TestFlows.com Open-Source Software Testing Framework v1.6.200712.1132037
```

## Want to know more?

Find more information about [TestFlows.com Open-Source Software Testing Framework] at https://testflows.com.   
Join our channel on [Telegram].

[TestFlows.com Open-Source Software Testing Framework]: https://testflows.com
[Telegram]: https://telegram.me/testflows
[pip3]: https://github.com/pypa/pip
[Python 3]: https://www.python.org/
[Ubuntu]: https://ubuntu.com/ 
