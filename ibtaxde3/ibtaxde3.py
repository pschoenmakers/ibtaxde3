import csv
from decimal import Decimal
from math import copysign

from finparser.parsers.ibflex_xml import parse_file
from collections import namedtuple
import logging

from ibtaxde3.TransactionGroup import TransactionGroup

logger = logging.getLogger("finance.ibtaxde3")


def get_data(filepaths):
    logger.info(f"fetch data from: {filepaths}")
    header = None
    trades = []
    cash_transactions = []
    for filepath in filepaths:
        data = parse_file(filepath)
        if header is None:
            header = data.header
        else:
            assert header.account_id == data.header.account_id, (f"account_id missmatch: {header.account_id} != "
                                                                 f"{data.header.account_id}")

        logger.info(f"import {len(data.trades)} trades from '{filepath}'")
        trades.extend(data.trades)

        logger.info(f"import {len(data.cash_transactions)} cash transactions from '{filepath}'")
        cash_transactions.extend(data.cash_transactions)

    logger.info(f"imported {len(trades)} trades and {len(cash_transactions)} in total")

    ParsingResult = namedtuple("ParsingResult", "header trades cash_transactions")
    return ParsingResult(header, trades, cash_transactions)


def group_trades(trades):
    groups = []

    trades_by_symbol = dict()
    for trade in trades:
        trade.open_quantity = trade.quantity

        # ib added a lower case letter to some foreign securities' symbols
        symbol = trade.symbol if trade.symbol[-1].isupper() else trade.symbol[:-1]

        trades_by_symbol[symbol] = trades_by_symbol.get(symbol, []) + [trade]

    for symbol in trades_by_symbol:
        groups.extend(_group_trades_symbol(trades_by_symbol[symbol]))

    return groups


def _group_trades_symbol(trades):
    trades.sort(key=lambda t: t.date)

    groups = []
    for trade in trades:
        if trade.asset_category == "cash":  # skip currency exchange
            continue

        if not groups:
            group = TransactionGroup(trade)
            groups.append(group)
            continue

        for group in groups:
            group.try_close(trade)
            if trade.open_quantity == 0:  # try_close reduced open_nominal if position was fully or partially closed
                break
        else:  # the not closed nominal of the trade is treated as an opening trade -> new group
            group = TransactionGroup(trade)
            groups.append(group)

    return groups


def calc_profit(groups, tax_year=None):
    for group in groups:
        ota = group.opening_transaction
        if ota.category == "buy":
            ota.profit_eur = Decimal(0)
        else:
            assert ota.category == "sell"
            ota.profit_eur = ota.value_eur + ota.fee_eur

        for cti in group.closing_transaction_items:
            ta = cti.transaction

            if ta.category == "buy":
                cti.profit_eur = (cti.closed_quantity / abs(ta.quantity)) * (ta.value_eur + ta.fee_eur)
            else:
                assert ta.category == "sell"
                cti.profit_eur = (cti.closed_quantity * (ta.price_eur - ota.price_eur)
                                  + cti.closed_quantity / abs(ta.quantity) * ta.fee_eur
                                  + cti.closed_quantity / abs(ota.quantity) * ota.fee_eur)


def export_groups(filepath, groups):
    with open(filepath, "w") as f:
        writer = csv.writer(f, delimiter=";", quotechar='"')

        row = ["OPEN/CLOSE", "closed quantity", "id", "date", "valuta", "buy/sell", "currency", "exchange rate",
               "asset category", "symbol", "isin", "description", "quantity", "price", "value", "tax",
               "fee", "value (EUR)", "tax (EUR)", "fee (EUR)", "profit (EUR)"]
        writer.writerow(row)

        for group in groups:
            o = group.opening_transaction
            row = ["OPEN", "", o.transaction_id, o.date, o.settlement_date, o.category, o.currency, o.exchange_rate,
                   o.asset_category, o.symbol, o.isin, o.description, o.quantity, o.price, o.value, o.tax,
                   o.fee, o.value_eur, o.tax_eur, o.fee_eur, o.profit_eur]
            writer.writerow(row)
            for cti in group.closing_transaction_items:
                c = cti.transaction
                row = ["CLOSE", abs(cti.closed_quantity), c.transaction_id, c.date, c.settlement_date, c.category,
                       c.currency, c.exchange_rate, c.asset_category, c.symbol, c.isin, c.description,
                       c.quantity, c.price, c.value, c.tax, c.fee, c.value_eur, c.tax_eur, c.fee_eur, cti.profit_eur]
                writer.writerow(row)
            writer.writerow([])
