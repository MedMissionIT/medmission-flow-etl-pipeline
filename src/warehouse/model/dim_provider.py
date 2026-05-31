class DimProvider:

    def build(self, providers):

        dim = providers.copy()

        dim["provider_key"] = range(1, len(dim)+1)

        return dim