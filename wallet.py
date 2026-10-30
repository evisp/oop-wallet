#!/usr/bin/env python3
"""A small digital wallet, built up across the OOP tutorials.

Version 5: Introduction to Design Patterns.
"""
import json
from abc import ABC, abstractmethod


def _check_amount(amount):
    """Raise if amount is not a positive whole number."""
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount must be an integer")
    if amount <= 0:
        raise ValueError("amount must be positive")


class TransactionLog(list):
    """A list that only accepts (kind, amount) transaction entries."""

    KINDS = ("deposit", "withdraw", "payment", "interest", "fee")

    def __init__(self, entries=()):
        super().__init__()
        self.extend(entries)

    def append(self, entry):
        """Add one entry, after checking it."""
        self._check(entry)
        super().append(entry)

    def extend(self, entries):
        """Add several entries; check them all before adding any."""
        entries = list(entries)
        for entry in entries:
            self._check(entry)
        super().extend(entries)

    def total(self, kind):
        """Return the sum of all amounts of one kind."""
        return sum(amount for k, amount in self if k == kind)

    def _check(self, entry):
        if not isinstance(entry, tuple) or len(entry) != 2:
            raise TypeError("entry must be a (kind, amount) tuple")
        kind, amount = entry
        if kind not in self.KINDS:
            raise ValueError(f"unknown kind: {kind!r}")
        _check_amount(amount)


class HistoryMixin:
    """Give a class a transaction history."""

    def _record(self, kind, amount):
        """Add one entry to this object's history."""
        if "_history" not in vars(self):
            self._history = TransactionLog()
        self._history.append((kind, amount))

    @property
    def history(self):
        """A copy of the transaction history."""
        return TransactionLog(vars(self).get("_history", ()))


class JSONMixin:
    """Give a class a dictionary and JSON form of its simple attributes."""

    def to_dict(self):
        """Return the type and simple attributes as a dictionary."""
        data = {"type": type(self).__name__}
        for name, value in vars(self).items():
            if isinstance(value, (str, int, float, bool)):
                data[name.lstrip("_")] = value
        return data

    def to_json(self):
        """Return to_dict() as a JSON string."""
        return json.dumps(self.to_dict())


class ObservableMixin:
    """Let observers subscribe to this object's events, by topic.

    Every recorded transaction is published as an event whose topic is
    its kind: "deposit", "withdraw", "payment", "interest" or "fee".
    """

    def subscribe(self, observer, topics=None):
        """Send observer the events in topics, or every event if None."""
        if not callable(getattr(observer, "notify", None)):
            raise TypeError("observer must have a notify method")
        if isinstance(topics, str):
            topics = [topics]
        wanted = None if topics is None else frozenset(topics)
        if "_observers" not in vars(self):
            self._observers = []
        self._observers.append((observer, wanted))

    def unsubscribe(self, observer):
        """Stop sending events to observer."""
        observers = vars(self).get("_observers", [])
        observers[:] = [(o, t) for o, t in observers if o is not observer]

    def _publish(self, topic, amount):
        """Notify every observer that wants this topic."""
        for observer, wanted in list(vars(self).get("_observers", ())):
            if wanted is None or topic in wanted:
                observer.notify(self, topic, amount)

    def _record(self, kind, amount):
        """Record the transaction, then publish it as an event."""
        super()._record(kind, amount)
        self._publish(kind, amount)


class Payer(ABC):
    """Interface: anything that can pay an amount."""

    @abstractmethod
    def pay(self, amount):
        """Pay amount, or raise ValueError; return what is left."""


