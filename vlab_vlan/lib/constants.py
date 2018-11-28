# -*- coding: UTF-8 -*-
from os import environ
from collections import namedtuple, OrderedDict


DEFINED = OrderedDict([
            ('VLAB_URL', environ.get('VLAB_URL', 'https://localhost')),
            ('INF_VCENTER_SERVER', environ.get('INF_VCENTER_SERVER', 'localhost')),
            ('INF_VCENTER_PORT', int(environ.get('INFO_VCENTER_PORT', 443))),
            ('INF_VCENTER_USER', environ.get('INF_VCENTER_USER', 'tester')),
            ('INF_VCENTER_PASSWORD', environ.get('INF_VCENTER_PASSWORD', 'a')),
            ('VLAB_VLAN_LOG_LEVEL', environ.get('VLAB_VLAN_LOG_LEVEL', 'INFO')),
            ('VLAB_MESSAGE_BROKER', environ.get('VLAB_MESSAGE_BROKER', 'vlan-broker')),
            ('INF_DB_HOSTNAME', environ.get('INF_DB_HOSTNAME', 'vlan-db')),
            ('POSTGRES_PASSWORD', environ.get('POSTGRES_PASSWORD', 'testing')),
            ('VLAB_VERIFY_TOKEN', environ.get('VLAB_VERIFY_TOKEN', False)),
          ])

Constants = namedtuple('Constants', list(DEFINED.keys()))

# The '*' expands the list, just liked passing a function *args
const = Constants(*list(DEFINED.values()))
