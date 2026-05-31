class VisitStagingBuilder:

    def build(self, visits):

        return visits.rename(
            columns={
                "date_started": "visit_date",
                "date_stopped": "visit_end_date"
            }
        )