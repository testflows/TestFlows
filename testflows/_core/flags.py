# Copyright 2019 Vitaliy Zakaznikov
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
# to the end flag
TE = 1 << 0
# utility test flag
UT = 1 << 1
# skip flag
SKIP = 1 << 2
# expected OK
EOK = 1 << 3
# expected Fail
EFAIL = 1 << 4
# expected Error
EERROR = 1 << 5 
# expected Skip
ESKIP = 1 << 6
# crossed out ok
XOK = 1 << 7
# crossed out fail
XFAIL = 1 << 8
# crossed out error
XERROR = 1 << 9
# crossed out null
XNULL = 1 << 10
# not counted fail
FAIL_NOT_COUNTED = 1 << 11
# not counted error
ERROR_NOT_COUNTED = 1 << 12
# not counted null
NULL_NOT_COUNTED = 1 << 13
# pause before test execution
PAUSE_BEFORE = 1 << 14
PUASE = PAUSE_BEFORE
# pause after test execution
PAUSE_AFTER = 1 << 15
# report flag
REP = 1 << 26
# documentation
DOC = 1 << 27
# mandatory test
MAN = 1 << 28
# clear flags mask
CLR = 1 << 31
# expected result
ERESULT = EOK | EFAIL | ESKIP | EERROR 
# expected any result
EANY = EOK | EFAIL | ESKIP
# crossed out result
XRESULT = XOK | XFAIL | XERROR | XNULL
# not counted
NOT_COUNTED = FAIL_NOT_COUNTED
NOT_COUNTED_ANY = FAIL_NOT_COUNTED | ERROR_NOT_COUNTED | NULL_NOT_COUNTED
# cumulative flags
CFLAGS = UT

class Flags(object):
    """Test flags."""
    all = [
            TE, UT, SKIP, EOK, EFAIL, EERROR, ESKIP,
            XOK, XFAIL, XERROR, XNULL,
            FAIL_NOT_COUNTED, ERROR_NOT_COUNTED, NULL_NOT_COUNTED,
            PAUSE_BEFORE, PAUSE_AFTER,
            REP, DOC, MAN, CLR
        ]
    all_str = [
            "TE", "UT", "SKIP", "EOK", "EFAIL", "EERROR", "ESKIP",
            "XOK", "XFAIL", "XERROR", "XNULL",
            "FAIL_NOT_COUNTED", "ERROR_NOT_COUNTED", "NULL_NOT_COUNTED",
            "PAUSE_BEFORE", "PAUSE_AFTER",
            "REP", "DOC", "MAN", "CLR"
        ]
    
    def __init__(self, flags=0):
        if flags is None:
            flags = 0
        if type(flags) is str:
            self.flags = 0
            if flags:
                for flag in [self.all[self.all_str.index(f)] for f in flags.split("|")]:
                    self.flags |= flag
        else:
            self.flags = int(flags)
    
    def __str__(self):
        l = [self.all_str[self.all.index(f)] for f in self.all if self.flags & f == f]
        return "|".join(l) or ""

    def __repr__(self):
        return "Flags('" + str(self) + "')"

    def __bool__(self):
        return bool(self.flags)

    def __int__(self):
        return self.flags

    def __and__(self, o):
        return Flags(self.flags & int(Flags(o)))
    
    def __or__(self, o):
        return Flags(self.flags | int(Flags(o)))
    
    def __xor__(self, o):
        return Flags(self.flags ^ int(Flags(o)))
    
    def __invert__(self):
        return Flags(~self.flags)
    
    def __contains__(self, o):
        return bool(self & o)

    def __eq__(self, o):
        return self.flags == int(Flags(o))

    def __ne__(self, o):
        return not self == o
