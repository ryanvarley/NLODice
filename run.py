""" A simple dice betting game to check nlocoin transactions through rpc
"""
from config import *
from peewee import *
from bitcoinrpc.authproxy import AuthServiceProxy
import random
import os.path
from decimal import Decimal

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

            if txin_id == '668da09106277019cb33bbd54d9243543cf6d9d6ac62e0677893db29d053f6a4':
                continue  # skip the seed payment

            try:  # Check if transaction has been processed before
                DiceTransactions.select().where(DiceTransactions.txin_id == txin_id or DiceTransactions.txin_out == txin_id).get()  #  .get fetches 1 record
            except DoesNotExist:
                print 'new transaction {} NLO ID:{} - processing'.format(amount, txin_id)

                # check if within game limits
                upper_limit = 1000
                lower_limit = 5

                if amount <= lower_limit:  # Consider it a donation
                    db_transaction = DiceTransactions.create(from_address=from_address, txin_id=txin_id, txin_amount=amount,
                                                             win=False, txout_id='donation', txout_amount=0, account=account)
                    db_transaction.save()
                    print 'Below limit - skipping'
                    continue
                elif amount > upper_limit:  # Return minus lower limit fee to stop spamming
                    txout_amount = amount - lower_limit

                    txout_id = rpcaccess.sendfrom(account, from_address, txout_amount)  # , comment Won or lost

                    db_transaction = DiceTransactions.create(from_address=from_address, txin_id=txin_id, txin_amount=amount,
                                                             win=False, txout_id=txout_id, txout_amount=txout_amount,
                                                             account=account)
                    db_transaction.save()
                    print 'Above limit - returning minus fee {}'.format(txout_id)

                # Roll Dice
                rolled = dice.randint(1, 100)

                if rolled <= game.rollodds:
                    win = True
                    win_amount = amount * Decimal(game.pay_odds)
                else:
                    win = False
                    win_amount = Decimal('0.0001')  # TODO odds should be set in decimal in config

                print 'odds are {} - rolled {} - result {} - win {} ({} * {})'.format(game.rollodds, rolled, win, win_amount,
                amount, game.pay_odds)

                # Send transaction
                txout_id = rpcaccess.sendfrom(account, from_address, win_amount)  # , comment Won or lost
                print "sending win {}".format(txout_id)

                # Store transaction and game info to DB
                db_transaction = DiceTransactions.create(from_address=from_address, txin_id=txin_id, txin_amount=amount,
                                                         win=win, txout_id=txout_id, txout_amount=win_amount,
                                                         account=account)
                db_transaction.save()
            else:
                print 'transaction exists - continuing'
finally:
    db.close()