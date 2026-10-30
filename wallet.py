#!/usr/bin/env python3
"""A small digital wallet, built up across the OOP tutorials.

Version 2: Inheritance & Polymorphism.
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

    def month_end(self):
        """Apply end-of-month rules and return the new balance.

        A plain account has none.
        """
        return self._balance

    def __str__(self):
        return f"{self.owner}: {self.balance} {self.currency}"

    def __repr__(self):
        return (f"{type(self).__name__}(owner={self.owner!r}, "
                f"balance={self.balance})")


class SavingsAccount(Account):
    """An account that earns interest every month."""

    def __init__(self, owner, balance=0, rate=1):
        """Create a savings account; rate is monthly interest in percent."""
        super().__init__(owner, balance)
        if isinstance(rate, bool) or not isinstance(rate, int):
            raise TypeError("rate must be an integer")
        if not 0 <= rate <= 10:
            raise ValueError("rate must be between 0 and 10")
        self._rate = rate

    @property
    def rate(self):
        """Monthly interest rate, in whole percent."""
        return self._rate

    def add_interest(self):
        """Add this month's interest and return the amount added."""
        interest = self._balance * self._rate // 100
        self._balance += interest
        return interest

    def month_end(self):
        """Add this month's interest and return the new balance."""
        self.add_interest()
        return self._balance

    def __repr__(self):
        return (f"{type(self).__name__}(owner={self.owner!r}, "
                f"balance={self.balance}, rate={self.rate})")


class CheckingAccount(Account):
    """An everyday account that may go below zero, up to a limit."""

    fee = 100

    def __init__(self, owner, balance=0, overdraft=0):
        """Create a checking account with an overdraft limit."""
        super().__init__(owner, balance)
        if isinstance(overdraft, bool) or not isinstance(overdraft, int):
            raise TypeError("overdraft must be an integer")
        if overdraft < 0:
            raise ValueError("overdraft must not be negative")
        self._overdraft = overdraft

    @property
    def overdraft(self):
        """How far below zero the balance may go."""
        return self._overdraft

    def withdraw(self, amount):
        """Take amount out, letting the balance go down to -overdraft."""
        self._check_amount(amount)
        if self._balance - amount < -self._overdraft:
            raise ValueError("overdraft limit exceeded")
        self._balance -= amount
        return self._balance

    def month_end(self):
        """Charge the monthly fee if overdrawn; return the new balance."""
        if self._balance < 0:
            self._balance -= self.fee
        return self._balance

    def __str__(self):
        return f"{super().__str__()} (overdraft {self.overdraft})"

    def __repr__(self):
        return (f"{type(self).__name__}(owner={self.owner!r}, "
                f"balance={self.balance}, overdraft={self.overdraft})")


if __name__ == "__main__":
    accounts = [
        Account("Ada", 500),
        SavingsAccount("Grace", 1000, rate=2),
        CheckingAccount("Linus", overdraft=500),
    ]
    accounts[2].withdraw(300)
    for account in accounts:
        account.month_end()
        print(account)
    total = sum(account.balance for account in accounts)
    print(f"Total: {total} {Account.currency}")
