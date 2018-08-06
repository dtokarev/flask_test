import enum


class FileTypes(enum.Enum):
    VIDEO = 'VIDEO'
    SUBTITLE = 'SUBTITLE'
    AUDIO = 'AUDIO'
    JUNK = 'JUNK'


class ResourceType(enum.Enum):
    MOVIE = 'MOVIE'
    SERIES = 'SERIES'
