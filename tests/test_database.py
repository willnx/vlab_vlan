# -*- coding: UTF-8 -*-
"""
A suite of tests for the functions in database.py
"""
import unittest
from unittest.mock import patch, MagicMock

import psycopg2

from vlab_vlan.lib.worker import database


class FakeIntegrityError23505(psycopg2.IntegrityError):
    """pgcode is a read-only attribute on the normal IntegrityError object. Doing
    this wonky workaround enables unit testing of the ``register_vlan`` function.
    """
    pgcode = '23505'


class FakeIntegrityError23504(psycopg2.IntegrityError):
    """pgcode is a read-only attribute on the normal IntegrityError object. Doing
    this wonky workaround enables unit testing of the ``register_vlan`` function.
    """
    pgcode = '23504'


class TestDatabase(unittest.TestCase):
    """A set of test cases for ``database.py``"""
    @classmethod
    def setUp(cls):
        """Runs before every test case"""
        cls.patcher = patch('vlab_vlan.lib.worker.database.psycopg2.connect')
        cls.fake_psycopg2_connect = cls.patcher.start()
        cls.fake_cur = MagicMock()
        cls.fake_conn = MagicMock()
        cls.fake_conn.cursor.return_value = cls.fake_cur
        cls.fake_psycopg2_connect.return_value = cls.fake_conn

    @classmethod
    def tearDown(cls):
        """Runs after every test case"""
        cls.fake_psycopg2_connect.stop()

    def test_get_vlan_strip_name(self):
        """database - ``get_vlan`` strips the username off the vLAN name"""
        self.fake_cur.fetchall.return_value = [('alice_smith_vlanA', 100)]

        result = database.get_vlan(username='alice_smith')
        expected = {'vlanA': 100}

        self.assertEqual(result, expected)

    def test_get_db_connection(self):
        """database - ``get_db_connection`` returns the connection and cursor"""
        conn, cur = database.get_db_connection()

        self.assertTrue(self.fake_conn is conn)
        self.assertTrue(self.fake_cur is cur)

    def test_get_vlan(self):
        """database - ``get_vlan`` returns a dictionary"""
        self.fake_cur.fetchall.return_value = [('vlanA', 100), ('vlanB', 101)]

        result = database.get_vlan(username='alice')
        expected = {'vlanA': 100, 'vlanB': 101}

        self.assertEqual(result, expected)

    def test_get_vlan_closes(self):
        """database - ``get_vlan`` always closes the DB connection"""
        self.fake_cur.execute.side_effect = RuntimeError('testing')

        try:
            database.get_vlan(username='alice')
        except RuntimeError:
            pass

        self.assertTrue(self.fake_conn.close.called)

    def test_delete_vlan(self):
        """database - ``delete_vlan`` returns None when delete succeeds"""
        self.fake_cur.rowcount = 1
        result = database.delete_vlan(vlan_name='someVlan', username='bob')

        self.assertTrue(result is None)

    def test_delete_vlan_commit(self):
        """database - ``delete_vlan`` commits when something is deleted"""
        self.fake_cur.rowcount = 1
        database.delete_vlan(vlan_name='someVlan', username='bob')

        self.assertTrue(self.fake_conn.commit.called)

    def test_delete_vlan_valueerror(self):
        """database - ``delete_vlan`` raises ValueError when the vlan doesn't exists"""
        self.fake_cur.rowcount = 0

        with self.assertRaises(ValueError):
            database.delete_vlan(vlan_name='someVlan', username='bob')

    def test_delete_vlan_runtimeerror(self):
        """database - ``delete_vlan`` raises RuntimeError when mulitiple vLANs would be deleted"""
        self.fake_cur.rowcount = 24

        with self.assertRaises(RuntimeError):
            database.delete_vlan(vlan_name='someVlan', username='bob')

    def test_delete_vlan_closes(self):
        """database - ``delete_vlan`` always closes the DB connection"""
        self.fake_cur.execute.side_effect = RuntimeError('testing')

        try:
            database.delete_vlan(vlan_name='foo', username='alice')
        except RuntimeError:
            pass

        self.assertTrue(self.fake_conn.close.called)

    def test_register_vlan(self):
        """database - ``register_vlan`` returns the vlan tag id upon success"""
        self.fake_cur.fetchall.return_value = [(200,)]
        fake_logger = MagicMock()

        vlan_id = database.register_vlan(username='alice', vlan_name='wootVlan', logger=fake_logger)
        expected = 200

        self.assertEqual(vlan_id, expected)

    def test_register_vlan_runtime_error(self):
        """database - ``register_vlan`` raises RuntimeError if no vlan tags available"""
        self.fake_cur.fetchall.return_value = [(200,)]
        self.fake_cur.rowcount = 0
        self.fake_cur.execute.side_effect = [MagicMock(),
                                             FakeIntegrityError23505(),
                                             MagicMock(),
                                            ]
        fake_logger = MagicMock()
        with self.assertRaises(RuntimeError):
            database.register_vlan(username='bob', vlan_name='someVlan', logger=fake_logger)

    def test_register_vlan_dberror(self):
        """database - ``register_vlan`` raises any the IntegrityError if the pgcode is not 23505"""
        self.fake_cur.fetchall.return_value = [(200,)]
        self.fake_cur.rowcount = 0
        self.fake_cur.execute.side_effect = [MagicMock(),
                                             FakeIntegrityError23504(),
                                             MagicMock(),
                                            ]
        fake_logger = MagicMock()
        with self.assertRaises(psycopg2.DatabaseError):
            database.register_vlan(username='bob', vlan_name='someVlan', logger=fake_logger)

    def test_register_vlan_valueerror(self):
        """database - ``register_vlan`` raises ValueError if a vlan with the same name already exists"""
        self.fake_cur.fetchall.return_value = [(200,)]
        self.fake_cur.rowcount = 1
        self.fake_cur.execute.side_effect = [MagicMock(),
                                             FakeIntegrityError23505(),
                                             MagicMock(),
                                            ]
        fake_logger = MagicMock()
        with self.assertRaises(ValueError):
            database.register_vlan(username='bob', vlan_name='someVlan', logger=fake_logger)


if __name__ == '__main__':
    unittest.main()
