import dataclasses

from ResponseLayout import ResponseLayout


def normalize(text: str) -> str:
    return " ".join(text.split())


@dataclasses.dataclass
class ChallengeResponsePair:
    position: int = 0
    challenge: str|None = None
    response: str|None = None
    sep: str = ","

    def __str__(self) -> str:
        tmp_challenge: str = self.challenge if self.challenge else ""
        tmp_response: str = self.response if self.response else ""

        _: str = tmp_challenge
        _ += "\t"
        _ += tmp_response
        _ += "\t"
        _ += tmp_challenge
        _ += self.sep
        _ += " "
        _ += tmp_response
        _ += "\t"
        _ += str(self.position)
        return _

    def lyx(self, layout: ResponseLayout) -> str:
        _ = ""
        tmp_challenge: str = self.challenge.strip() if self.challenge else ""
        tmp_response: str = self.response.strip() if self.response else ""

        _ += "\\begin_layout Enumerate\n"
        _ += normalize(tmp_challenge)

        if layout == ResponseLayout.SINGLE_LINE:
            _ += "\n"
            _ += self.sep
            _ += "\n"
            _ += tmp_response
            _ += "\n\\end_layout\n\n"
        elif layout == ResponseLayout.ENUMERATE:
            _ += "\n\\end_layout\n\n"
            _ += "\\begin_deeper\n"
            for t in tmp_response.split("\t"):
                _ += "\\begin_layout Enumerate\n"
                _ += normalize(t)
                _ += "\n\\end_layout\n\n"
            _ += "\\end_deeper\n"
        elif layout == ResponseLayout.ITEMIZE:
            _ += "\n\\end_layout\n\n"
            _ += "\\begin_deeper\n"
            for t in tmp_response.split("\t"):
                _ += "\\begin_layout Itemize\n"
                _ += normalize(t)
                _ += "\n\\end_layout\n\n"
            _ += "\\end_deeper\n"
        elif layout == ResponseLayout.NONE:
            _ += "\n\\end_layout\n\n"
        elif layout == ResponseLayout.PLAIN:
            _ += "\n\\end_layout\n\n"
            _ += "\\begin_deeper\n"
            _ += "\\begin_layout Standard\n"
            _ += normalize(tmp_response)
            _ += "\n\\end_layout\n\n"
            _ += "\\end_deeper\n"
        else:
            raise RuntimeError(f"Unhandled layout: {str(layout)}")

        return _

    def copy(self) -> "ChallengeResponsePair":
        dupe: ChallengeResponsePair = ChallengeResponsePair()

        dupe.challenge = self.challenge
        dupe.response = self.response
        dupe.sep = self.sep
        dupe.position = self.position

        return dupe


