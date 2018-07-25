# -*- coding: UTF-8 -*-
"""
Enables Health checks for the power API
"""
from time import time
import pkg_resources

import ujson
from flask_classy import FlaskView, Response
from vlab_inf_common.vmware import vCenter



class HealthView(FlaskView):
    """
    Simple end point to test if the service is alive
    """
    route_base = '/api/1/inf/vlan/healthcheck'
    trailing_slash = False

    def get(self):
        """End point for health checks"""
        resp = {}
        resp['version'] = pkg_resources.get_distribution('vlab-vlan').version
        response = Response(ujson.dumps(resp))
        response.status_code = 200
        response.headers['Content-Type'] = 'application/json'
        return response
