
class DiceGame(object):
    def __init__(self, nlocoind_account_name, pay_odds, house_edge, receive_address, upperlimit, lowerlimit):
        """ Sets up a new dice game
        :param nlocoind_account_name: receiving address for game in nlocoind
        :param payodds: odds to payout i.e 2:1 would be 2, 3:2 would be 1.5
        :param house_edge: % edge for house. This is subtracted from odds i.e 2% edge and 2:1 to win becomes 48% win chance
        """

        self.account = nlocoind_account_name
        self.pay_odds = float(pay_odds)
        self.house_edge = float(house_edge)

        self.rollodds = (100. / pay_odds) - house_edge
        self.receive_address = receive_address

        self.upperlimit = upperlimit
        self.lowerlimit = lowerlimit


def get_first_input(rpcaccess, txid):
    """ Turns a TXID into the first input address which is normally but not always controlled by the sender

    :param rpcaccess:
    :param txid:
    :return:
    """
    def raw(tx):
        return rpcaccess.decoderawtransaction(rpcaccess.getrawtransaction(tx))

    first_input = raw(txid)['vin'][0]

    return raw(first_input['txid'])['vout'][first_input['vout']]['scriptPubKey']['addresses'][0]