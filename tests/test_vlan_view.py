# -*- coding: UTF-8 -*-
"""
A suite of unit tests for the VlanView object
"""
import unittest
from unittest.mock import patch, MagicMock

import ujson
from flask import Flask
from vlab_api_common import flask_common
from vlab_api_common.http_auth import generate_v2_test_token


from vlab_vlan.lib.views import vlan


class TestVlanView(unittest.TestCase):
    """A set of test cases for the VlanView object"""
    @classmethod
    def setUpClass(cls):
        """Runs once for the whole test suite"""
        cls.token = generate_v2_test_token(username='bob')

    @classmethod
    def setUp(cls):
        """Runs before every test case"""
        app = Flask(__name__)
        vlan.VlanView.register(app)
        app.config['TESTING'] = True
        cls.app = app.test_client()
        # Mock Celery
        app.celery_app = MagicMock()
        cls.fake_task = MagicMock()
        cls.fake_task.id = 'asdf-asdf-asdf'
        app.celery_app.send_task.return_value = cls.fake_task

    @patch.object(flask_common, 'logger')
    def test_get_task_id(self, fake_logger):
        """VlanView - GET on /api/2/inf/vlan returns a task-id"""
        resp = self.app.get('/api/2/inf/vlan',
                            headers={'X-Auth': self.token})

        task_id = resp.json['content']['task-id']
        expected = 'asdf-asdf-asdf'

        self.assertEqual(task_id, expected)

    @patch.object(flask_common, 'logger')
    def test_get_status_coded(self, fake_logger):
        """VlanView - GET on /api/2/inf/vlan returns HTTP 202"""
        resp = self.app.get('/api/2/inf/vlan',
                            headers={'X-Auth': self.token})

        status = resp.status_code
        expected = 202

        self.assertEqual(status, expected)

    @patch.object(flask_common, 'logger')
    def test_get_link(self, fake_logger):
        """VlanView - GET on /api/2/inf/vlan sets the Link header"""
        resp = self.app.get('/api/2/inf/vlan',
                            headers={'X-Auth': self.token})

        link = resp.headers['Link']
        expected = '<https://localhost/api/2/inf/vlan/task/asdf-asdf-asdf>; rel=status'

        self.assertEqual(link, expected)

    @patch.object(flask_common, 'logger')
    def test_post_task_id(self, fake_logger):
        """VlanView - POST on /api/2/inf/vlan returns a task-id"""
        resp = self.app.post('/api/2/inf/vlan',
                             json={'switch-name': 'SomeSwitch', 'vlan-name': 'NewVLAN'},
                             headers={'X-Auth': self.token})

        task_id = resp.json['content']['task-id']
        expected = 'asdf-asdf-asdf'

        self.assertEqual(task_id, expected)

    @patch.object(flask_common, 'logger')
    def test_post_status_code(self, fake_logger):
        """VlanView - POST on /api/2/inf/vlan returns HTTP 202"""
        resp = self.app.post('/api/2/inf/vlan',
                             json={'switch-name': 'SomeSwitch', 'vlan-name': 'NewVLAN'},
                             headers={'X-Auth': self.token})

        status_code = resp.status_code
        expected = 202

        self.assertEqual(status_code, expected)

    @patch.object(flask_common, 'logger')
    def test_post_switch_name_required(self, fake_logger):
        """VlanView - POST on /api/2/inf/vlan returns HTTP 400 if switch-name not supplied"""
        resp = self.app.post('/api/2/inf/vlan',
                             json={'vlan-name': 'NewVLAN'},
                             headers={'X-Auth': self.token})

        status_code = resp.status_code
        expected = 400

        self.assertEqual(status_code, expected)

    @patch.object(flask_common, 'logger')
    def test_post_vlan_name_required(self, fake_logger):
        """VlanView - POST on /api/2/inf/vlan returns HTTP 400 if vlan-name not supplied"""
        resp = self.app.post('/api/2/inf/vlan',
                             json={'switch-name': 'SomeSwitch'},
                             headers={'X-Auth': self.token})

        status_code = resp.status_code
        expected = 400

        self.assertEqual(status_code, expected)

    @patch.object(flask_common, 'logger')
    def test_post_link(self, fake_logger):
        """VlanView - POST on /api/2/inf/vlan sets the Link header"""
        resp = self.app.post('/api/2/inf/vlan',
                             json={'switch-name': 'SomeSwitch', 'vlan-name': 'NewVLAN'},
                             headers={'X-Auth': self.token})

        status_code = resp.status_code
        link = resp.headers['Link']
        expected = '<https://localhost/api/2/inf/vlan/task/asdf-asdf-asdf>; rel=status'

        self.assertEqual(link, expected)

    @patch.object(flask_common, 'logger')
    def test_delete_task_id(self, fake_logger):
        """VlanView - DELETE on /api/2/inf/vlan returns a task-id"""
        resp = self.app.delete('/api/2/inf/vlan',
                             json={'vlan-name': 'NewVLAN'},
                             headers={'X-Auth': self.token})

        task_id = resp.json['content']['task-id']
        expected = 'asdf-asdf-asdf'

        self.assertEqual(task_id, expected)

    @patch.object(flask_common, 'logger')
    def test_delete_status_code(self, fake_logger):
        """VlanView - DELETE on /api/2/inf/vlan returns HTTP 202"""
        resp = self.app.delete('/api/2/inf/vlan',
                             json={'vlan-name': 'NewVLAN'},
                             headers={'X-Auth': self.token})

        status_code = resp.status_code
        expected = 202

        self.assertEqual(status_code, expected)

    @patch.object(flask_common, 'logger')
    def test_delete_vlan_name_required(self, fake_logger):
        """VlanView - DELETE on /api/2/inf/vlan returns HTTP 400 if vlan-name not supplied"""
        resp = self.app.delete('/api/2/inf/vlan',
                             json={},
                             headers={'X-Auth': self.token})

        status_code = resp.status_code
        expected = 400

        self.assertEqual(status_code, expected)

    @patch.object(flask_common, 'logger')
    def test_delete_link(self, fake_logger):
        """VlanView - DELETE on /api/2/inf/vlan sets the Link header"""
        resp = self.app.delete('/api/2/inf/vlan',
                             json={'vlan-name': 'NewVLAN'},
                             headers={'X-Auth': self.token})

        link = resp.headers['Link']
        expected = '<https://localhost/api/2/inf/vlan/task/asdf-asdf-asdf>; rel=status'

        self.assertEqual(link, expected)

    @patch.object(flask_common, 'logger')
    def test_v1_404(self, fake_logger):
        """VlanView - GET on /api/1/inf/vlan returns HTTP 404"""
        resp = self.app.get('/api/1/inf/vlan',
                            headers={'X-Auth': self.token})

        status = resp.status_code
        expected = 404

        self.assertEqual(status, expected)

if __name__ == '__main__':
    unittest.main()
