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
import re
import time

from datetime import timedelta
from datetime import datetime

def strftime(dt):
    """Return string representation of datetime.
    """
    return f"{dt:%b %d,%Y %-H:%M:%S%z}"

def localfromtimestamp(timestamp):
    """Convert UTC timestamp to local time.

    :param timestamp: UTC timestamp
    """
    utctime = datetime.utcfromtimestamp(timestamp)
    offset = datetime.fromtimestamp(timestamp) - utctime
    return utctime + offset

def timestamp():
    """Return epoch timestamp."""
    return time.time()

def timestampfromlocal(local):
    """Convert local date time to timestamp.

    :param local: local datetime
    """
    return local.timestamp()

def timestampfromutc(utc):
    """Convert UTC date time to timestamp.

    :param utc: UTC datetime
    """
    return (utc - datetime(1970, 1, 1)).total_seconds()

def strftimedelta(td, format=None):
    """Return string representation of timedelta.

    :param td: timedelta
    """
    if isinstance(td, (int, float)):
        td = timedelta(seconds=td)
    days = td.days
    hours, left = divmod(int(td.total_seconds()) - (days * 24 * 3600), 3600)
    min, sec = divmod(left, 60)
    ms_float = (td.total_seconds() % 1) * 1000
    ms = int(ms_float)
    us_float = ((ms_float % 1) * 1000)
    us = int(us_float)

    if format is None:
        format = "{days}d {hours}h {min}m"
        if days > 0:
            format = "{days}d {hours}h"
        elif hours > 0:
            format = "{hours}h {min}m"
        elif min > 0:
            format = "{min}m {sec}s"
        elif sec > 0:
            format = "{sec}s {ms}ms"
        elif ms > 0:
            format = "{ms}ms"
        else:
            format = "{us}us"

    return format.format(**{
        "days": days,
        "hours": hours,
        "min": min,
        "sec": sec,
        "ms": ms,
        "us": us
    })

def strptimedelta(timelapse):
    """Parse string into timedelta.

    Supported format:
        1[d,day,days]1h[r]1m11[.111]s1ms10us

    :param timelapse: timelapse string
    """
    parser = re.compile(r'('
        '((?P<days>\d+)d|day|days)?'
        '((?P<hours>\d+)hr?)?'
        '((?P<min>\d+)m(?!s))?'
        '((?P<sec>(\d+.\d+)|(\d+))s)?'
        '((?P<ms>\d+)ms)?'
        '((?P<us>\d+)us)?'
    ')?$')

    match = parser.match(s)
    if match is None:
        raise ValueError("'%s' time delta string has invalid format" % timelapse)
    match = match.groupdict()

    args = {}
    for name, value in match.items():
        if not value:
            continue
        if name == "min":
            args["minutes"] = int(value)
        elif name == "sec":
            args["seconds"] = float(value)
        elif name == "ms":
            args["seconds"] = args.get("seconds", 0) + int(value) / 1000.0
        elif name == "us":
            args["seconds"] = args.get("seconds", 0) + int(value) / 1000000.0
        else:
            args[name] = int(value)

    return timedelta(**args)
