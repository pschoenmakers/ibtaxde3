import csv
from decimal import Decimal
from datetime import date as Date


def export_groups_csv(groups, filepath):
    with open(filepath, "w") as fp:
        writer = csv.writer(fp, delimiter=";", quotechar='"')

        header_row = ["OPEN/CLOSE", "closed quantity", "transaction id", "date", "valuta", "buy/sell", "currency",
                      "exchange rate", "asset category", "symbol", "isin", "description", "quantity", "price",
                      "value", "tax", "fee", "value (EUR)", "tax (EUR)", "fee (EUR)", "profit (EUR)"]
        writer.writerow(header_row)
        writer.writerow([])

        for group in groups:
            o = group.opening_transaction
            c = group.closing_transaction

            profit = group.calc_profit()

            open_row = ["OPEN", "", o.transaction_id, o.date, o.settlement_date, o.category, o.currency,
                        o.exchange_rate, o.asset_category, o.symbol, o.isin, o.description, o.quantity, o.price,
                        o.value, o.tax, o.fee, o.value_eur, o.tax_eur, o.fee_eur, profit.open_profit]
            writer.writerow(format_row_ger(open_row))

            if c is None:
                writer.writerow([])
                continue

            close_row = ["CLOSE", group.quantity, c.transaction_id, c.date, c.settlement_date, c.category, c.currency,
                         c.exchange_rate, c.asset_category, c.symbol, c.isin, c.description, c.quantity, c.price,
                         c.value, c.tax, c.fee, c.value_eur, c.tax_eur, c.fee_eur, profit.close_profit]
            writer.writerow(format_row_ger(close_row))
            writer.writerow([])


def format_row_ger(row):
    row = [(lambda x: str(x.quantize(Decimal("0.000"))).replace(".", ",") if isinstance(x, Decimal) else x)(x)
           for x in row]
    row = [(lambda x: f"{x.day:02d}.{x.month:02d}.{x.year:04d}" if isinstance(x, Date) else x)(x) for x in row]
    return row


def export_groups_close_first_csv(grouping_result, filepath):
    with open(filepath, "w") as fp:
        writer = csv.writer(fp, delimiter=";", quotechar='"')

        header_row = ["OPEN/CLOSE", "closed quantity", "transaction id", "date", "valuta", "buy/sell", "currency",
                      "exchange rate", "asset category", "symbol", "isin", "description", "quantity", "price",
                      "value", "tax", "fee", "value (EUR)", "tax (EUR)", "fee (EUR)", "profit (EUR)"]
        writer.writerow(header_row)
        writer.writerow([])

        rows = []
        for groups in grouping_result.closing_groups:
            profit = sum(group.calc_profit().close_profit for group in groups)
            c = groups[0].closing_transaction

            close_row = ["CLOSE", "", c.transaction_id, c.date, c.settlement_date, c.category, c.currency,
                         c.exchange_rate, c.asset_category, c.symbol, c.isin, c.description, c.quantity, c.price,
                         c.value, c.tax, c.fee, c.value_eur, c.tax_eur, c.fee_eur, profit]
            writer.writerow(format_row_ger(close_row))

            for group in groups:
                o = group.opening_transaction
                open_row = ["OPEN", group.quantity, o.transaction_id, o.date, o.settlement_date, o.category, o.currency,
                            o.exchange_rate, o.asset_category, o.symbol, o.isin, o.description, o.quantity, o.price,
                            o.value, o.tax, o.fee, o.value_eur, o.tax_eur, o.fee_eur, group.calc_profit().open_profit]
                writer.writerow(format_row_ger(open_row))

            writer.writerow([])

        for group in grouping_result.open_short_groups:
            o = group.opening_transaction
            open_row = ["OPEN", group.quantity, o.transaction_id, o.date, o.settlement_date, o.category, o.currency,
                        o.exchange_rate, o.asset_category, o.symbol, o.isin, o.description, o.quantity, o.price,
                        o.value, o.tax, o.fee, o.value_eur, o.tax_eur, o.fee_eur, group.calc_profit().open_profit]
            writer.writerow(format_row_ger(open_row))
            writer.writerow([])
