# src/warehouse/model/dim_date.py

import pandas as pd


class DimDate:

    def build(self, dates):

        dates = pd.Series(dates).dropna()

        df = pd.DataFrame()

        df["full_date"] = (
            pd.to_datetime(dates)
            .dt.normalize()
        )

        df = (
            df
            .drop_duplicates()
            .sort_values("full_date")
        )

        df["date_key"] = (
            df["full_date"]
            .dt.strftime("%Y%m%d")
            .astype(int)
        )

        df["year"] = df["full_date"].dt.year
        df["month"] = df["full_date"].dt.month
        df["quarter"] = df["full_date"].dt.quarter
        df["day"] = df["full_date"].dt.day

        return df.reset_index(drop=True)