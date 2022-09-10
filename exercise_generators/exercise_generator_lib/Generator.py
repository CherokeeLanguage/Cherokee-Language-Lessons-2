import dataclasses
import math
import re
import shutil

import LyxTemplate
from pathlib import Path
from random import Random

from ChallengeResponsePair import ChallengeResponsePair
from Pragma import Pragma
from ResponseLayout import ResponseLayout
from ReplacementSet import ReplacementSet
from TimingSlots import TimingSlots
from ChallengeResponsePair import normalize
from itertools import islice


def partition_list(items: list, sublist_size: int) -> list[list]:
    items = iter(items)
    return [*iter(lambda: tuple(islice(items, sublist_size)), ())]


def get_value(key: str, line: str) -> str:
    tmp: str = line.split(key, 1)[1].strip()
    if " " in tmp:
        tmp = tmp[:tmp.index(" ")].strip()
    return tmp


def write_debug_response_pairs(debug_out_file: Path, debug_challenges: list[ChallengeResponsePair]) -> None:
    text = ""
    for c in debug_challenges:
        text += c.challenge.replace("\t", "\\t").replace("\n", "\\n")
        text += "\n"
        text += c.response.replace("\t", "\\t").replace("\n", "\\n")
        text += "\n"
        text += "\n"
    with debug_out_file.open("w") as w:
        w.write(text)


def write_challenge_response_pairs(out_file: Path, queued: list[ChallengeResponsePair]) -> None:
    with out_file.open("w") as w:
        for q in queued:
            w.write(str(q))
            w.write("\n")


def write_lyx_challenge_response_pairs(pragma: Pragma, out_file: Path, queued: list[ChallengeResponsePair]) -> None:
    sets: int = math.ceil(float(len(queued)) / float(pragma.max_set_size))
    count_per_set: int = math.ceil(float(len(queued)) / float(sets))
    print(f"LyX: Sets: {sets:,}. Per set: {count_per_set:,}")
    sublists = partition_list(queued, count_per_set)
    lyx_challenges_only: str = ""
    lyx_challenges_response: str = ""
    if pragma.max_sets and len(sublists) > pragma.max_sets:
        sublists = sublists[:pragma.max_sets]
    lyx_challenges_only += LyxTemplate.doc_start
    lyx_challenges_response += LyxTemplate.doc_start

    section: int = 1
    for sublist in sublists:
        lyx_challenges_only += LyxTemplate.subsubsection(section)
        lyx_challenges_response += LyxTemplate.subsubsection(section)
        lyx_challenges_only += LyxTemplate.multi_col2_begin
        lyx_challenges_response += LyxTemplate.multi_col2_begin
        pair: ChallengeResponsePair
        for pair in sublist:
            lyx_challenges_only += pair.lyx(ResponseLayout.NONE)
            lyx_challenges_response += pair.lyx(pragma.layout)
        lyx_challenges_only += LyxTemplate.multi_col2_end
        lyx_challenges_response += LyxTemplate.multi_col2_end
        section += 1
    lyx_challenges_only += LyxTemplate.doc_end
    lyx_challenges_response += LyxTemplate.doc_end

    with out_file.with_stem(out_file.stem + "-co").open("w") as w:
        w.write(lyx_challenges_only)
    with out_file.with_stem(out_file.stem + "-cr").open("w") as w:
        w.write(lyx_challenges_response)


def sort_by_len_alpha(challenges: list[ChallengeResponsePair]) -> None:
    challenges.sort(key=lambda c: (len(c.challenge), c.challenge))


