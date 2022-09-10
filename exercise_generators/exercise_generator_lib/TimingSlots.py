import dataclasses


@dataclasses.dataclass
class TimingSlots:
    slots: set[int] = dataclasses.field(default_factory=set)

    def is_used(self, seconds_start:int, length:int)->bool:
        for ix in range(seconds_start, seconds_start+length):
            if ix in self.slots:
                return True
        return False

    def mark_used(self, seconds_start:int, length:int)->None:
        for ix in range(seconds_start, seconds_start+length):
            self.slots.add(ix)
