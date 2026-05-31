class FactOphtalmo:

    def build(self, screening, surgery):
        screening["event_type"] = "SCREENING"
        surgery["event_type"] = "SURGERY"

        return screening._append(surgery, ignore_index=True)
