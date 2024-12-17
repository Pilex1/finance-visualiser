import datetime
import sqlalchemy as sql
import sqlalchemy.sql.functions as func
import sqlalchemy.dialects.postgresql as psql
import pandas as pd
import numpy as np
import re
from constants import Constants, DescRules


class Database:
    def __init__(self):
        self.DATABASE_URL = "postgresql+psycopg2://pilex:pilex@localhost:5432/finance"
        self.engine = sql.create_engine(self.DATABASE_URL)

        self.metadata = sql.MetaData()

        self.conn = self.engine.connect()

        self.table_transaction = sql.Table(
            "transaction",
            self.metadata,
            sql.Column("id", sql.Integer, primary_key=True),
            sql.Column("date", sql.Date),
            sql.Column("value_date", sql.Date),
            sql.Column("amount", sql.DECIMAL(10, 2)),
            sql.Column("location", sql.VARCHAR),
            sql.Column("description_id", sql.VARCHAR,
                       sql.ForeignKey("description.id")),
            sql.Column("description", sql.VARCHAR),
            sql.Column("description_original", sql.VARCHAR),
            sql.Column("balance", sql.DECIMAL(10, 2)),
            sql.UniqueConstraint(
                "date", "amount", "balance", "description_original"),
        )
        self.table_description = sql.Table(
            "description",
            self.metadata,
            sql.Column("id", sql.VARCHAR, primary_key=True),
            sql.Column("processed", sql.Boolean),
            sql.Column("category_id", sql.VARCHAR,
                       sql.ForeignKey("category.id"))
        )
        self.table_category = sql.Table(
            "category",
            self.metadata,
            sql.Column("id", sql.VARCHAR, primary_key=True),
        )

    def __del__(self):
        self.conn.close()

    def drop_all(self):
        self.metadata.drop_all(self.engine)

    def initialise_empty_tables(self):
        """
        run this only at the very start when there are no tables in the database
        """

        self.metadata.create_all(self.engine)

        # initialise the category table
        categories = set(Constants.category_dict.values())
        if None in categories:
            categories.remove(None)
        categories_df = pd.DataFrame.from_dict({"id": list(categories)})
        self.conn.execute(psql.insert(self.table_category).values(
            categories_df.to_dict(orient="records")))
        self.conn.commit()

    @staticmethod
    def get_suburb_info(desc: str) -> tuple[str, str | None]:
        """
        given the description, extracts the suburb information if possible

        returns: a tuple of the description without suburb information, and the suburb information

        if unable to extract suburb information returns the original string and None
        """

        def extract_suburb(y: str, i: int):
            # search for a suburb name
            match = re.search(Constants.regex_suburb, y.lower())
            if match:
                start_index = match.span()[0]
                end_index = match.span()[1]
                # once we find a suburb name, we need to check the part of the string after the suburb name - this should be the state e.g. NSW and/or country e.g. AUS
                remainder = y[end_index:].lower()
                match_remainder = re.search(
                    "^" + Constants.regex_post_suburb, remainder)
                if match_remainder:
                    return desc[:i + start_index].strip(), y[start_index:].strip()
                else:
                    # not a valid match
                    # recursively try to extract the suburb
                    # from the substring formed by removing this "fake suburb"
                    return extract_suburb(y[end_index:], i + end_index)
            else:
                return desc, None

        result = extract_suburb(desc, 0)
        # if suburb extraction failed, try to see if the suburb name was just truncated
        if result[1] is None:
            # first, search for the post-suburb text
            match = re.search(Constants.regex_post_suburb, desc.lower())
            # if found, search for any truncated suburbs at the end
            if match:
                start_index = match.span()[0]
                match_truncated = re.search(
                    f"({Constants.regex_suburb_truncated})$", desc.lower()[:start_index].strip())
                if match_truncated:
                    i = match_truncated.span()[0]
                    desc_trunc = desc[:i].strip()
                    location_trunc = desc[i:].strip()
                    return desc_trunc, location_trunc

        return result

    @staticmethod
    def process_records(filename: str) -> pd.DataFrame:
        df = pd.read_csv(filename,
                         names=["date", "amount",
                                "description_original", "balance"],
                         parse_dates=["date"],
                         date_format="%d/%m/%Y")

        df["description"] = df["description_original"]
        desc = df["description"].str.split("Value Date: ").str.get(0)
        value_date = df["description"].str.split("Value Date: ").str.get(1)

        df["description"] = desc
        df["value_date"] = pd.to_datetime(value_date, format="%d/%m/%Y")

        df["description"] = df["description"].str.split("Card xx").str.get(0)

        # extract suburb location from description
        result = df["description"].apply(
            Database.get_suburb_info).apply(pd.Series)
        df["description"] = result[0]
        df["location"] = result[1]

        df = df.replace({np.nan: None})
        return df

    @staticmethod
    def process_description(desc: str) -> tuple[str, bool]:

        if desc in DescRules.display_name_dict:
            return DescRules.display_name_dict[desc], True

        for s in DescRules.starts_with_set:
            if desc.lower().startswith(s.lower()):
                return s, True

        for k, v in DescRules.starts_with_dict.items():
            if desc.lower().startswith(k.lower()):
                return v, True

        for k, v in DescRules.regex_dict.items():
            if re.search(k, desc, flags=re.IGNORECASE):
                return v, True

        return desc.title(), False

    def add_records(self, csv_file: str):
        # first we need to process the descriptions, and insert them into the description table
        df = Database.process_records(csv_file)
        descriptions = df["description"].apply(Database.process_description)
        descriptions = pd.DataFrame.from_records(
            descriptions, columns=["id", "processed"])
        descriptions["category_id"] = descriptions["id"].apply(
            lambda x: Constants.category_dict[x] if x in Constants.category_dict else None)
        self.conn.execute(psql.insert(self.table_description).values(
            descriptions.to_dict(orient="records")).on_conflict_do_nothing())

        # then we can update the transaction table, with the foreign key constraint to the description
        df["description_id"] = descriptions["id"]
        self.conn.execute(psql.insert(self.table_transaction).values(
            df.to_dict(orient="records")).on_conflict_do_nothing())

        # commmit changes
        self.conn.commit()

    def get_transactions_groupby(self):
        """
        returns the total amount spent on each day and each category
        """
        description = self.table_description
        transaction = self.table_transaction

        coalesce_date = func.coalesce(
            transaction.c["value_date"], transaction.c["date"]).label("date")
        query = (
            sql.select(
                coalesce_date,
                description.c["category_id"],
                func.sum(transaction.c["amount"]).label("amount")
            )
            .select_from(
                transaction.join(
                    description, transaction.c["description_id"] == description.c["id"], isouter=True)
            )
            .group_by(coalesce_date, description.c["category_id"])
            .order_by(coalesce_date.asc())
        )

        return self.conn.execute(query)

    def get_transactions_for_category(self,
                                      category: str | None = None,
                                      start_date: datetime.date | None = None,
                                      end_date: datetime.date | None = None):
        """
        returns the total amount spent on each day in a particular category (or if category is not given, in total)
        """
        description = self.table_description
        transaction = self.table_transaction

        coalesce_date = func.coalesce(
            transaction.c["value_date"], transaction.c["date"]).label("date")
        query = (
            sql.select(
                coalesce_date,
                func.sum(transaction.c["amount"]).label("amount")
            )
            .select_from(
                transaction.join(
                    description, transaction.c["description_id"] == description.c["id"], isouter=True)
            )
        )
        if category is not None:
            query = query.where(description.c["category_id"] == category)
        if start_date is not None:
            query = query.where(coalesce_date >= start_date)
        if end_date is not None:
            query = query.where(coalesce_date <= end_date)

        query = (query
                 .group_by(coalesce_date)
                 .order_by(coalesce_date.asc()))

        return self.conn.execute(query)

    def get_categories(self):
        category = self.table_category
        query = sql.select(category.c["id"]).select_from(category)
        return self.conn.execute(query)


if __name__ == "__main__":
    db = Database()

    new_db = False
    if new_db:
        db.drop_all()
        db.initialise_empty_tables()

        db.add_records("data/2022to2024transactions-Copy1.csv")
        db.add_records("data/2024-dec.csv")

        print("Records inserted into database")

    result = db.get_transactions_groupby()
    print(result.keys())
    print(result.fetchmany(5))

    result = db.get_transactions_for_category("fuel")
    print(result.keys())
    print(result.fetchmany(5))

DB = Database()