@dataclasses.dataclass
class Generator:
    in_folder: Path = Path("input")
    out_folder: Path = Path("output")

    random_replacements: dict[str, ReplacementSet] = dataclasses.field(default_factory=dict)

    def list_files(self) -> list[Path]:
        files = [*self.in_folder.glob("*.psv")]
        return files

    def run(self) -> None:
        if not self.in_folder.exists():
            self.in_folder.mkdir()
        shutil.rmtree(self.out_folder, ignore_errors=True)
        self.out_folder.mkdir()
        files: list[Path] = self.list_files()
        print(f"Processing {len(files):,} files.")
        for file in files:
            self.process(file)

    def process(self, file: Path) -> None:
        pragma: Pragma
        challenges: list[ChallengeResponsePair]
        queued: list[ChallengeResponsePair]

        print(f"Processing {file.name}")
        out_file: Path = self.out_folder.joinpath(file.name)
        debug_out_file: Path = out_file.with_suffix(".debug.txt")
        lyx_base_file = out_file.with_suffix(".lyx")
        pragma, challenges = self.parse_challenge_response_pairs(file)
        debug_challenges = challenges.copy()
        print(f"Loaded {len(challenges):,} challenge templates.")
        if pragma.include_reversed or pragma.only_reversed:
            tmp_list: list[ChallengeResponsePair] = list()
            for challenge in challenges:
                new_pair = challenge.copy()
                _ = new_pair.challenge
                new_pair.challenge = new_pair.response
                new_pair.response = _
                tmp_list.append(new_pair)
            if pragma.only_reversed:
                challenges.clear()
            challenges.extend(tmp_list)
        if pragma.sort:
            sort_by_len_alpha(challenges)
        if pragma.random:
            length: int = sum([len(c.challenge) * 2 + len(c.response) * 3 for c in challenges])
            rnd: Random = Random(length)
            rnd.shuffle(challenges)
        queued = self.create_with_pimsleur_timings(challenges, pragma.depth)
        # Space and punctuation fix
        for q in queued:
            q.challenge = normalize(q.challenge)
            q.response = normalize(q.response)
            q.challenge = re.sub("\\s+([.!?])", "\\1", q.challenge)
            q.response = re.sub("\\s+([.!?])", "\\1", q.response)
        if pragma.for_pictures:
            numbers: list[int] = list()
            for i in range(len(queued)):
                numbers.append(i + 1)
            rnd: Random = Random(len(challenges) + len(numbers))
            rnd.shuffle(numbers)
            for i in range(len(queued)):
                q: ChallengeResponsePair = queued[i]
                if q.response:
                    q.response += q.sep + " "
                q.response += f"[{numbers[i]}]"
        if pragma.debug:
            write_debug_response_pairs(debug_out_file, debug_challenges)
        if pragma.plain_text:
            write_challenge_response_pairs(out_file, queued)
        write_lyx_challenge_response_pairs(pragma, lyx_base_file, queued)

    def parse_challenge_response_pairs(self, file: Path) -> tuple[Pragma, list[ChallengeResponsePair]]:
        pairs: list[ChallengeResponsePair] = list()
        pragma: Pragma = Pragma()
        with file.open("r") as r:
            for line in r:
                line = line.strip()
                if not line:
                    continue
                # "#pragma: setsize=9 layout=Enumerate depth=6"
                if line.startswith("#pragma:"):
                    if "required:" in line:
                        tmp = get_value("required:", line)
                        pragma.required.update(tmp.split(";"))
                    if "forpictures" in line or "for-pictures" in line:
                        pragma.for_pictures = True
                    if "include-reversed" in line:
                        pragma.include_reversed = True
                    if "only-reversed" in line:
                        pragma.only_reversed = True
                    if "layout=" in line:
                        tmp = get_value("layout=", line)
                        pragma.layout = ResponseLayout.value_of(tmp)
                    if "sep=" in line:
                        tmp = get_value("sep=", line)
                        pragma.sep = tmp
                    if "nosort" in line or "no-sort" in line:
                        pragma.sort = False
                    if "random" in line:
                        pragma.random = True
                        pragma.sort = False
                        pragma.depth = 1
                    if "setsize=" in line:
                        tmp = get_value("setsize=", line)
                        pragma.max_set_size = int(tmp)
                    if "set-size" in line:
                        tmp = get_value("set-size=", line)
                        pragma.max_set_size = int(tmp)
                    if "depth=" in line:
                        tmp = get_value("depth=", line)
                        pragma.depth = int(tmp)
                    if "maxsets=" in line:
                        tmp = get_value("maxsets=", line)
                        pragma.max_sets = int(tmp)
                    if "max-sets=" in line:
                        tmp = get_value("max-sets=", line)
                        pragma.max_sets = int(tmp)
                    continue
                if line.startswith("#random:"):
                    tmp = line[line.index(":") + 1:]
                    field = tmp[:tmp.index("=")].strip()
                    tmp = tmp[tmp.index("=") + 1:]
                    values = tmp.split(",")
                    rset: ReplacementSet = ReplacementSet()
                    rset.field = field
                    rset.replacements = values
                    self.random_replacements[f"<{field}>"] = rset
                    continue
                if line.startswith("#"):
                    continue
                if "|" not in line and not pragma.for_pictures:
                    raise RuntimeError(f"BAD LINE (no pipes found): '{line}'")
                pair: ChallengeResponsePair = ChallengeResponsePair()
                before_tab = line[:line.index("|")]
                after_tab = line[line.index("|") + 1:]
                pair.challenge = before_tab.strip()
                pair.response = after_tab.strip()
                pairs.append(pair)
        return pragma, pairs

    def create_with_pimsleur_timings(self, challenges: list[ChallengeResponsePair], intervals: int) -> list[
        ChallengeResponsePair]:
        used_timing_slots: TimingSlots = TimingSlots()
        queued: list[ChallengeResponsePair] = list()
        pair: ChallengeResponsePair
        for pair in challenges:
            seconds_offset: int = 0
            for interval in range(0, intervals):
                new_pair: ChallengeResponsePair = pair.copy()
                seconds_start: int = int(math.pow(5, interval)) + seconds_offset
                length: int = math.ceil(float(len(new_pair.challenge)) / 5.0)
                while used_timing_slots.is_used(seconds_start, length):
                    seconds_start += 1
                used_timing_slots.mark_used(seconds_start, length)
                new_pair.position = seconds_start
                seconds_offset = seconds_start + length
                queued.append(new_pair)
        queued.sort(key=lambda q: q.position)
        max_tries = 10
        while max_tries:
            max_tries -= 1
            prev: ChallengeResponsePair | None = None
            for ix in range(len(queued)):
                a: ChallengeResponsePair = queued[ix]
                if a == prev:
                    del queued[ix]
                    queued.append(a)
                prev = a
        length: int = sum([len(c.challenge) + len(c.response) for c in queued])
        rnd: Random = Random(length)
        for new_pair in queued:
            for field in self.random_replacements.keys():
                field_alt: str = f"<={field[1:]}"
                if field not in new_pair.challenge and field not in new_pair.response and field_alt not in new_pair.challenge and field_alt not in new_pair.response:
                    continue
                rset: ReplacementSet = self.random_replacements[field]
                if not rset.replacements:
                    continue
                if not rset.deck:
                    rset.deck = rset.replacements.copy()
                    rnd.shuffle(rset.deck)
                tmp: str = rset.deck.pop(0)
                a1: str
                b2: str
                if "=" in tmp:
                    a1 = tmp[:tmp.index("=")].strip()
                    b1 = tmp[tmp.index("=") + 1:].strip()
                else:
                    a1 = tmp.strip()
                    b1 = ""
                new_pair.challenge = new_pair.challenge.replace(field, a1)
                new_pair.challenge = new_pair.challenge.replace(field_alt, b1)
                new_pair.response = new_pair.response.replace(field, a1)
                new_pair.response = new_pair.response.replace(field_alt, b1)
        prev: ChallengeResponsePair | None = None
        for ix in range(len(queued) - 1, -1, -1):
            if queued[ix] == prev:
                del queued[ix]
                continue
            prev = queued[ix]
        return queued


def main() -> None:
    g: Generator = Generator()
    g.run()


if __name__ == '__main__':
    main()
