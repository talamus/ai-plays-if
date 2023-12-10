import sys
import textwrap
import argparse
import yaml
from pathlib import Path

from .cli import main, VERBOSITY
from . import DEFAULT_CONFIG, start_playing

# -----------------------------------------------------------------------------

APP_NAME = "ai_plays_if"
APP_DESCRIPTION = f"AI plays Interactive Fiction — A duet for two smart machines"
APP_CONFIG = {
    "config_file": str(Path(__file__).parent.parent / f"{APP_NAME}.config"),
    "verbosity": "INFO",
    "log_file": str(Path(__file__).parent.parent / "logs" / f"{APP_NAME}.log"),
    "log_file_format": "%(asctime)s %(levelname)s %(name)s %(message)s",
    "log_level": "INFO",
    "log_max_bytes": 100 * 1024,
    "log_max_files": 10,
}
cfg = DEFAULT_CONFIG | APP_CONFIG
APP_USAGE = f"""
Here will be an example...

Default configuration:
{textwrap.indent(yaml.dump(cfg, sort_keys=False), "  ")}
"""

# -----------------------------------------------------------------------------

argparser = argparse.ArgumentParser(
    prog=f"python -m {APP_NAME}",
    description=APP_DESCRIPTION,
    epilog=APP_USAGE,
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
argparser.add_argument(
    "story_file",
    metavar="story.dat",
    help="story that our AI will try to play",
)
argparser.add_argument(
    "-v",
    "--verbosity",
    action="count",
    default=0,
    help="Be more verbose",
)
argparser.add_argument(
    "-q",
    "--quiet",
    dest="verbosity",
    action="store_const",
    const=-1,
    help="Do not output anything",
)
argparser.add_argument(
    "--config",
    dest="alterative_config_file",
    metavar="CONFIG",
    help="read configuration from this file (YAML format)",
)
argparser.add_argument(
    "--loglevel",
    dest="log_level",
    metavar="LEVEL",
    choices=VERBOSITY.keys(),
    help=f"set logging level ({ ', '.join(list(VERBOSITY.keys())) })",
)

args = vars(argparser.parse_args())

# Be more verbose by default
args["verbosity"] = args["verbosity"] + 2

# Remove arguments that are not set
if not args["log_level"]:
    del args["log_level"]

sys.exit(main(start_playing, args, cfg, APP_DESCRIPTION))
