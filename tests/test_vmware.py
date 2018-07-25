# -*- coding: UTF-8 -*-
"""
A suite of tests for the functions in vmware.py
"""
import unittest
from unittest.mock import patch, MagicMock

from vlab_vlan.lib.worker import vmware


class TestVMware(unittest.TestCase):
    """A set of test cases for ``vmware.py``"""
    def test_spec(self):
        """vmware - ``get_dv_portgroup_spec`` returns vim.dvs.DistributedVirtualPortgroup.ConfigSpec"""
        spec = vmware.get_dv_portgroup_spec(name='myVlan', vlan_id=1234)

        self.assertTrue(isinstance(spec, vmware.vim.dvs.DistributedVirtualPortgroup.ConfigSpec))

    def test_spec_name(self):
        """vmware - ``get_dv_portgroup_spec`` sets the vlan name correctly"""
        spec = vmware.get_dv_portgroup_spec(name='myVlan', vlan_id=1234)

        expected = 'myVlan'
        self.assertEqual(spec.name, expected)

    def test_spec_id(self):
        """vmware - ``get_dv_portgroup_spec`` sets the vlan tag id correctly"""
        spec = vmware.get_dv_portgroup_spec(name='myVlan', vlan_id=1234)

        expected = 1234
        self.assertEqual(spec.defaultPortConfig.vlan.vlanId, expected)

    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_delete_network(self, fake_vCenter, fake_consume_task):
        """vmware - ``delete_network`` returns None upon success"""
        result = vmware.delete_network(name='someNetwork')
        expected = None

        self.assertEqual(result, expected)

    @patch.object(vmware, 'vCenter')
    def test_delete_network_not_exists(self, fake_vCenter):
        """vmware - ``delete_network`` raises ValueError if the vLAN network does not exist"""
        fake_network = MagicMock()
        fake_vCenter.return_value.__enter__.return_value.networks = {'someNetwork': fake_network}

        with self.assertRaises(ValueError):
            vmware.delete_network(name='DerpNetwork')

    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_delete_network_in_use(self, fake_vCenter, fake_consume_task):
        """vmware - ``delete_network`` raises ValueError if the vLAN is still being used by VMs"""
        fake_consume_task.side_effect = [vmware.vim.fault.ResourceInUse()]

        with self.assertRaises(ValueError):
            vmware.delete_network(name='someNetwork')

    @patch.object(vmware, 'vCenter')
    @patch.object(vmware, 'sleep')
    def test_create_network(self, fake_sleep, fake_vCenter):
        """vmware - ``create_network`` returns an empty string when successful"""
        fake_task = MagicMock()
        fake_task.info.error = None
        fake_switch = MagicMock()
        fake_switch.AddDVPortgroup_Task.return_value = fake_task
        fake_vCenter.return_value.__enter__.return_value.dv_switches = {'someSwitch': fake_switch}

        result = vmware.create_network(name='myVlan', vlan_id=1234, switch_name='someSwitch')
        expected = ''

        self.assertEqual(result, expected)

    @patch.object(vmware, 'vCenter')
    @patch.object(vmware, 'sleep')
    def test_create_network_valueerror(self, fake_sleep, fake_vCenter):
        """vmware - ``create_network`` raises ValueError if the switch does not exist"""
        fake_task = MagicMock()
        fake_task.info.error.msg = None
        fake_switch = MagicMock()
        fake_switch.AddDVPortgroup_Task.return_value = fake_task
        fake_vCenter.return_value.__enter__.return_value.dv_switches = {'otherSwitch': fake_switch}

        with self.assertRaises(ValueError):
            vmware.create_network(name='myVlan', vlan_id=1234, switch_name='someSwitch')

    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    @patch.object(vmware, 'sleep')
    def test_create_network_error(self, fake_sleep, fake_vCenter, fake_consume_task):
        """vmware - ``create_network`` returns the error message upon failure"""
        fake_consume_task.side_effect = [RuntimeError('Some handy error message')]

        result = vmware.create_network(name='myVlan', vlan_id=1234, switch_name='someSwitch')
        expected = 'Some handy error message'

        self.assertEqual(result, expected)



if __name__ == '__main__':
    unittest.main()
