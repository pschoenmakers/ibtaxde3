import csv
from decimal import Decimal
from math import copysign
from datetime import date as Date

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
    logger.info("grouping trades")
    groups = []

    trades_by_symbol = dict()
    for trade in trades:
        if trade.symbol[-1].islower():  # ib added a lower case letter to some foreign securities' symbols
            symbol = trade.symbol[:-1]
            logger.warning(f"ignoring lower case suffix to symbol: {trade.symbol} -> {symbol}")
        else:
            symbol = trade.symbol

        trades_by_symbol[symbol] = trades_by_symbol.get(symbol, []) + [trade]

    for symbol in trades_by_symbol:
        logging.info(f"found {len(trades_by_symbol[symbol])} trades for symbol {symbol}")
        groups.extend(_group_trades_symbol(trades_by_symbol[symbol]))

    return groups


def _group_trades_symbol(trades):
    trades.sort(key=lambda t: t.timestamp)

    groups = []
    for trade in trades:
        if trade.asset_category == "cash":  # skip currency exchange
            continue

        if not groups:
            group = TransactionGroup(trade)
            groups.append(group)
            continue

        trade.open_quantity = abs(trade.quantity)
        for group in groups:
            result = group.try_close(trade)
            if result is None or result.closed_quantity == 0:
                continue

            if result.remaining_open_quantity > 0:
                new_group = TransactionGroup(group.opening_transaction, result.remaining_open_quantity)
                groups.append(new_group)

            if trade.open_quantity == 0:
                break

        else:
            new_group = TransactionGroup(trade, trade.open_quantity)
            groups.append(new_group)

    return groups


def group_trades_close_first(groups):
    open_short_groups = [g for g in groups
                         if g.closing_transaction is None
                         and g.opening_transaction.category == "sell"]

    for group in open_short_groups:
        groups.remove(group)

    closing_transaction_ids = set([g.closing_transaction.transaction_id for g in groups
                                   if g.closing_transaction is not None])

    closing_groups = []
    for cta_id in closing_transaction_ids:
        closing_group = [g for g in groups
                         if g.closing_transaction is not None
                         and g.closing_transaction.transaction_id == cta_id]

        closing_groups.append(closing_group)

    closing_groups.sort(key=lambda groups: (groups[0].closing_transaction.timestamp,
                                            groups[0].closing_transaction.symbol))

    GroupTradesCloseFirstResult = namedtuple("GroupTradesCloseFirstResult", "closing_groups open_short_groups")
    return GroupTradesCloseFirstResult(closing_groups, open_short_groups)
