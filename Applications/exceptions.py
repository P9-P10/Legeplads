
class InvalidTransformationException(Exception):
    pass

class InvalidQueryException(Exception):
    pass

class InvalidSelectionException(InvalidQueryException):
    pass