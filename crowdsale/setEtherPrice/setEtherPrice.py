#! /usr/bin/env python2

import os, sys, json, getpass

if len(sys.argv)<2:
    sys.exit("Usage: {0} PRICE".format(sys.argv[0]))

sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), "jsonrpclib"))
import jsonrpclib

cfgfile=sys.argv[0]
if cfgfile.endswith(".py"):
    cfgfile=cfgfile[:-3]
cfgfile+=".conf"

config=json.load(open(cfgfile, "rt"))

walletrpc=jsonrpclib.jsonrpc.Server("http://{0}:{1}".format(config["node"]["address"], config["node"]["port"]))

txobject={}
txobject["from"]=config["caller"]
txobject["to"]=config["contract"]
txobject["value"]="0x0"
txobject["gas"]="0x{0:x}".format(100000)
txobject["gasPrice"]="0x{0:x}".format(int(walletrpc.eth_gasPrice(), 16)//config["gas-divisor"])
txobject["data"]="0x27187991"+"{0:x}".format(int(sys.argv[1])).rjust(64, '0')

print txobject

password=getpass.getpass()
walletrpc.personal_unlockAccount(config["caller"], password)

print walletrpc.eth_sendTransaction(txobject)
