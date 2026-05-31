import pandas as pd


class DimDate:

    def build(self, df, col="date"):
        d = pd.DataFrame()
        d["date"] = pd.to_datetime(df[col], errors="coerce")
        d["year"] = d["date"].dt.year
        d["month"] = d["date"].dt.month
        d["week"] = d["date"].dt.isocalendar().week
        return d.drop_duplicates()
