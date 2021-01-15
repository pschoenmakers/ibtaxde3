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

        if self.closing_transaction is not None:
            return None

        if _same_sign(self.opening_transaction.quantity, transaction.quantity):
            return None

        quantity_to_close = min(self.quantity, abs(transaction.open_quantity))
        if quantity_to_close == 0:
            return None

        remaining_quantity = self.quantity - quantity_to_close
        self.quantity = quantity_to_close
        self.closing_transaction = transaction
        transaction.open_quantity -= quantity_to_close

        TryCloseResult = namedtuple("TryCloseResult", "closed_quantity remaining_open_quantity")
        return TryCloseResult(quantity_to_close, remaining_quantity)

    def calc_profit(self):
        ota = self.opening_transaction
        cta = self.closing_transaction

        if ota.category == "sell":
            open_profit = self.quantity / abs(ota.quantity) * (ota.value_eur + ota.fee_eur)
            close_profit = (self.quantity / abs(cta.quantity) * (cta.value_eur + cta.fee_eur)
                            if cta is not None else Decimal(0))
        else:
            assert ota.category == "buy"
            open_profit = Decimal(0)
            close_profit = ((self.quantity * (cta.price_eur - ota.price_eur)
                             + self.quantity / abs(ota.quantity) * ota.fee_eur
                             + self.quantity / abs(cta.quantity) * cta.fee_eur)
                            if cta is not None else Decimal(0))

        CalcProfitResult = namedtuple("CalcProfitResult", "open_profit close_profit")
        return CalcProfitResult(open_profit, close_profit)

    def is_relevant_for_tax_year(self, year):
        if self.opening_transaction.date.year == year and self.opening_transaction.category == "sell":
            return True

        if self.closing_transaction is not None and self.closing_transaction.date.year == year:
            return True

        return False
