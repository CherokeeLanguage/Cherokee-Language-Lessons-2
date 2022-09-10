import dataclasses


@dataclasses.dataclass
class ReplacementSet:
    field: str | None = None
    replacements: list[str] = dataclasses.field(default_factory=list)
    deck: list[str] = dataclasses.field(default_factory=list)
