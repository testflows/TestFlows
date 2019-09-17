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
from .exceptions import RequirementError
from .baseobject import TestObject, TestArg
from .baseobject import get, hash

class Result(TestObject):
    _fields = ("test", "message")
    _defaults = (None,)

    def __init__(self, test, message=None):
        self.test = test
        self.message = message
        return super(Result, self).__init__()

    def __eq__(self, o):
        return type(self) == o
  
    def __ne__(self, o):
        return not self == o

class OK(Result):
    def __init__(self, test, message=None):
        return super(OK, self).__init__(test, message=message)
    
    def __bool__(self):
        return True

class Fail(Result):
    def __init__(self, test, message=None):
        return super(Fail, self).__init__(test, message=message)

    def __bool__(self):
        return False

class Skip(Result):
    def __init__(self, test, message=None):
        return super(Skip, self).__init__(test, message=message)

    def __bool__(self):
        return True

class Error(Result):
    def __init__(self, test, message=None):
        return super(Error, self).__init__(test, message=message)

    def __bool__(self):
        return False

class Null(Result):
    def __init__(self, test):
        return super(Null, self).__init__(test, message=None)

    def __bool__(self):
        return False

class Argument(TestObject):
    _fields = ("name", "value", "group", "type", "uid")
    _defaults = (None,) * 3
    uid = None
    type = None
    group = None

    def __init__(self, name, value, type=None, group=None, uid=None):
        self.name = name
        self.value = value
        self.type = get(type, self.type)
        self.group = get(group, self.group)
        self.uid = get(uid, self.uid)
        return super(Argument, self).__init__()

class Attribute(TestObject):
    _fields = ("name", "value", "type", "group", "uid")
    _defaults = (None,) * 3
    uid = None
    type = None
    group = None
    
    def __init__(self, name, value, type=None, group=None, uid=None):
        self.name = name
        self.value = value
        self.type = get(type, self.type)
        self.group = get(group, self.group)
        self.uid = get(uid, self.uid)
        return super(Attribute, self).__init__()

class Requirement(TestObject):
    _fields = ("name", "revision", "description",
            "link", "priority", "type", "group", "uid")
    _defaults = (None,) * 6
    uid = None
    link = None
    priority = None
    type = None
    group = None
    
    def __init__(self, name, revision, description=None, link=None,  
            priority=None, type=None, group=None, uid=None):
        self.name = name
        self.revision = revision
        self.description = get(description, self.__doc__)
        self.link = get(link, self.link)
        self.priority = get(priority, self.priority)
        self.type = get(type, self.type)
        self.group = get(group, self.group)
        self.uid = get(uid, self.uid)
        return super(Requirement, self).__init__()  

    def __call__(self, *revision):
        if not self.revision in revision:
            raise RequirementError("requirement revision %s is not in %s" % (self.revision, list(revision)))
        return self

class Measurement(TestObject):
    _fields = ("name", "value", "units", "type", "group", "uid")
    _defaults = (None,) * 3
    uid = None
    type = None
    group = None
    
    def __init__(self, name, value, units, type=None, group=None, uid=None):
        self.name = name
        self.value = value
        self.units = units
        self.type = get(type, self.type)
        self.group = get(group, self.group)
        self.uid = get(uid, self.uid)
        return super(Measurement, self).__init__()

class Output(TestObject):
    _fields = ("name", "value", "type", "group", "uid")
    _defaults = (None,) * 3
    uid = None
    type = None
    group = None

    def __init__(self, name, value, type=None, group=None, uid=None):
        self.name = name
        self.value = value
        self.type = get(type, self.type)
        self.group = get(group, self.group)
        self.uid = get(uid, self.uid)
        return super(Output, self).__init__()

class Project(TestObject):
    _fields = ("name", "type", "group", "uid",
        "tags", "attributes")
    _defaults = (None,) * 5
    uid = None
    type = None
    group = None
    tags = []
    attributes = []
    
    def __init__(self, name, type=None, group=None, tags=None, attributes=None, uid=None):
        self.name = name
        self.type = get(type, self.type)
        self.group = get(group, self.group)
        self.tags = get(tags, self.tags)
        self.attributes = get(attributes, self.attributes)
        self.uid = get(uid, self.uid)
        return super(Project, self).__init__()

