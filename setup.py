#!/usr/bin/env python

from distutils.core import setup

setup(name='ytanalysiskit',
      version='0.1',
      description='Youtube Analysis Kit',
      author='Roland Askew',
      author_email='rolandjamesaskew37@gmail.com',
      url='https://www.python.org/sigs/distutils-sig/',
      packages=['networkx','matplotlib','google-api-python-client','numpy','scipy'],
      scripts=['scripts/yt_script.py']
     )