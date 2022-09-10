from enum import Enum
from enum import auto


class ResponseLayout(Enum):
    NONE = auto()
    ENUMERATE = auto()
    PLAIN = auto()
    ITEMIZE = auto()
    SINGLE_LINE = auto()

    @classmethod
    def value_of(cls, value: str) -> "ResponseLayout":
        value = value.upper().strip()
        for k, v in cls.__members__.items():
            if k == value:
                return v
        return ResponseLayout.NONE
