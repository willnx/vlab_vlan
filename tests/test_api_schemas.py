# -*- coding: UTF-8 -*-
"""
A suite of tests for the HTTP API schemas
"""
import unittest

from jsonschema import Draft4Validator
from vlab_vlan.lib.views import vlan


class TestVlanViewSchema(unittest.TestCase):
    """A set of test cases for the schemas in /api/1/inf/vlan end points"""

    def test_post_schema(self):
        """The schema defined for POST on /api/1/inf/vlan is valid"""
        try:
            Draft4Validator.check_schema(vlan.VlanView.POST_SCHEMA)
            schema_valid = True
        except RuntimeError:
            schema_valid = False

        self.assertTrue(schema_valid)

    def test_delete_schema(self):
        """The schema defined for DELETE on /api/1/inf/vlan is valid"""
        try:
            Draft4Validator.check_schema(vlan.VlanView.DELETE_SCHEMA)
            schema_valid = True
        except RuntimeError:
            schema_valid = False

        self.assertTrue(schema_valid)

    def test_token_schema(self):
        """The schema defined for DELETE on /api/1/inf/vlan/token is valid"""
        try:
            Draft4Validator.check_schema(vlan.VlanView.TASK_ARGS)
            schema_valid = True
        except RuntimeError:
            schema_valid = False

        self.assertTrue(schema_valid)


if __name__ == '__main__':
    unittest.main()