class Account(ObservableMixin, HistoryMixin, JSONMixin, Payer):
    """Abstract base for wallet accounts holding money, in whole lek."""

    currency = "ALL"

    def __init__(self, owner, balance=0):
        """Create an account for owner with an opening balance."""
        self.owner = owner
        if isinstance(balance, bool) or not isinstance(balance, int):
            raise TypeError("balance must be an integer")
        if balance < 0:
            raise ValueError("balance must not be negative")
        self._balance = balance
        if balance:
            self._record("deposit", balance)

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
        _check_amount(amount)
        self._balance += amount
        self._record("deposit", amount)
        return self._balance

    def withdraw(self, amount):
        """Take amount from the balance and return the new balance."""
        _check_amount(amount)
        if amount > self._balance:
            raise ValueError("insufficient funds")
        self._balance -= amount
        self._record("withdraw", amount)
        return self._balance

    def pay(self, amount):
        """Pay amount from this account; return the new balance."""
        return self.withdraw(amount)

    @abstractmethod
    def month_end(self):
        """Apply end-of-month rules and return the new balance."""

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
        if interest > 0:
            self._balance += interest
            self._record("interest", interest)
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
        _check_amount(amount)
        if self._balance - amount < -self._overdraft:
            raise ValueError("overdraft limit exceeded")
        self._balance -= amount
        self._record("withdraw", amount)
        return self._balance

    def month_end(self):
        """Charge the monthly fee if overdrawn; return the new balance."""
        if self._balance < 0:
            self._balance -= self.fee
            self._record("fee", self.fee)
        return self._balance

    def __str__(self):
        return f"{super().__str__()} (overdraft {self.overdraft})"

    def __repr__(self):
        return (f"{type(self).__name__}(owner={self.owner!r}, "
                f"balance={self.balance}, overdraft={self.overdraft})")


class GiftCard(ObservableMixin, HistoryMixin, JSONMixin, Payer):
    """A prepaid card with a fixed value. It is not an account."""

    currency = "ALL"

    def __init__(self, code, value):
        """Create a gift card with a code and a starting value."""
        if not isinstance(code, str) or not code.strip():
            raise ValueError("code must be a non-empty string")
        _check_amount(value)
        self._code = code.strip()
        self._value = value
        self._holder = None

    @property
    def holder(self):
        """The customer holding this card, or None."""
        return self._holder

    @property
    def value(self):
        """What is left on the card."""
        return self._value

    def pay(self, amount):
        """Pay amount from the card; return the value left."""
        _check_amount(amount)
        if amount > self._value:
            raise ValueError("not enough value on the card")
        self._value -= amount
        self._record("payment", amount)
        return self._value

    def __str__(self):
        return f"Gift card {self._code}: {self.value} {self.currency}"

    def __repr__(self):
        return f"GiftCard(code={self._code!r}, value={self.value})"


class AccountFactory:
    """Create accounts by kind, from a registry of account classes."""

    def __init__(self):
        self._registry = {}

    def register(self, kind, account_class):
        """Make kind create account_class, and return account_class."""
        if not isinstance(kind, str) or not kind.strip():
            raise ValueError("kind must be a non-empty string")
        if not (isinstance(account_class, type)
                and issubclass(account_class, Account)):
            raise TypeError("account_class must be a subclass of Account")
        self._registry[kind] = account_class
        return account_class

    def create(self, kind, owner, **options):
        """Create an account of a registered kind."""
        if kind not in self._registry:
            raise ValueError(f"unknown account kind: {kind!r}")
        return self._registry[kind](owner, **options)

    def kinds(self):
        """The registered kinds, sorted."""
        return sorted(self._registry)


account_factory = AccountFactory()
account_factory.register("savings", SavingsAccount)
account_factory.register("checking", CheckingAccount)


class Customer(JSONMixin):
    """A wallet customer, who can hold accounts and gift cards."""

    def __init__(self, name, email):
        """Create a customer with a name and an email address."""
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string")
        if not isinstance(email, str) or "@" not in email:
            raise ValueError("email must contain @")
        self._name = name.strip()
        self._email = email.strip()
        self._accounts = []
        self._gift_cards = []

    @property
    def name(self):
        """The customer's name."""
        return self._name

    @property
    def email(self):
        """The customer's email address."""
        return self._email

    @property
    def accounts(self):
        """The customer's accounts, as a tuple."""
        return tuple(self._accounts)

    @property
    def gift_cards(self):
        """The customer's gift cards, as a tuple."""
        return tuple(self._gift_cards)

    def add_account(self, account):
        """Add an account this customer owns, and return it."""
        if not isinstance(account, Account):
            raise TypeError("account must be an Account")
        if account.owner != self._name:
            raise ValueError("account belongs to another customer")
        if account in self._accounts:
            raise ValueError("account already added")
        self._accounts.append(account)
        return account

    def open_account(self, kind, **options):
        """Open a new account of a registered kind, and return it."""
        account = account_factory.create(kind, self._name, **options)
        return self.add_account(account)

    def add_gift_card(self, card):
        """Give this customer a gift card nobody else holds; return it."""
        if not isinstance(card, GiftCard):
            raise TypeError("card must be a GiftCard")
        if card.holder is not None:
            raise ValueError("gift card already has a holder")
        card._holder = self
        self._gift_cards.append(card)
        return card

    def total_balance(self):
        """Return the sum of all account balances."""
        return sum(account.balance for account in self._accounts)

    def month_end(self):
        """Run the end-of-month rules on every account."""
        for account in self._accounts:
            account.month_end()

    def __str__(self):
        return (f"{self.name} <{self.email}>: "
                f"accounts: {len(self._accounts)}, "
                f"gift cards: {len(self._gift_cards)}")

    def __repr__(self):
        return f"Customer(name={self.name!r}, email={self.email!r})"


