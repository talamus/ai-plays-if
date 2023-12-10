import logging
from typing import Any
import pexpect
import importlib.resources


class Story:
    """Run a Z-Machine format Interactive Fiction story using the MojoZork™
    :ivar titlecard: Title and copyright information.
    :ivar history: List of outputs and commands.
    :ivar output: Latest output of a command.
    """

    @staticmethod
    def _canonize_newlines(text: str) -> str:
        """Force Unix style newlines."""
        return text.replace("\r\n", "\n")

    def __init__(self, cfg: dict[str, Any]) -> None:
        """Start running a story from a file.
        :param cfg: Configuration:
            `story_file`: The Z-Machine data file to be executed.
        """

        if "story_file" not in cfg:
            raise FileNotFoundError(f"No story.dat provided. Run with --help for help.")

        log = logging.getLogger(__name__)
        mojozork_path = str(importlib.resources.files(__package__) / "bin" / "mojozork")
        log.debug(
            "Starting MojoZork",
            extra={"mojozork_path": mojozork_path, "story_file": cfg["story_file"]},
        )

        self.child = pexpect.spawn(
            mojozork_path,
            args=[cfg["story_file"]],
            encoding="windows-1252",
        )

        self.child.expect(">")
        log.debug("MojoZork output before prompt", extra={"before": self.child.before})
        intro = Story._canonize_newlines(self.child.before).strip().split("\n\n")

        self.title_card = intro.pop(0)

        self.output = "\n\n".join(intro)
        self.history = [{"output": self.output}]

    def do(self, command: str) -> str:
        """Do a thing in the story.
        :param command: The thing to do.
        :returns: Result of the command.
        """
        log = logging.getLogger(__name__)

        command = command.strip()
        log.info("Command", extra={"text": command})
        self.child.sendline(command)
        self.history.append({"command": command})

        self.child.expect(">")
        self.output = (
            Story._canonize_newlines(self.child.before)
            .strip()
            .removeprefix(f"{command}\n")
        )
        log.info("Output", extra={"text": self.output})
        self.history.append({"output": self.output})

        return self.output
