import unittest

from ibtaxde3 import ibtaxde3


class TestGroupTrades(unittest.TestCase):
    def test_group_trades(self):
        temp = ibtaxde3.get_data(["resource/2018.xml", "resource/2019.xml", "resource/2020.xml"])
        trades = temp.trades

        groups = ibtaxde3.group_trades(trades)
        ibtaxde3.calc_profit(groups)
        # ibtaxde3.export_groups("groups.csv", result)

        inverted_groups = ibtaxde3._get_groups_close_first(groups)
        ibtaxde3.calc_profit(inverted_groups)
        ibtaxde3.export_groups_close_first("inverted_groups.csv", inverted_groups, groups)


if __name__ == '__main__':
    unittest.main()
