from collections import namedtuple
from decimal import Decimal
from math import copysign


class TransactionGroup(object):
    def __init__(self, opening_transaction):
        self.opening_transaction = opening_transaction
        self.closing_transaction_items = []

    def __str__(self):
        return f"TransactionGroup(opening={self.opening_transaction}, closing={self.closing_transaction_items})"

    def __repr__(self):
        return self.__str__()

    def try_close(self, transaction):
        def _same_sign(value1, value2):
            """ return True if both values have the same sign """
            return copysign(1, value1) == copysign(1, value2)

        def _reduce_abs(value, amount):
            """ reduce the absolute value by <amount> but keep <value>'s sign """
            assert amount >= 0
            return Decimal(copysign(abs(value) - amount, value))

        if _same_sign(self.opening_transaction.nominal, transaction.nominal):
            return None

        nominal_to_close_abs = min(abs(self.opening_transaction.open_nominal), abs(transaction.open_nominal))
        if nominal_to_close_abs == 0:
            return None

        self.opening_transaction.open_nominal = _reduce_abs(self.opening_transaction.open_nominal, nominal_to_close_abs)
        transaction.open_nominal = _reduce_abs(transaction.open_nominal, nominal_to_close_abs)

        ClosingTransactionItem = namedtuple("ClosingTransactionItem", "transaction closed_nominal")
        cti = ClosingTransactionItem(transaction, copysign(nominal_to_close_abs, transaction.nominal))
        self.closing_transaction_items.append(cti)

        return nominal_to_close_abs
