# -*- coding: UTF-8 -*-
"""
A suite of tests for the functions in tasks.py
"""
import unittest
from unittest.mock import patch, MagicMock

from vlab_vlan.lib.worker import tasks


class TestTasks(unittest.TestCase):
    """A set of test cases for ``tasks.py``"""
    @patch.object(tasks, 'database')
    def test_list(self, fake_database):
        """tasks - ``list`` returns a dictionary mapping vlan names to vlan tag ids"""
        fake_database.get_vlan.return_value = {'myVlan' : 1234}
        result = tasks.list(username='bob')
        expected =  {'content': {'myVlan': 1234}, 'params': {}, 'error': None}

        self.assertEqual(result, expected)

    @patch.object(tasks, 'database')
    @patch.object(tasks, 'delete_network')
    def test_delete(self, fake_delete_network, fake_database):
        """tasks - ``delete`` destroys the defined vLAN returns a dictionary"""
        fake_database.get_vlan.return_value = {'someVlan' : 1234}

        result = tasks.delete(username='alice', vlan_name='someVlan')
        expected = {'content': {}, 'error': None, 'params': {'vlan_name': 'someVlan'}}

        self.assertEqual(result, expected)

    @patch.object(tasks, 'database')
    @patch.object(tasks, 'delete_network')
    def test_delete_not_owned(self, fake_delete_network, fake_database):
        """tasks - ``delete`` returns an error message when the user does not own the vLAN"""
        fake_database.get_vlan.return_value = {'someVlan' : 1234}

        result = tasks.delete(username='alice', vlan_name='derpVlan')['error']
        expected = 'Unable to delete vLAN you do not own'

        self.assertEqual(result, expected)

    @patch.object(tasks, 'database')
    @patch.object(tasks, 'delete_network')
    def test_delete_vmware_fail(self, fake_delete_network, fake_database):
        """tasks - ``delete`` returns an error message if unable to delete the vLAN network"""
        fake_database.get_vlan.return_value = {'someVlan' : 1234}
        fake_delete_network.side_effect = [ValueError("some error message")]

        result = tasks.delete(username='alice', vlan_name='someVlan')['error']
        expected = 'some error message'

        self.assertEqual(result, expected)

    @patch.object(tasks, 'database')
    @patch.object(tasks, 'delete_network')
    def test_delete_db_issue(self, fake_delete_network, fake_database):
        """tasks - ``delete`` returns an error when unable to remove DB ref to vLAN"""
        fake_database.get_vlan.return_value = {'someVlan' : 1234}
        fake_database.delete_vlan.side_effect = ValueError('some error')

        result = tasks.delete(username='alice', vlan_name='someVlan')['error']
        expected = 'some error'

        self.assertEqual(result, expected)

    @patch.object(tasks, 'database')
    @patch.object(tasks, 'create_network')
    def test_create(self, fake_create_network, fake_database):
        """tasks - ``create`` returns empty content in dictionary upon success"""
        fake_database.register_vlan.return_value = 1234
        fake_create_network.return_value = None

        result = tasks.create(username='alice', vlan_name='someVlan', switch_name='someSwitch')
        expected = {'error' : None, 'content': {},
                    'params': {'vlan_name': 'someVlan', 'switch_name': 'someSwitch'}}

        self.assertEqual(result, expected)

    @patch.object(tasks, 'database')
    @patch.object(tasks, 'create_network')
    def test_create_register_failure(self, fake_create_network, fake_database):
        """tasks - ``create`` returns an error message if the vlan registration fails"""
        fake_database.register_vlan.side_effect = [ValueError('testing error msg')]
        fake_create_network.return_value = None

        result = tasks.create(username='alice', vlan_name='someVlan', switch_name='someSwitch')['error']
        expected = 'testing error msg'

        self.assertEqual(result, expected)

    @patch.object(tasks, 'database')
    @patch.object(tasks, 'create_network')
    def test_create_error(self, fake_create_network, fake_database):
        """tasks - ``create`` returns an error message if the network creation fails"""
        fake_database.register_vlan.return_value = 1234
        fake_create_network.side_effect = [ValueError("Some Error")]

        result = tasks.create(username='alice', vlan_name='someVlan', switch_name='someSwitch')['error']
        expected = 'Some Error'

        self.assertEqual(result, expected)

    @patch.object(tasks, 'logger')
    @patch.object(tasks, 'database')
    @patch.object(tasks, 'create_network')
    def test_create_rollback_fail(self, fake_create_network, fake_database, fake_logger):
        """tasks - ``create`` logs the traceback if unable to delete the ref after creating the network"""
        fake_database.register_vlan.return_value = 1234
        fake_database.delete_vlan.side_effect = [Exception('some unexpected failure')]
        fake_create_network.side_effect = [ValueError("Some Error")]

        result = tasks.create(username='alice', vlan_name='someVlan', switch_name='someSwitch')['error']
        expected = 'Some Error'

        self.assertTrue(fake_logger.traceback.called)


if __name__ == '__main__':
    unittest.main()
