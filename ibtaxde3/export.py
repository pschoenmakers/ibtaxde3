import csv


def export_groups_csv(groups, filepath):
    with open(filepath, "w") as fp:
        writer = csv.writer(fp, delimiter=";", quotechar='"')

        header_row = ["OPEN/CLOSE", "closed quantity", "transaction id", "date", "valuta", "buy/sell", "currency",
                      "exchange rate", "asset category", "symbol", "isin", "description", "quantity", "price",
                      "value", "tax", "fee", "value (EUR)", "tax (EUR)", "fee (EUR)"]
        writer.writerow(header_row)
        writer.writerow([])

        for group in groups:
            o = group.opening_transaction
            c = group.closing_transaction

            open_row = ["OPEN", "", o.transaction_id, o.date, o.settlement_date, o.category, o.currency,
                        o.exchange_rate, o.asset_category, o.symbol, o.isin, o.description, o.quantity, o.price,
                        o.value, o.tax, o.fee, o.value_eur, o.tax_eur, o.fee_eur]
            writer.writerow(open_row)

            if c is None:
                writer.writerow([])
                continue

            close_row = ["CLOSE", group.quantity, c.transaction_id, c.date, c.settlement_date, c.category, c.currency,
                        c.exchange_rate, c.asset_category, c.symbol, c.isin, c.description, c.quantity, c.price,
                        c.value, c.tax, c.fee, c.value_eur, c.tax_eur, c.fee_eur]
            writer.writerow(close_row)
            writer.writerow([])