from collections import namedtuple

import xlsxwriter


def export_groups(groups, filepath):
    workbook = xlsxwriter.Workbook(filepath)
    _export_all_transactions_sheet(workbook, groups)
    _export_transactions_by_category_sheet(workbook, groups, "stock", "Stock Transactions")
    _export_transactions_by_category_sheet(workbook, groups, "bond", "Bond Transactions")
    workbook.close()


def _export_all_transactions_sheet(workbook, groups):
    worksheet = workbook.add_worksheet("All Transactions")
    fmt = _format(workbook, worksheet)

    column_names = ["OPEN/CLOSE", "closed quantity", "transaction id", "date", "valuta", "buy/sell", "currency",
                    "exchange rate", "asset category", "symbol", "isin", "description", "quantity", "price",
                    "value", "tax", "fee", "value (EUR)", "tax (EUR)", "fee (EUR)", "profit (EUR)"]

    for i, col_name in enumerate(column_names):
        worksheet.write(0, i, col_name, fmt.bold)

    row = 1
    for group in groups:
        o = group.opening_transaction
        c = group.closing_transaction

        profit = group.calc_profit()

        row_content = ["OPEN", "", o.transaction_id, o.date, o.settlement_date, o.category, o.currency,
                       o.exchange_rate, o.asset_category, o.symbol, o.isin, o.description, o.quantity, o.price,
                       o.value, o.tax, o.fee, o.value_eur, o.tax_eur, o.fee_eur, profit.open_profit]
        for i, value in enumerate(row_content):
            if i > 16:
                worksheet.write(row, i, value, fmt.euro)
            elif i in [1, 7, 12, 13, 14, 15, 16]:
                worksheet.write(row, i, value, fmt.number)
            elif i in [3, 4]:
                worksheet.write(row, i, value, fmt.date)
            else:
                worksheet.write(row, i, value)

        row += 1

        if c is None:
            row += 1
        else:
            row_content = ["CLOSE", group.quantity, c.transaction_id, c.date, c.settlement_date, c.category, c.currency,
                           c.exchange_rate, c.asset_category, c.symbol, c.isin, c.description, c.quantity, c.price,
                           c.value, c.tax, c.fee, c.value_eur, c.tax_eur, c.fee_eur, profit.close_profit]
            for i, value in enumerate(row_content):
                if i > 16:
                    worksheet.write(row, i, value, fmt.euro)
                elif i in [1, 7, 12, 13, 14, 15, 16]:
                    worksheet.write(row, i, value, fmt.number)
                elif i in [3, 4]:
                    worksheet.write(row, i, value, fmt.date)
                else:
                    worksheet.write(row, i, value)
            row += 1
        row += 1


def _format(workbook, worksheet):
    worksheet.set_column("A:A", 6)
    worksheet.set_column("C:C", 1)
    worksheet.set_column("D:D", 10)
    worksheet.set_column("E:E", 1)
    worksheet.set_column("F:G", 5)
    worksheet.set_column("K:K", 14)
    worksheet.set_column("L:L", 25)
    worksheet.set_column("O:O", 10)
    worksheet.set_column("R:R", 10)
    worksheet.set_column("U:U", 10)

    bold = workbook.add_format({"bold": True})
    euro = workbook.add_format({"num_format": "###,0.00€;[RED]-###,0.00€"})
    number = workbook.add_format({"num_format": "###,0.000;[RED]-###,0.000"})
    short_number = workbook.add_format({"num_format": "###,0.00;[RED]-###,0.00"})
    date = workbook.add_format({"num_format": "dd.mm.yyyy"})

    Format = namedtuple("Format", "bold euro number short_number date")
    return Format(bold, euro, number, short_number, date)


def _export_transactions_by_category_sheet(workbook, groups, category, sheet_name=None):
    worksheet = workbook.add_worksheet(sheet_name or f"{category} transactions")
    fmt = _format(workbook, worksheet)

    column_names = ["OPEN/CLOSE", "closed quantity", "transaction id", "date", "valuta", "buy/sell", "currency",
                    "exchange rate", "asset category", "symbol", "isin", "description", "quantity", "price",
                    "value", "tax", "fee", "value (EUR)", "tax (EUR)", "fee (EUR)", "profit (EUR)"]

    for i, col_name in enumerate(column_names):
        worksheet.write(0, i, col_name, fmt.bold)

    groups = [grp for grp in groups if grp.opening_transaction.asset_category == category]
    row = 1
    for group in groups:
        o = group.opening_transaction
        c = group.closing_transaction

        assert o.asset_category == "stock"
        assert not c or c.asset_category == "stock"

        profit = group.calc_profit()

        row_content = ["OPEN", "", o.transaction_id, o.date, o.settlement_date, o.category, o.currency,
                       o.exchange_rate, o.asset_category, o.symbol, o.isin, o.description, o.quantity, o.price,
                       o.value, o.tax, o.fee, o.value_eur, o.tax_eur, o.fee_eur, profit.open_profit]
        for i, value in enumerate(row_content):
            if i > 16:
                worksheet.write(row, i, value, fmt.euro)
            elif i in [1, 7, 12, 13, 14, 15, 16]:
                worksheet.write(row, i, value, fmt.number)
            elif i in [3, 4]:
                worksheet.write(row, i, value, fmt.date)
            else:
                worksheet.write(row, i, value)

        row += 1

        if c is None:
            row += 1
        else:
            row_content = ["CLOSE", group.quantity, c.transaction_id, c.date, c.settlement_date, c.category, c.currency,
                           c.exchange_rate, c.asset_category, c.symbol, c.isin, c.description, c.quantity, c.price,
                           c.value, c.tax, c.fee, c.value_eur, c.tax_eur, c.fee_eur, profit.close_profit]
            for i, value in enumerate(row_content):
                if i > 16:
                    worksheet.write(row, i, value, fmt.euro)
                elif i in [1, 7, 12, 13, 14, 15, 16]:
                    worksheet.write(row, i, value, fmt.number)
                elif i in [3, 4]:
                    worksheet.write(row, i, value, fmt.date)
                else:
                    worksheet.write(row, i, value)
            row += 1
        row += 1

