""" A simple dice betting game to check nlocoin transactions through rpc
"""
from config import *
from peewee import *

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

# TODO setup RPC

# Per address / odds

# TODO check transactions (and that none are missed)

# TODO process unrolled transactions

    # TODO roll dice

    # TODO info to DB

    # TODO transaction