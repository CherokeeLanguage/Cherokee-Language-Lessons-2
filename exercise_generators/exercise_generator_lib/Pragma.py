import dataclasses

from ResponseLayout import ResponseLayout


@dataclasses.dataclass
class Pragma:
    plain_text: bool = False
    debug: bool = False
    depth: int = 5
    max_sets: int = 0
    layout: ResponseLayout = ResponseLayout.SINGLE_LINE
    include_reversed: bool = False
    only_reversed: bool = False
    max_set_size: int = 5
    sort: bool = True
    random: bool = False
    sep: str = ":"
    for_pictures: bool = False
    required: set[str] = dataclasses.field(default_factory=set)
