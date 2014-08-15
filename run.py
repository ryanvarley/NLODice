""" A simple dice betting game to check nlocoin transactions through rpc
"""
from config import *
from peewee import *
from bitcoinrpc.authproxy import AuthServiceProxy
import random
import os.path

# Setup The Database and Establish Connection
db = SqliteDatabase(sqlite_location)

class DiceTransactions(Model):
    roll_id = PrimaryKeyField()
    account = CharField(12)  # the dice game account
    from_address = CharField(34)
    txin_id = CharField(64)
    txin_amount = DecimalField()
    win = BooleanField()
    txout_id = CharField(64)
    txout_amount = DecimalField()

    class Meta:
        database = db  # This model uses the "people.db" database.

try:
    if not os.path.exists(sqlite_location):  # on first run create the tables
        db.create_tables([DiceTransactions])

        # TODO add if failed to connect statement

    # Use RPC to Connect to nlocoind
    rpcaccess = AuthServiceProxy("http://{}:{}@{}:{}".format(rpcuser, rpcpass, rpcip, rpcport))
    # print rpcaccess.getinfo()  # test

        # TODO add if failed to connect statement


    dice = random.SystemRandom()

    # Per address / odds
    for game in dicegames:
        startfrom = 0  # TODO need a way of only getting unprocessed transactions perhaps keeping a start from counter
        # and processing x per minute
        number_of_tranasactions = 20

        transactions = rpcaccess.listtransactions(game.account, 20, 0)

        for transaction in transactions:
            amount = transaction['amount']
            from_address = transaction['address']
            txin_id = transaction['txid']
            account = transaction['account']  # TODO seperate by account (maybe function called to process transaction?

            try:  # Check if transaction has been processed before
                DiceTransactions.select().where(DiceTransactions.txin_id == txin_id).get()  #  .get fetches 1 record
            except DoesNotExist:
                print 'new transaction {} - processing'.format(txin_id)

                # TODO roll dice
                rolled = dice.randint(1, 100)
                if rolled <= game.rollodds:
                    win = True
                else:
                    win = False

                print 'odds are {} - rolled {} - result {}'.format(game.rollodds, rolled, win)

                # TODO info to DB

                # TODO transaction

                txout_id = '189d86539b552541b1550d5ed4bec85cba066e34caf7e930b4cda3081bd04c42'
                txout_amount = 0.0001

                db_transaction = DiceTransactions.create(from_address=from_address, txin_id=txin_id, txin_amount=amount,
                                                         win=win, txout_id=txout_id, txout_amount=txout_amount,
                                                         account=account)
                db_transaction.save()
            else:
                print 'transaction exists - continuing'
finally:
    db.close()