#! /usr/bin/env python2

import os, sys, json, getpass, csv

if len(sys.argv)<2:
    sys.exit("Usage: {0} file.csv".format(sys.argv[0]))

sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), "jsonrpclib"))
import jsonrpclib

cfgfile=sys.argv[0]
if cfgfile.endswith(".py"):
    cfgfile=cfgfile[:-3]
cfgfile+=".conf"

config=json.load(open(cfgfile, "rt"))

walletrpc=jsonrpclib.jsonrpc.Server("http://{0}:{1}".format(config["node"]["address"], config["node"]["port"]))

try:
    password=config["password"]
except:
    password=getpass.getpass()

walletrpc.personal_unlockAccount(config["caller"], password)

csvdialect=csv.register_dialect("my", delimiter=';', quotechar='"', lineterminator="\r\n")

reader=csv.reader(open(sys.argv[1], "rt"), dialect="my")
for line in reader:
    amount=int(float(line[0])*100000000)
    receiver=line[1].strip().lower()

    txobject={}
    txobject["from"]=config["caller"]
    txobject["to"]=config["contract"]
    txobject["value"]="0x0"
    txobject["gas"]="0x{0:x}".format(100000)
    txobject["gasPrice"]="0x{0:x}".format(int(walletrpc.eth_gasPrice(), 16)//config["gas-divisor"])
    txobject["data"]="0xa9059cbb"+12*"00"+receiver[2:]+"{0:x}".format(amount).rjust(64, '0')

    print walletrpc.eth_sendTransaction(txobject)
