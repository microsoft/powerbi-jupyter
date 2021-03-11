from enum import IntEnum

# Permission for embedding Power BI report
class Permissions(IntEnum):
    READ = 0
    READWRITE = 1
    COPY = 2
    CREATE = 4
    ALL = 7

# Type of token for embedding Power BI report
class TokenType(IntEnum):
    AAD = 0
    EMBED = 1

# Embed mode for embedding Power BI report
class EmbedMode(IntEnum):
    VIEW = 0
    EDIT = 1
    CREATE = 2

# Type of data to be exported
class ExportDataType(IntEnum):
    SUMMARIZED = 0
    UNDERLYING = 1
