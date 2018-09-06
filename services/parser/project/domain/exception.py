class NonCriticalException(Exception):
    pass


class ResultNotFoundException(NonCriticalException):
    pass


class ParserNonCriticalException(NonCriticalException):
    pass
