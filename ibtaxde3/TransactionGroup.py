from collections import namedtuple
from decimal import Decimal
from math import copysign


class TransactionGroup(object):
    def __init__(self, opening_transaction, quantity=None):
        assert quantity is None or quantity > 0

        self.opening_transaction = opening_transaction
        self.quantity = quantity or abs(opening_transaction.quantity)
        self.closing_transaction = None

    def __str__(self):
        return (f"TransactionGroup(opening={self.opening_transaction}, closing={self.closing_transaction}, "
                f"quantity={self.quantity})")

    def __repr__(self):
        return self.__str__()

    def try_close(self, transaction):
        """ try to close the opening transaction. Return None if it is not possible or the still open quantity else """

        def _same_sign(value1, value2):
            """ return True if both values have the same sign """
            return copysign(1, value1) == copysign(1, value2)

        if _same_sign(self.opening_transaction.quantity, transaction.quantity):
            return None

        quantity_to_close = min(self.quantity, abs(transaction.open_quantity))
        if quantity_to_close == 0:
            return None

        remaining_quantity = self.quantity - quantity_to_close
        self.quantity = quantity_to_close
        self.closing_transaction = transaction

        return remaining_quantity
