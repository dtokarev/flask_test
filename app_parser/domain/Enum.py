import enum


class FileTypes(enum.Enum):
    VIDEO = 'VIDEO'
    SUBTITLE = 'SUBTITLE'
    AUDIO = 'AUDIO'
    JUNK = 'JUNK'


class ResourceType(enum.Enum):
    MOVIE = 'MOVIE'
    SERIES = 'SERIES'


class ResourceStatuses(enum.Enum):
    NOT_ENCODED = 'NOT_ENCODED'
    ENCODING = 'ENCODING'
    NOT_DEPLOYED = 'NOT_DEPLOYED'
    DEPLOYED = 'DEPLOYED'