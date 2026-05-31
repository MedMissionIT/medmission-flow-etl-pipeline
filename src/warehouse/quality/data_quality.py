class DataQuality:

    def check_nulls(self, df):
        return df.isnull().sum()

    def check_duplicates(self, df, key):
        return df.duplicated(subset=[key]).sum()

    def validate_date_range(self, df, col):
        return df[col].min(), df[col].max()
