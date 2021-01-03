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

        if _same_sign(self.opening_transaction.quantity, transaction.quantity):
            return None

        quantity_to_close = min(abs(self.opening_transaction.open_quantity), abs(transaction.open_quantity))
        if quantity_to_close == 0:
            return None

        self.opening_transaction.open_quantity = _reduce_abs(self.opening_transaction.open_quantity, quantity_to_close)
        transaction.open_quantity = _reduce_abs(transaction.open_quantity, quantity_to_close)

        class _ClosingTransactionItem(object):
            def __init__(self, transaction, closed_quantity):
                self.transaction = transaction
                self.closed_quantity = closed_quantity
                self.profit_eur = None

        cti = _ClosingTransactionItem(transaction, quantity_to_close)
        self.closing_transaction_items.append(cti)

        return quantity_to_close
