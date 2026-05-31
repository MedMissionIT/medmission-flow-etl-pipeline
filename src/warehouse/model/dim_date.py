import pandas as pd


class DimDate:

    def build(self, dates):

        if dates is None:
            raise ValueError("dates is None")

        df = pd.DataFrame()

        # SAFE parsing (OpenMRS + Excel + mixed formats)
        df["full_date"] = pd.to_datetime(dates, errors="coerce")

        if df["full_date"].isna().all():
            raise ValueError("All dates are invalid")

        df["date_key"] = df["full_date"].dt.strftime("%Y%m%d").astype("Int64")

        df["year"] = df["full_date"].dt.year
        df["month"] = df["full_date"].dt.month
        df["day"] = df["full_date"].dt.day
        df["quarter"] = df["full_date"].dt.quarter
        df["week"] = df["full_date"].dt.isocalendar().week.astype("Int64")

        # BI ADDITIONS
        df["day_name"] = df["full_date"].dt.day_name()
        df["is_weekend"] = df["full_date"].dt.weekday >= 5

        return df