class Ticket(TestObject):
    _fields = ("name", "link", "type", "group", "uid")
    _defaults = (None,) * 4
    uid = None
    link = None
    type = None
    group = None
    
    def __init__(self, name, link=None, type=None, group=None, uid=None):
        self.name = name
        self.link = get(link, self.link)
        self.type = get(type, self.type)
        self.group = get(group, self.group)
        self.uid = get(uid, self.uid)
        return super(Ticket, self).__init__()

class User(TestObject):
    _fields = ("name", "type", "group", "link", "uid",
        "tags", "attributes")
    _defaults = (None,) * 6
    uid = None
    link = None
    type = None
    group = None
    tags = []
    attributes = []
    
    def __init__(self, name, link=None, type=None, group=None, tags=None, attributes=None, uid=None):
        self.name = name
        self.link = get(link, self.link)
        self.type = get(type, self.type)
        self.group = get(group, self.group)
        self.tags = get(tags, self.tags)
        self.attributes = get(attributes, self.attributes)
        self.uid = get(uid, self.uid)
        return super(User, self).__init__()

class Environment(TestObject):
    _fields = ("name", "type", "group", "uid",
        "tags", "attributes", "devices")
    _defaults = (None,) * 6
    uid = None
    type = None
    group = None
    tags = []
    attributes = []
    devices = []

    def __init__(self, name, type=None, group=None, tags=None, attributes=None,
            devices=None, uid=None):
        self.name = name
        self.type = get(type, self.type)
        self.group = get(group, self.group)
        self.tags = get(tags, self.tags)
        self.attributes = get(attributes, self.attributes)
        self.devices = get(devices, self.devices)
        self.uid = get(uid, self.uid)
        return super(User, self).__init__()

class Device(TestObject):
    _fields = ("name", "type", "group", "tags", "uid",
        "attributes", "requirements",
        "software", "hardware")
    _defaults = (None,) * 7
    uid = None
    type = None
    group = None
    tags = []
    attributes = []
    requirements = []
    software = []
    hardware = []
    
    def __init__(self, name, type=None, group=None, tags=None,
            attributes=None, requirements=None,
            software=None, hardware=None, uid=None):
        self.name = name
        self.type = get(type, self.type)
        self.group = get(group, self.group)
        self.tags = get(tags, self.tags)
        self.attributes = get(attributes, self.attributes)
        self.requirements = get(requirements, self.requirements)
        self.software = get(software, self.software)
        self.hardware = get(hardware, self.hardware)
        self.uid = get(uid, self.uid)
        return super(Device, self).__init__()

class Software(TestObject):
    _fields = ("name", "type", "group", "uid",
        "tags", "attributes", "requirements")
    _defaults = (None,) * 5
    uid = None
    type = None
    group = None
    tags = []
    attributes = []
    requirements = []

    def __init__(self, name, type=None, group=None, tags=None,
            attributes=None, requirements=None, uid=None):
        self.name = name
        self.type = get(type, self.type)
        self.group = get(group, self.group)
        self.tags = get(tags, self.tags)
        self.attributes = get(attributes, self.attributes)
        self.requirements = get(requirements, self.requirements)
        self.uid = get(uid, self.uid)
        return super(Software, self).__init__()

class Hardware(TestObject):
    _fields = ("name", "type", "group", "uid",
        "tags", "attributes", "requirements")
    _defaults = (None,) * 5
    uid = None
    type = None
    group = None
    tags = []
    attributes = []
    requirements = []

    def __init__(self, name, type=None, group=None, tags=None,
            attributes=None, requirements=None, uid=None):
        self.name = name
        self.type = get(type, self.type)
        self.group = get(group, self.group)
        self.tags = get(tags, self.tags)
        self.attributes = get(attributes, self.attributes)
        self.requirements = get(requirements, self.requirements)
        self.uid = get(uid, self.uid)
        return super(Hardware, self).__init__()

class Job(TestObject):
    _fields = ("name", "type", "group",
        "tags", "user",
        "attributes", "requirements", "uid")
    _defaults = (None,) * 5
    uid = None
    user = None
    type = None
    group = None
    tags = []
    attributes = []
    requirements = []
    
    def __init__(self, name, user, type=None, group=None, tags=None,
            attributes=None, requirements=None, uid=None):
        self.name = name
        self.user = user
        self.type = get(type, self.type)
        self.group = get(group, self.group)
        self.tags = get(tags, self.tags)
        self.attributes = get(attributes, self.attributes)
        self.requirements = get(requirements, self.requirements)
        self.uid = get(uid, self.uid)
        return super(Software, self).__init__()
