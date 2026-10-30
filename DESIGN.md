# Design

The wallet's design, drawn in [Mermaid](https://mermaid.js.org). GitHub draws these
diagrams directly. They are explained in the
[UML](https://evisp.github.io/augmented_software_engineering/02-foundations/oop/uml/)
and [Design Patterns](https://evisp.github.io/augmented_software_engineering/02-foundations/oop/design-patterns/)
tutorials.

## Domain

```mermaid
classDiagram
    direction TB
    class Customer {
        +name: str
        +email: str
        +accounts: tuple
        +gift_cards: tuple
        +add_account(account) Account
        +add_gift_card(card) GiftCard
        +total_balance() int
        +month_end()
    }
    class Payer {
        <<interface>>
        +pay(amount: int)* int
    }
    class Account {
        <<abstract>>
        +owner: str
        +balance: int
        +deposit(amount: int) int
        +withdraw(amount: int) int
        +month_end()* int
    }
    class SavingsAccount {
        +rate: int
        +add_interest() int
        +month_end() int
    }
    class CheckingAccount {
        +overdraft: int
        +fee: int$
        +withdraw(amount: int) int
        +month_end() int
    }
    class GiftCard {
        +value: int
        +holder: Customer
        +pay(amount: int) int
    }
    class TransactionLog {
        +total(kind: str) int
    }
    Payer <|.. Account
    Payer <|.. GiftCard
    Account <|-- SavingsAccount
    Account <|-- CheckingAccount
    Customer "1" --> "0..*" Account : holds
    Customer "0..1" o-- "0..*" GiftCard : holds
    Account "1" *-- "1" TransactionLog : history
    GiftCard "1" *-- "1" TransactionLog : history
```

## How the code shares behaviour

```mermaid
classDiagram
    class HistoryMixin {
        <<mixin>>
        +history: TransactionLog
        #_record(kind, amount)
    }
    class JSONMixin {
        <<mixin>>
        +to_dict() dict
        +to_json() str
    }
    class list {
        <<built-in>>
    }
    HistoryMixin <|-- Account
    JSONMixin <|-- Account
    HistoryMixin <|-- GiftCard
    JSONMixin <|-- GiftCard
    JSONMixin <|-- Customer
    list <|-- TransactionLog
    HistoryMixin ..> TransactionLog : creates
```

## Paying with checkout()

```mermaid
sequenceDiagram
    participant M as __main__
    participant C as checkout()
    participant A as checking: CheckingAccount
    participant L as history: TransactionLog
    M->>C: checkout(checking, 300)
    C->>A: pay(300)
    A->>A: withdraw(300)
    alt within the overdraft limit
        A->>L: append(("withdraw", 300))
        A-->>C: -300
        C-->>M: -300
    else over the limit
        A-->>C: raises ValueError
        C-->>M: raises ValueError
    end
```

## End of the month

```mermaid
sequenceDiagram
    participant M as __main__
    participant C as ada: Customer
    participant A as account: Account
    M->>C: month_end()
    loop for each account in ada.accounts
        C->>A: month_end()
        Note right of A: runs the subclass's own month_end
        A-->>C: new balance
    end
    C-->>M: None
```

