from typing import Union

from .cells import cell_len, set_cell_size
from .console import Console, ConsoleOptions, RenderResult
from .jupyter import JupyterMixin
from .style import Style
from .text import Text


class Rule(JupyterMixin):
    """A console renderable to draw a horizontal rule (line).

    Args:
        title (Union[str, Text], optional): Text to render in the rule. Defaults to "".
        characters (str, optional): Character(s) used to draw the line. Defaults to "─".
        style (StyleType, optional): Style of Rule. Defaults to "rule.line".
        end (str, optional): Character at end of Rule. defaults to "\\n"
        align (str, optional):
    """

    def __init__(
        self,
        title: Union[str, Text] = "",
        *,
        characters: str = "─",
        style: Union[str, Style] = "rule.line",
        end: str = "\n",
        align: str = "center",
    ) -> None:
        if cell_len(characters) < 1:
            raise ValueError(
                "'characters' argument must have a cell width of at least 1"
            )
        if align not in ("left", "center", "right"):
            raise ValueError(
                f'invalid value for align, expected "left", "center", "right" (not {align!r})'
            )
        self.title = title
        self.characters = characters
        self.style = style
        self.end = end
        self.align = align

    def __repr__(self) -> str:
        return f"Rule({self.title!r}, {self.characters!r})"

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        width = options.max_width

        # Python3.6 doesn't have an isascii method on str
        isascii = getattr(str, "isascii", None) or (
            lambda s: all(ord(c) < 128 for c in s)
        )
        characters = (
            "-"
            if (options.ascii_only and not isascii(self.characters))
            else self.characters
        )

        chars_len = cell_len(characters)
        if not self.title:
            rule_text = Text(characters * ((width // chars_len) + 1), self.style)
            rule_text.truncate(width)
            rule_text.plain = set_cell_size(rule_text.plain, width)
            yield rule_text
            return

        if isinstance(self.title, Text):
            title_text = self.title
        else:
            title_text = console.render_str(self.title, style="rule.text")

        if cell_len(title_text.plain) > width - 4:
            title_text.truncate(width - 4, overflow="ellipsis")

        title_text.plain = title_text.plain.replace("\n", " ")
        title_text.expand_tabs()
        rule_text = Text(end=self.end)

        if self.align == "center":
            side_width = (width - cell_len(title_text.plain)) // 2
            left = Text(characters * (side_width // chars_len + 1))
            left.truncate(side_width - 1)
            right_length = width - cell_len(left.plain) - cell_len(title_text.plain)
            right = Text(characters * (side_width // chars_len + 1))
            right.truncate(right_length)
            rule_text.append(left.plain + " ", self.style)
            rule_text.append(title_text)
            rule_text.append(" " + right.plain, self.style)
        elif self.align == "left":
            rule_text.append(title_text)
            rule_text.append(" ")
            rule_text.append(characters * (width - rule_text.cell_len), self.style)
        elif self.align == "right":
            rule_text.append(characters * (width - title_text.cell_len - 1), self.style)
            rule_text.append(" ")
            rule_text.append(title_text)

        rule_text.plain = set_cell_size(rule_text.plain, width)
        yield rule_text


if __name__ == "__main__":  # pragma: no cover
    from rich.console import Console
    import sys

    try:
        text = sys.argv[1]
    except IndexError:
        text = "Hello, World"
    console = Console()
    console.print(Rule(title=text))