class PayerDecorator(Payer):
    """Wrap a payer to add behaviour to pay; forward everything else."""

    def __init__(self, wrapped):
        if not callable(getattr(wrapped, "pay", None)):
            raise TypeError("wrapped must have a pay method")
        self._wrapped = wrapped

    def pay(self, amount):
        """Pass the payment on to the wrapped payer."""
        return self._wrapped.pay(amount)

    def __getattr__(self, name):
        return getattr(self._wrapped, name)

    def __str__(self):
        return str(self._wrapped)

    def __repr__(self):
        return f"{type(self).__name__}({self._wrapped!r})"


class SpendingLimit(PayerDecorator):
    """Refuse any single payment above a limit."""

    def __init__(self, wrapped, limit):
        super().__init__(wrapped)
        _check_amount(limit)
        self._limit = limit

    def pay(self, amount):
        """Pay amount, unless it is over the limit."""
        if amount > self._limit:
            raise ValueError(f"payment over the limit of {self._limit}")
        return super().pay(amount)


class Receipts(PayerDecorator):
    """Keep a receipt for every payment that goes through."""

    def __init__(self, wrapped):
        super().__init__(wrapped)
        self.receipts = []

    def pay(self, amount):
        """Pay amount, then write a receipt."""
        result = super().pay(amount)
        self.receipts.append(f"Paid {amount} ALL")
        return result


class RoundUp(PayerDecorator):
    """Round each payment up to the next 100 and save the difference."""

    def __init__(self, wrapped, savings):
        super().__init__(wrapped)
        if not isinstance(savings, Account):
            raise TypeError("savings must be an Account")
        self._savings = savings

    def pay(self, amount):
        """Pay amount, then move the round-up into savings if possible."""
        result = super().pay(amount)
        spare = -amount % 100
        if spare:
            try:
                result = super().pay(spare)
            except ValueError:
                return result
            self._savings.deposit(spare)
        return result


class AuditLog:
    """Observer: keep one line for every event it is sent."""

    def __init__(self):
        self.lines = []

    def notify(self, source, topic, amount):
        """Record the event."""
        self.lines.append(f"{type(source).__name__} {topic} {amount}")


class SMSAlert:
    """Observer: text a phone number about the events it is sent."""

    def __init__(self, phone):
        self.phone = phone
        self.sent = []

    def notify(self, source, topic, amount):
        """Send a short message about the event."""
        self.sent.append(f"To {self.phone}: {topic} of {amount} ALL")


def checkout(payer, amount):
    """Charge amount to anything that can pay; return what it returns."""
    return payer.pay(amount)


if __name__ == "__main__":
    ada = Customer("Ada", "ada@example.com")
    savings = ada.open_account("savings", balance=1000, rate=2)
    checking = ada.open_account("checking", overdraft=500)

    audit = AuditLog()
    sms = SMSAlert("+355 69 000 0000")
    for account in ada.accounts:
        account.subscribe(audit)
    checking.subscribe(sms, topics=["fee"])

    payer = RoundUp(Receipts(SpendingLimit(checking, limit=500)), savings)
    checkout(payer, 230)
    ada.month_end()

    for account in ada.accounts:
        print(account)
    print(*payer.receipts, sep="\n")
    print(*audit.lines, sep="\n")
    print(*sms.sent, sep="\n")
