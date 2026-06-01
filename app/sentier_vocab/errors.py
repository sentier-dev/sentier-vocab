class GraphFilterError(Exception):
    """Filter on graph produced undesired result"""

    pass


class MissingDimensionVector(Exception):
    """Unit is missing `hasDimensionVector` attribute"""

    pass


class SchemaValidationError(Exception):
    """A data file failed validation against its LinkML schema."""

    pass
