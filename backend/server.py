from collections.abc import Sequence
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from database import Database
import datetime

app = FastAPI()
db = Database()

origins = [
    "http://localhost:5173"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_transactions_raw(category: Optional[str] = None, 
                     start_date: Optional[datetime.date] = None,
                     end_date: Optional[datetime.date] = None) -> list[dict]:
    transactions = db.get_transactions_for_category(category, start_date, end_date)
    transactions = [dict(row) for row in transactions.mappings()]

    result = list()
    
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

@app.get("/categories")
def get_categories():
    categories = db.get_categories()
    return [row["id"] for row in categories.mappings()]

@app.get("/transactions")
def get_transactions(category: Optional[str] = None, 
                     start_date: Optional[datetime.date] = None,
                     end_date: Optional[datetime.date] = None,
                     smoothing: Optional[str] = None,
                     avg_days: int = 7):
    transactions = get_transactions_raw(category, start_date, end_date)
    match smoothing:
        case None:
            return transactions
        case "averaged":
            return get_transactions_averaged(transactions, avg_days)
        case "smoothed":
            return get_transactions_smoothed(transactions, avg_days)
        case _:
            return []

def get_transactions_averaged(transactions: list[dict], avg_days: int) -> list[dict]:
    
    dates = [t["date"] for t in transactions]
    amounts = [float(t["amount"]) for t in transactions]

    averaged_amounts = [0.0] * len(dates)
    for i in range(len(dates)):
        for d in range(-avg_days, avg_days+1):
            if 0 <= i + d < len(dates):
                averaged_amounts[i + d] += amounts[i] / (2*avg_days+1)
    
    return [{"date": dates[i], "amount": averaged_amounts[i]} for i in range(len(dates))]

def get_transactions_smoothed(transactions: list[dict], avg_days: int) -> list[dict]:
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

        smooth = convolve_smooth(start + mid + end)
        smoothed_amounts[i] = smooth
        
    return [{"date": dates[i], "amount": smoothed_amounts[i]} for i in range(n)]
 
        

def convolve_smooth(x: Sequence[float]) -> float:
    """
    
    Args:
        x: assumed to be equidistant points in [-1, 1]
    """

    bump = lambda y: np.exp(-1/(1-y**2))
    n = len(x)
    # scaling should be done in a way so that if the inputs are all 1s, then the output should be 1
    scaling = np.sum(np.ones(n) * bump(np.linspace(1, -1, n, endpoint=True)))

    return np.sum(x * bump(np.linspace(1, -1, n, endpoint=True))) / scaling


if __name__ == "__main__":
    pass