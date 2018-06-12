# -*- coding: UTF-8 -*-
"""
This module defines all tasks for creating, deleting, listing virtual vLANs.

All responses from a task *MUST* be a dictionary, and *MUST* contain the following
keys:

- ``error``  An error message about bad user input,or None
- ``params`` The parameters provided by the user, or an empty dictionary
- ``content`` The resulting output from running a task, or an empty dictionary

Example:

.. code-block:: python

   # If everything works
   {'error' : None,
    'content' : {'vlan' : 24, 'name': 'bob_FrontEnd'}
    'params' : {'vlan-name' : 'FrontEnd'}
   }
   # If bad params are provided
   {'error' : "Valid parameters are foo, bar, baz",
    'content' : {},
    'params' : {'doh': 'Not a valid param'}
   }

"""
from celery import Celery
from vlab_api_common import get_logger
from vlab_inf_common.vmware import vCenter

from vlab_vlan.lib.worker import database
from vlab_vlan.lib.worker.vmware import create_network, delete_network
from vlab_vlan.lib import const

app = Celery('vlan', backend='rpc://', broker=const.VLAB_MESSAGE_BROKER)
logger = get_logger(__name__, loglevel=const.VLAB_VLAN_LOG_LEVEL)


@app.task(name='vlan.show')
def list(username):
    """List all vLANs owned by the user

    :Returns: Dictionary

    :param username: The name of the user who wants a list of their vLANs.
    :type username: String
    """
    resp = {'content' : {}, 'error' : None, 'params' : {}}
    resp['content'] = database.get_vlan(username)
    return resp


@app.task(name='vlan.delete')
def delete(username, vlan_name):
    """Delete a vLAN owned by the user.

    :Returns: Dictionary

    :param username: The name of the user who wants to destroy a vLAN.
    :type username: String

    :param vlan_name: The kind of vLAN to make, like FrontEnd or BackEnd
    :type vlan_name: String
    """
    resp = {'error' : None, 'content': {},
            'params': {'vlan_name': vlan_name}}

    owns = database.get_vlan(username).get(vlan_name, None)
    if not owns:
        resp['error'] = "Unable to delete vLAN you do not own"
        return resp
    try:
        delete_network(vlan_name)
    except ValueError as doh:
        resp['error'] = '{}'.format(doh)
        return resp
    try:
        database.delete_vlan(username=username, vlan_name=vlan_name)
    except (RuntimeError, ValueError) as doh:
        resp['error'] = '{}'.format(doh)
    return resp


@app.task(name='vlan.create')
def create(username, vlan_name, switch_name):
    """Create a vLAN for the user.

    :Returns: Dictionary

    :param username: The name of the user who wants to create a vLAN
    :type username: String

    :param vlan_name: The kind of vLAN to make, like FrontEnd or BackEnd
    :type vlan_name: String
    """
    resp = {'error' : None, 'content': {},
            'params': {'vlan_name': vlan_name, 'switch_name': switch_name}}
    try:
        vlan_tag_id = database.register_vlan(username=username, vlan_name=vlan_name)
    except ValueError as doh:
        resp['error'] = '{}'.format(doh)
        return resp

    try:
        error = create_network(vlan_name, vlan_tag_id, switch_name)
    except ValueError as doh:
        resp['error'] = '{}'.format(doh)
    else:
        resp['error'] = error
    if resp['error']:
        try:
            # Delete the record in the DB to keep VMware & the DB records in sync
            # otherwise, we'll leak vLAN tag ids
            database.delete_vlan(username=username, vlan_name=vlan_name)
        except Exception as doh:
            logger.traceback(doh)
    return resp
