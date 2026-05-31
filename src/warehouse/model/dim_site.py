class DimSite:

    def build(self, encounters):
        return (
            encounters[["location"]]
            .drop_duplicates()
            .rename(columns={"location": "site_name"})
        )
