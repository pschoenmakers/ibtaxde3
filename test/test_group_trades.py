import unittest

from ibtaxde3 import ibtaxde3
from ibtaxde3 import export


class TestGroupTrades(unittest.TestCase):
    def test_group_trades(self):
        temp = ibtaxde3.get_data(["resource/2018.xml", "resource/2019.xml", "resource/2020.xml"])
        trades = temp.trades

        groups = ibtaxde3.group_trades(trades)
        export.export_groups_csv(groups, "new_groups.csv")


if __name__ == '__main__':
    unittest.main()
