#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
vlan RESTful endpoints for vLab
"""
from setuptools import setup, find_packages


setup(name="vlab-vlan",
      author="Nicholas Willhite",
      author_email='willnx84@gmail.com',
      version='2018.11.28',
      packages=find_packages(),
      include_package_data=True,
      package_files={'vlab_switches' : ['app.ini']},
      description="A service for working with vLANs in vLab",
      long_description=open('README.rst').read(),
      install_requires=['flask', 'psycopg2', 'pyjwt', 'uwsgi', 'vlab-api-common',
                        'ujson', 'cryptography', 'celery', 'vlab-inf-common']
      )
