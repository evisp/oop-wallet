#!/usr/bin/env python3
"""A small digital wallet, built up across the OOP tutorials.

Version 1: Classes & Object Model.
"""


class Account:
    """A wallet account holding money, in whole lek."""

    currency = "ALL"

    def __init__(self, owner, balance=0):
        """Create an account for owner with an opening balance."""
        self.owner = owner
        if isinstance(balance, bool) or not isinstance(balance, int):
            raise TypeError("balance must be an integer")
        if balance < 0:
            raise ValueError("balance must not be negative")
        self._balance = balance

    @property
    def owner(self):
        """The account holder's name."""
        return self._owner

    @owner.setter
    def owner(self, value):
        if not isinstance(value, str):
            raise TypeError("owner must be a string")
        if not value.strip():
            raise ValueError("owner must not be empty")
        self._owner = value.strip()

    @property
    def balance(self):
        """The current balance. Read-only: use deposit and withdraw."""
        return self._balance

    def deposit(self, amount):
        """Add amount to the balance and return the new balance."""
        self._check_amount(amount)
        self._balance += amount
        return self._balance

    def withdraw(self, amount):
        """Take amount from the balance and return the new balance."""
        self._check_amount(amount)
        if amount > self._balance:
            raise ValueError("insufficient funds")
        self._balance -= amount
        return self._balance

    def _check_amount(self, amount):
        """Raise if amount is not a positive whole number."""
        if isinstance(amount, bool) or not isinstance(amount, int):
            raise TypeError("amount must be an integer")
        if amount <= 0:
            raise ValueError("amount must be positive")

    def __str__(self):
        return f"{self.owner}: {self.balance} {self.currency}"

    def __repr__(self):
        return f"Account(owner={self.owner!r}, balance={self.balance})"


if __name__ == "__main__":
    ada = Account("Ada", 500)
    ada.deposit(200)
    ada.withdraw(100)
    print(ada)
    print(repr(ada))
