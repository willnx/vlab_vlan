# -*- coding: UTF-8 -*-
from flask import Flask
from celery import Celery

from vlab_vlan.lib import const
from vlab_vlan.lib.views import VlanView, HealthView

app = Flask(__name__)
app.celery_app = Celery('vlan', backend='rpc://', broker=const.VLAB_MESSAGE_BROKER)
app.celery_app.conf.broker_heartbeat = 0 #https://github.com/celery/celery/issues/4895

VlanView.register(app)
HealthView.register(app)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
