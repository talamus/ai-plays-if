import logging
from .story import Story
from .ai import AI
from .default_config import DEFAULT_CONFIG


def start_playing(cfg: dict = None) -> None:
    if cfg is None:
        cfg = dict(DEFAULT_CONFIG)

    log = logging.getLogger(__name__)
    log.debug("Configuration", extra={"cfg": cfg})

    # Start AI
    ai = AI(cfg)

    # Load Z-Machine and start the story
    story = Story(cfg)
    log.info("Title", extra={"text": story.title_card})
    log.info("Output", extra={"text": story.output})

    for command in cfg["story_commands"]:
        story.do(command)

    while True:
        try:
            story.do(ai.think(story))
        except KeyboardInterrupt:
            break

    log.debug("History", extra={"history": story.history})
