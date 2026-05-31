import duckdb


class DuckDBExporter:

    def export(self, df, table_name):

        conn = duckdb.connect(
            "healthcare_dw.duckdb"
        )

        conn.register(
            "temp_df",
            df
        )

        conn.execute(
            f"""
            CREATE OR REPLACE TABLE
            {table_name}
            AS
            SELECT *
            FROM temp_df
            """
        )