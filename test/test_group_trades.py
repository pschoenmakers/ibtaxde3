import unittest

from ibtaxde3 import ibtaxde3
from ibtaxde3 import export_csv
from ibtaxde3 import export_xlsx

class TestGroupTrades(unittest.TestCase):
    def test_group_trades(self):
        temp = ibtaxde3.get_data(["resource/2018.xml", "resource/2019.xml", "resource/2020.xml"])
        trades = temp.trades

        groups = ibtaxde3.group_trades(trades)
        groups = [g for g in groups
                  if g.is_relevant_for_tax_year(2019)]
                  # and g.opening_transaction.asset_category == "stock"]
        # export.export_groups_csv(groups, "new_groups.csv")
        export_xlsx.export_groups(groups, "groups.xlsx")

        closing_groups = ibtaxde3.group_trades_close_first(groups)
        #export_csv.export_groups_close_first_csv(closing_groups, "new_groups2.csv")


if __name__ == '__main__':
    unittest.main()
