class CsvExporter:

    def export(self, dataframe, path):

        dataframe.to_csv(path, index=False)