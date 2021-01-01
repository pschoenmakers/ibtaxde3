import unittest

from ibtaxde3 import ibtaxde3


class TestGroupTrades(unittest.TestCase):
    def test_group_trades(self):
        temp = ibtaxde3.get_data(["resource/2018.xml", "resource/2019.xml", "resource/2020.xml"])
        trades = temp.trades

        result = ibtaxde3.group_trades(trades)
        for ta_group in result:
            print(f"[OPEN] {ta_group.opening_transaction}")
            for closing in ta_group.closing_transaction_items:
                print(f"[CLOSE, nominal={closing.closed_nominal}] closing_ta={closing.transaction}")

            print()

        ibtaxde3.export_groups("groups.csv", result)


if __name__ == '__main__':
    unittest.main()
