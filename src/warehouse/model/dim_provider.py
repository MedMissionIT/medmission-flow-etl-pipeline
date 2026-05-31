import pandas as pd


class DimProvider:

    def build(self, providers):

        if providers is None:
            raise ValueError("providers is None")

        if "provider_id" not in providers.columns:
            raise ValueError("provider_id missing in providers")

        dim = providers.copy()

        dim["provider_key"] = range(1, len(dim) + 1)

        return dim[[
            "provider_id",
            "provider_key"
        ]]