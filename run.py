""" A simple dice betting game to check nlocoin transactions through rpc
"""
from config import *
from peewee import *
from bitcoinrpc.authproxy import AuthServiceProxy

# Setup The Database and Establish Connection
db = SqliteDatabase(sqlite_location)

class DiceTransactions(Model):
    roll_id = PrimaryKeyField()
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
print rpcaccess.getinfo()  # test

    # TODO add if failed to connect statement


# Per address / odds
for game in dicegames:
    number_of_transactions = 20
    confirmations = 1
    print game.account, number_of_transactions, confirmations

    print rpcaccess.listreceivedbyaccount(0, True)
    transactions = rpcaccess.listreceivedbyaccount(game.account, number_of_transactions, confirmations)

    print transactions  # EODN this is failing with JSON error - need to get it to output then parse the JSON

# TODO check transactions (and that none are missed)

# TODO process unrolled transactions

    # TODO roll dice

    # TODO info to DB

    # TODO transaction