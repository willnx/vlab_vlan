# -*- coding: UTF-8 -*-
"""
Defines the HTTP API for working with vLANs in vLab
"""
import ujson
from flask import current_app
from flask_classy import request, route
from jsonschema import validate, ValidationError
from vlab_inf_common.views import TaskView
from vlab_api_common import describe, get_logger, requires, validate_input

from vlab_vlan.lib import const

logger = get_logger(__name__, loglevel=const.VLAB_VLAN_LOG_LEVEL)


class VlanView(TaskView):
    """Defines the HTTP API for working with virtual local area networks"""
    route_base = 'api/1/inf/vlan'
    POST_SCHEMA = { "$schema": "http://json-schema.org/draft-04/schema#",
                    "type": "object",
                    "properties": {
                        "vlan-name": {
                            "description": "The base name of the new vLAN",
                            "type": "string"
                        },
                        "switch-name": {
                            "description": "The switch to configure for the new vLAN",
                            "type": "string"
                        }
                    },
                    "required":[
                        "vlan-name",
                        "switch-name"
                    ]
                  }
    DELETE_SCHEMA = { "$schema": "http://json-schema.org/draft-04/schema#",
                      "type": "object",
                      "properties": {
                          "vlan-name": {
                              "description": "The base name of the vlan to destroy",
                              "type": "string"
                          }
                      },
                      "required":[
                        "vlan-name"
                      ]
                    }

    @requires(verify=False)
    @describe(post=POST_SCHEMA, delete=DELETE_SCHEMA, get_args={})
    def get(self, *args, **kwargs):
        """Obtain a info about the vlans a user owns"""
        username = kwargs['token']['username']
        resp = {'user' : username}
        task = current_app.celery_app.send_task('vlan.show', [username])
        resp['content'] = {'task-id': task.id}
        return ujson.dumps(resp), 200

    @requires(verify=False) # XXX remove verify=False before commit
    @validate_input(schema=POST_SCHEMA)
    def post(self, *args, **kwargs):
        """Create a new vlan"""
        username = kwargs['token']['username']
        vlan_name = kwargs['body']['vlan-name']
        switch_name = kwargs['body']['switch-name']
        return _dispatch_modify(username=username, the_task='vlan.create', vlan_name=vlan_name, switch_name=switch_name)

    @requires(verify=False) # XXX remove verify=False before commit
    @validate_input(schema=DELETE_SCHEMA)
    def delete(self, *args, **kwargs):
        """Delete a lvan"""
        username = kwargs['token']['username']
        vlan_name = kwargs['body']['vlan-name']
        return _dispatch_modify(username=username, the_task='vlan.delete', vlan_name=vlan_name)


def _dispatch_modify(username, the_task, **kwargs):
    """Send the task to Celery that makes or destroys a vlan

    :Returns: Tuple - http body, http status

    :param username: The name of the caller performing the action
    :type username: String

    :param the_task: The name of the task to dispatch
    :type the_task: String

    :param kwargs: The arguments to send to the back-end task, by key-word.
    :type kwargs:
    """
    assert the_task in ('vlan.create', 'vlan.delete')
    resp = {'user': username}
    task = current_app.celery_app.send_task(the_task, args=[username], kwargs=kwargs)
    resp['content'] = {'task-id': task.id}
    return ujson.dumps(resp), 200