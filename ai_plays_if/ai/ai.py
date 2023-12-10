import re
import logging
import random
from typing import Any
import torch
import transformers
from ..story import Story


class AI:
    def __init__(self, cfg: dict[str, Any]) -> None:
        """Launch conversational AI pipeline with history."""
        log = logging.getLogger(__name__)

        device = (
            torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        )

        log.info("Starting AI", extra={"device": str(device), "model": cfg["ai_model"]})

        self.tokenizer = transformers.AutoTokenizer.from_pretrained(cfg["ai_model"])
        self.pipeline = transformers.pipeline(
            "text-generation",
            model=cfg["ai_model"],
            torch_dtype=torch.float16,
            device=device,
        )
        self.prompt = cfg["ai_prompt"]
        self.separator = "\n\nWhat do you do next?\n"

    def think(self, story: Story) -> str:
        log = logging.getLogger(__name__)

        the_story_so_far = self.prompt
        for entry in story.history:
            if "command" in entry:
                the_story_so_far += "\n\nYou: " + entry["command"]
            else:
                the_story_so_far += "\n\n" + entry["output"]
        the_story_so_far += self.separator

        log.debug("The story so far:\n%s", the_story_so_far)

        sequences = self.pipeline(
            the_story_so_far,
            do_sample=True,
            top_k=10,
            num_return_sequences=1,
            eos_token_id=self.tokenizer.eos_token_id,
            max_new_tokens=200,
        )
        log.debug("Sequences", extra={"sequences": sequences})
        result = "".join(map(lambda x: x["generated_text"], sequences))
        commands = result.split(self.separator)[1].strip().replace("\n\n", "\n")

        choices = []
        for line in commands.split("\n"):
            if not line.endswith(":") and re.search(r"\w+", line):

                match = re.search(r"^You: ", line)
                if match:
                    line = line.removeprefix(match[0])

                match = re.search(r"^\s*\w\)\s+", line)
                if match:
                    line = line.removeprefix(match[0])

                match = re.search(r"^\s*-\s+", line)
                if match:
                    line = line.removeprefix(match[0])

                choices.append(line)

        return random.choice(choices)
