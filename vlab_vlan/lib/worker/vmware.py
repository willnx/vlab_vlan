# -*- coding: UTF-8 -*-
"""
This module abstracts the VMware API for creating/deleting Distributed Virtual Portgroups.
"""
from vlab_inf_common.vmware import vCenter, vim, consume_task

from vlab_vlan.lib import const


def create_network(name, vlan_id, switch_name):
    """Create a new network for VMs.

    :Returns: String (error message)

    :param name: The name of the new distributed virtual portgroup
    :type name: String

    :param vlan_id: The vLAN tag id of the new dv portgroup
    :type vlan_id: Integer

    :param switch_name: The name of the switch to add the new vLAN network to
    :type switch_name: String
    """
    with vCenter(host=const.INF_VCENTER_SERVER, user=const.INF_VCENTER_USER,\
                password=const.INF_VCENTER_PASSWORD) as vcenter:
        try:
            switch = vcenter.dv_switches[switch_name]
        except KeyError:
            available = list(vcenter.dv_switches.keys())
            msg = 'No such switch: {}, Available: {}'.format(switch_name, available)
            raise ValueError(msg)
        spec = get_dv_portgroup_spec(name, vlan_id)
        task = switch.AddDVPortgroup_Task([spec])
        try:
            consume_task(task, timeout=300)
            error = ''
        except RuntimeError as doh:
            error = '{}'.format(doh)
        return error


def delete_network(name):
    """Destroy a vLAN network

    :Returns: None

    :Raises: ValueError

    :param name: The name of the network to destroy
    :type name: String
    """
    with vCenter(host=const.INF_VCENTER_SERVER, user=const.INF_VCENTER_USER, \
                password=const.INF_VCENTER_PASSWORD) as vcenter:
        try:
            network = vcenter.networks[name]
        except KeyError:
            msg = 'No such vLAN exists: {}'.format(name)
            raise ValueError(msg)
        try:
            task = network.Destroy_Task()
            consume_task(task, timeout=300)
        except vim.fault.ResourceInUse:
            msg = "Unable to delete vLAN when Virtual Machines(es) are configured to use it"
            raise ValueError(msg)


def get_dv_portgroup_spec(name, vlan_id):
    """Obtain a creation specification for a new DV Portgroup. The spec created
    is for Virtual Switch vLAN Tagging (VST).

    :Returns: vim.dvs.DistributedVirtualPortgroup.ConfigSpec

    :param name: The name of the new distributed virtual portgroup
    :type name: String

    :param vlan_id: The vLAN tag id of the new dv portgroup
    :type vlan_id: Integer
    """

    spec = vim.dvs.DistributedVirtualPortgroup.ConfigSpec()
    spec.name = name

    spec.type = vim.dvs.DistributedVirtualPortgroup.PortgroupType.ephemeral

    spec.defaultPortConfig = vim.dvs.VmwareDistributedVirtualSwitch.VmwarePortConfigPolicy()
    spec.defaultPortConfig.vlan = vim.dvs.VmwareDistributedVirtualSwitch.VlanIdSpec()
    spec.defaultPortConfig.vlan.vlanId = vlan_id

    spec.defaultPortConfig.securityPolicy = vim.dvs.VmwareDistributedVirtualSwitch.SecurityPolicy()
    spec.defaultPortConfig.securityPolicy.forgedTransmits = vim.BoolPolicy(value=True)
    spec.defaultPortConfig.securityPolicy.allowPromiscuous = vim.BoolPolicy(value=True)
    spec.defaultPortConfig.securityPolicy.macChanges = vim.BoolPolicy(value=False)
    spec.defaultPortConfig.securityPolicy.inherited = False

    return spec
