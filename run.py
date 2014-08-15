""" A simple dice betting game to check nlocoin transactions through rpc
"""
from config import *
from peewee import *
from bitcoinrpc.authproxy import AuthServiceProxy

# Setup The Database and Establish Connection
db = SqliteDatabase(sqlite_location)

try:
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

    if 0:  # on first run create the tables
        db.create_tables([DiceTransactions])

        # TODO add if failed to connect statement

    # Use RPC to Connect to nlocoind
    rpcaccess = AuthServiceProxy("http://{}:{}@{}:{}".format(rpcuser, rpcpass, rpcip, rpcport))
    # print rpcaccess.getinfo()  # test

        # TODO add if failed to connect statement

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
            account = transaction['account']

            # TODO check already rolled
            try:
                DiceTransactions.select().where(DiceTransactions.txin_id == txin_id).get()  #  .get fetches 1 record
            except DoesNotExist:
                print 'new transaction {} - processing'.format(txin_id)
                # TODO roll dice

                # TODO info to DB

                # TODO transaction

                win = False
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