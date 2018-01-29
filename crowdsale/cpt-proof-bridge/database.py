#! /usr/bin/env python2

import os, pymysql, sys, config, traceback, time


dbconfig=config.config["database"]
db=pymysql.connect(host=dbconfig["host"], user=dbconfig["user"], passwd=dbconfig["password"], db=dbconfig["dbname"])

db.cursor().execute("SET sql_notes = 0;")
db.cursor().execute("""CREATE TABLE IF NOT EXISTS transferEvents
(
  blockNumber BIGINT UNSIGNED NOT NULL,
  logIndex INT UNSIGNED NOT NULL,
  txhash VARCHAR(100) NOT NULL,
  minter VARCHAR(50) NOT NULL,
  amount BIGINT UNSIGNED NOT NULL,
  status TINYINT(1) NOT NULL,
  PRIMARY KEY(blockNumber, logIndex)
);
""")
db.cursor().execute("SET sql_notes = 1;")
db.commit()

def getLastCheckedBlock():
    cur=db.cursor()
    n=cur.execute("SELECT MAX(blockNumber) FROM transferEvents;")
    if n==0:
        return None
    else:
        return cur.fetchone()[0]

def addTransfer(blockNumber, logIndex, txhash, minter, amount):
    db.cursor().execute("INSERT INTO transferEvents VALUES (%s, %s, %s, %s, %s, 0);", (blockNumber, logIndex, txhash, minter, amount))
    db.commit()

def getPendingTransfers():
    cur=db.cursor()
    cur.execute("SELECT blockNumber, logIndex, txhash, minter, amount FROM transferEvents WHERE status=0;")
    return cur.fetchall()

def markTransfers(transfers, status):
    cur=db.cursor()
    for (blockNumber, logIndex) in transfers:
        cur.execute("UPDATE transferEvents SET status=%s WHERE blockNumber=%s AND logIndex=%s;", (status, blockNumber, logIndex))
    db.commit()
