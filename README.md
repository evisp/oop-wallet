# OOP Wallet

Companion code for the **Object-Oriented Design** module of the
[Augmented Software Engineering](https://evisp.github.io/augmented_software_engineering/)
handbook at Holberton School Albania.

One small digital wallet grows across the five tutorials of the module.
Each tutorial adds to the code from the one before, and each finished
stage is saved as a Git tag, so you can open the code exactly as it was
at the end of any tutorial.

## Versions

| Tag | Tutorial | What it adds |
|---|---|---|
| [`v1-classes`](../../tree/v1-classes) | [Classes & Object Model](https://evisp.github.io/augmented_software_engineering/02-foundations/oop/classes/) | The `Account` class: validation, properties, string representations |
| [`v2-inheritance`](../../tree/v2-inheritance) | [Inheritance & Polymorphism](https://evisp.github.io/augmented_software_engineering/02-foundations/oop/inheritance/) | `SavingsAccount` and `CheckingAccount`: `super()`, overriding, polymorphism |
| `v3-abstract` | Abstract Classes & Interfaces | Coming soon |
| `v4-uml` | Introduction to UML Modeling | Coming soon |
| `v5-patterns` | Introduction to Design Patterns | Coming soon |

## Run it

You need Python 3.10 or later.

```bash
git clone https://github.com/evisp/oop-wallet.git
cd oop-wallet
./wallet.py
```

## Open an earlier version

```bash
git tag                       # list the versions
git switch --detach v1-classes
git switch main               # back to the latest
```

Try to write each version yourself from the tutorial first, then compare
it with the tag.
