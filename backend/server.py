
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.transactions import get_transactions_averaged, get_transactions_raw, get_transactions_smoothed
from src.database import DB
import datetime

app = FastAPI()

origins = [
    "http://localhost:5173"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/categories")
def get_categories():
    categories = DB.get_categories()
    return [row["id"] for row in categories.mappings()]


@app.get("/transactions")
def get_transactions(category: str | None = None,
                     start_date: datetime.date | None = None,
                     end_date: datetime.date | None = None,
                     smoothing: str | None = None,
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


if __name__ == "__main__":
    pass
