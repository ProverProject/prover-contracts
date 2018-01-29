#! /usr/bin/env python2

import sys, os, json
import database
import config

sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), "jsonrpclib"))
import jsonrpclib

walletrpc=jsonrpclib.jsonrpc.Server("http://{0}:{1}".format(config.config["node"]["address"], config.config["node"]["port"]))


def getAllTransfersToProver(fromBlock, toBlock):
    filterOptions={}
    filterOptions["fromBlock"]="0x{0:x}".format(fromBlock) if fromBlock is not None else "earliest"
    filterOptions["toBlock"]="0x{0:x}".format(toBlock) if toBlock is not None else "latest"
    filterOptions["address"]=config.config["cryptaur"]["contract-address"]
    filterOptions["topics"]=[]
    # "Transfer"
    filterOptions["topics"].append("0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef")
    # Any sender
    filterOptions["topics"].append(None)
    # Prover contract as a receiver
    filterOptions["topics"].append("0x"+12*"00"+config.config["prover"]["contract-address"][2:])

    return walletrpc.eth_getLogs(filterOptions)

# TODO: uncomment and use it

#def getAllMintEvents(fromBlock, minter):
#    filterOptions={}
#    filterOptions["fromBlock"]="0x{0:x}".format(fromBlock) if fromBlock is not None else "earliest"
#    filterOptions["toBlock"]="latest"
#    filterOptions["address"]=config.config["prover"]["contract-address"]
#    filterOptions["topics"]=[]
#    # "Mint"
#    filterOptions["topics"].append("0x3dec94b8abc8f801eaade1616d3aadd3114b556a284267905e0a053b2df39892")
#    # Minter
#    if minter is None:
#        filterOptions["topics"].append(None)
#    else:
#        filterOptions["topics"].append("0x"+12*"00"+minter[2:])
#
#    return walletrpc.eth_getLogs(filterOptions)


scanFromBlock=database.getLastCheckedBlock()
if scanFromBlock is not None:
    scanFromBlock+=1

topBlock=int(walletrpc.eth_blockNumber(), 16)
scanToBlock=topBlock-10

print "Scanning block range {0}-{1}".format(scanFromBlock, scanToBlock)

for logEntry in getAllTransfersToProver(scanFromBlock, scanToBlock):
    blockNumber=int(logEntry["blockNumber"], 16)
    logIndex=int(logEntry["logIndex"], 16)
    txhash=logEntry["transactionHash"]
    minter="0x"+logEntry["topics"][1][-40:]
    amount=int(logEntry["data"], 16)

    database.addTransfer(blockNumber, logIndex, txhash, minter, amount)

accumulator={}
for (blockNumber, logIndex, txhash, minter, amount) in database.getPendingTransfers():
    accumulator.setdefault(minter, []).append((blockNumber, logIndex, txhash, amount))

    totalAccumulated=0
    for dummy,dummy,dummy,amount in accumulator[minter]:
        totalAccumulated+=amount

    if totalAccumulated>=config.config["depositCPT"]["minimum"]:
        selectedTransfers=[(blockNumber, logIndex) for (blockNumber, logIndex, txhash, amount) in accumulator[minter]]
        database.markTransfers(selectedTransfers, 1)

        txobject={}
        txobject["from"]=config.config["depositCPT"]["caller"]
        txobject["to"]=config.config["prover"]["contract-address"]
        txobject["gas"]="0x{0:x}".format(config.config["depositCPT"]["gas"])
        txobject["gasPrice"]=walletrpc.eth_gasPrice()
        txobject["data"]="0x3bc764f7"+12*"00"+minter[2:]+"{0:x}".format(totalAccumulated).rjust(64, '0')+accumulator[minter][-1][2][2:]

        txhash=None
        try:
            txhash=walletrpc.eth_sendTransaction(txobject)
        except jsonrpclib.ProtocolError as e:
            if e.message==(-32000, "authentication needed: password or unlock"):
                walletrpc.personal_unlockAccount(config.config["depositCPT"]["caller"], config.config["depositCPT"]["password"])
                txhash=walletrpc.eth_sendTransaction(txobject)
            else:
                raise

        print txhash

        database.markTransfers(selectedTransfers, 2)

        accumulator[minter]=[]
