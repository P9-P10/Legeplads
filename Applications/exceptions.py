class InvalidTransformationException(Exception):
    pass

class InvalidQueryException(Exception):
    pass

class InvalidSelectionException(InvalidQueryException):
    pass

class AmbiguousColumnException(Exception):
    pass

class ColumnNotFoundException(Exception):
    pass

class TableNotFoundException(Exception):
    pass