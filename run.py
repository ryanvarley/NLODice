""" A simple dice betting game to check nlocoin transactions through rpc
"""
from config import *
from peewee import *
from bitcoinrpc.authproxy import AuthServiceProxy
import random
import os.path
from decimal import Decimal
from dice_classes import get_first_input
import logging

logger = logging.getLogger('nlodice')
hdlr = logging.FileHandler(logfile_location)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

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


class MetaOptions(Model):
    meta_id = PrimaryKeyField()
    option = CharField(20)
    value = CharField(150)

    class Meta:
        database = db  # This model uses the "people.db" database.

try:
    if not os.path.exists(sqlite_location):  # on first run create the tables
        db.create_tables([DiceTransactions, MetaOptions])
        lasttnum = MetaOptions(option='lasttnum', value='0')
        lasttnum.save()
    else:
        lasttnum = MetaOptions.select().where(MetaOptions.option == 'lasttnum').get()

        # TODO add if failed to connect statement

    # Use RPC to Connect to nlocoind
    rpcaccess = AuthServiceProxy("http://{}:{}@{}:{}".format(rpcuser, rpcpass, rpcip, rpcport))
    # print rpcaccess.getinfo()  # test

        # TODO add if failed to connect statement

    dice = random.SystemRandom()

    # Per address / odds
    game = dicegames[0]  # needs to be replaced by changing game per transaction
    startfrom = int(lasttnum.value)
    transactions = rpcaccess.listtransactions(game.account, number_of_transactions, startfrom)

    for transaction in transactions:
        amount = transaction['amount']
        txin_id = transaction['txid']
        from_address = get_first_input(rpcaccess, txin_id)
        account = transaction['account']  # TODO seperate by account (maybe function called to process transaction?

        if txin_id == seed_txid:
            lasttnum.value = int(lasttnum.value) + 1
            lasttnum.save()
            logger.info('skipping seed payment')
            continue  # skip the seed payment

        if transaction['category'] == 'send':
            logger.info(transaction['category'], txin_id)
            logger.info('skipping sent payment')
            lasttnum.value = int(lasttnum.value) + 1
            lasttnum.save()
            continue  # skip sent payments

        try:  # Check if transaction has been processed before
            DiceTransactions.select().where(DiceTransactions.txin_id == txin_id or DiceTransactions.txin_out == txin_id).get()  #  .get fetches 1 record
        except DoesNotExist as e:
            print e
            logger.info('new transaction {} NLO ID:{} - processing'.format(amount, txin_id))

            # check if within game limits
            upper_limit = game.upperlimit
            lower_limit = game.lowerlimit

            if amount < lower_limit:  # Consider it a donation
                db_transaction = DiceTransactions.create(from_address=from_address, txin_id=txin_id, txin_amount=amount,
                                                         win=False, txout_id='donation', txout_amount=0, account=account)
                db_transaction.save()
                logger.info('Below limit - skipping')
                continue
            elif amount > upper_limit:  # Return minus lower limit fee to stop spamming
                txout_amount = amount - lower_limit

                txout_id = rpcaccess.sendfrom(account, from_address, txout_amount)  # , comment Won or lost

                db_transaction = DiceTransactions.create(from_address=from_address, txin_id=txin_id, txin_amount=amount,
                                                         win=False, txout_id=txout_id, txout_amount=txout_amount,
                                                         account=account)
                db_transaction.save()
                logger.info('Above limit - returning minus fee {}'.format(txout_id))

            # Roll Dice
            rolled = dice.randint(1, 100)

            if rolled <= game.rollodds:
                win = True
                win_amount = amount * Decimal(game.pay_odds)
            else:
                win = False
                win_amount = Decimal('0.0001')  # TODO odds should be set in decimal in config

            logger.info('odds are {} - rolled {} - result {} - win {} ({} * {})'.format(game.rollodds, rolled, win, win_amount,
            amount, game.pay_odds))

            # Send transaction
            txout_id = rpcaccess.sendfrom(account, from_address, win_amount)  # , comment Won or lost
            logger.info("sending win {}".format(txout_id))

            # Store transaction and game info to DB
            db_transaction = DiceTransactions.create(from_address=from_address, txin_id=txin_id, txin_amount=amount,
                                                     win=win, txout_id=txout_id, txout_amount=win_amount,
                                                     account=account)
            db_transaction.save()
        else:
            logger.info('transaction exists - continuing')
        finally:
            lasttnum.value = int(lasttnum.value) + 1
finally:
    db.close()
    logger.info('finished')