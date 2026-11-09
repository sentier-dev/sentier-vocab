class GraphFilterError(Exception):
    """Filter on graph produced undesired result"""


class MissingDimensionVector(Exception):
    """Unit is missing `hasDimensionVector` attribute"""


class ValidationError(Exception):
    """The terms/ or relations/ layer violates term.yaml or relation.yaml."""


# Old name, kept one release for callers that catch it.
SchemaValidationError = ValidationError
