# -*- coding: UTF-8 -*-
from flask import Flask
from celery import Celery

from vlab_vlan.lib import const
from vlab_vlan.lib.views import VlanView

app = Flask(__name__)
app.celery_app = Celery('vlan', backend='rpc://', broker=const.VLAB_MESSAGE_BROKER)

VlanView.register(app)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
