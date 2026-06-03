import argparse

from loan.eligibility import evaluate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--income", type=float, default=0.0)
    parser.add_argument("--debt", type=float, default=0.0)
    parser.add_argument("--tenure-months", type=int, default=0)
    parser.add_argument("--age", type=int, default=0)
    parser.add_argument("--savings-balance", type=float, default=0.0)
    parser.add_argument("--late-payments", type=int, default=0)
    parser.add_argument("--dependents", type=int, default=0)
    args = parser.parse_args()
    result = evaluate(args.income, args.debt, args.tenure_months, args.age,
                      args.savings_balance, args.late_payments, args.dependents,
                      history=[])
    print(result)


if __name__ == "__main__":
    main()
