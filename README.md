# loan-eligibility

Loan eligibility evaluation for a cooperativa de ahorro y crédito.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run the tests

```bash
pytest
```

## CLI

```bash
python -m loan.cli --income 1500 --debt 400 --tenure-months 24 --age 30 --savings-balance 800
```
