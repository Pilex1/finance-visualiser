import datetime

from src.database import DB
import src.math as math
from typing import TypedDict


class Transaction(TypedDict):
    date: datetime.date
    amount: float


def get_transactions_raw(category: str | None = None,
                         start_date: datetime.date | None = None,
                         end_date: datetime.date | None = None) -> list[Transaction]:

    transactions = DB.get_transactions_for_category(
        category, start_date, end_date)
    transactions = [Transaction(**row) for row in transactions.mappings()]

    result: list[Transaction] = []

    # starting at the earliest date in the transactions, and incrementing by one day until today
    start: datetime.date = start_date if start_date is not None else transactions[0]["date"]
    end: datetime.date = end_date if end_date is not None else transactions[-1]["date"]

    date = start
    i = 0
    while date <= end:
        if i >= len(transactions):
            result.append({"date": date, "amount": 0})
        elif date == transactions[i]["date"]:
            result.append(transactions[i])
            i += 1
        else:
            assert date < transactions[i]["date"]
            result.append({"date": date, "amount": 0})

        date += datetime.timedelta(days=1)
    return result


def get_transactions_averaged(transactions: list[Transaction], avg_days: int) -> list[Transaction]:

    dates = [t["date"] for t in transactions]
    amounts = [float(t["amount"]) for t in transactions]

    averaged_amounts = [0.0] * len(dates)
    for i in range(len(dates)):
        for d in range(-avg_days, avg_days+1):
            if 0 <= i + d < len(dates):
                averaged_amounts[i + d] += amounts[i] / (2*avg_days+1)

    return [{"date": dates[i], "amount": averaged_amounts[i]} for i in range(len(dates))]


def get_transactions_smoothed(transactions: list[Transaction], avg_days: int) -> list[Transaction]:
    dates = [t["date"] for t in transactions]
    amounts = [float(t["amount"]) for t in transactions]

    n = len(dates)
    smoothed_amounts = [0.0] * n

    for i in range(n):
        start = []
        end = []
        if i - avg_days < 0:
            start = [0] * (avg_days - i)
        if i + avg_days >= n:
            end = [0] * (i + avg_days - n + 1)
        mid = amounts[max(0, i - avg_days): min(n, i + avg_days)]

        smooth = math.convolve_smooth(start + mid + end)
        smoothed_amounts[i] = smooth

    return [{"date": dates[i], "amount": smoothed_amounts[i]} for i in range(n)]
