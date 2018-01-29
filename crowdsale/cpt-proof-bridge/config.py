#! /usr/bin/env python2

import sys, os, json

config=json.load(open(os.path.join(os.path.dirname(sys.argv[0]), "cpt-proof-bridge.conf"), "rt"))
