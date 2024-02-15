import os

import pymsgbox
import requests
import sys

if "--accept-eula" not in sys.argv:
    def _term_warning():
        if (
                not input(
                    "This program breaks Discords TOS.\nPress yes to aknowledge all responsibility\nThis will be the "
                    "only time this is asked. [N/y]"
                )
                        .lower()
                        .startswith("y")
        ):
            exit(0)
        _eula_accepted()


    def _eula_accepted():
        with open(os.path.join(cfg, ".eulaaccepted"), "a") as f:
            pass


    CONFIG = {
        "nt": os.path.expanduser("~\\AppData\\Local\\discord-sender"),
        "other": os.path.expanduser("~/.config/discord-sender"),
    }
    cfg = CONFIG["nt"] if os.name == "nt" else CONFIG["other"]
    if not os.path.exists(os.path.join(cfg, ".eulaaccepted")):
        if not os.path.exists(cfg):
            os.mkdir(cfg)
        try:
            _term_warning()
        except Exception:
            print(
                "You cannot use this program until you have accepted the eula but there was an error writing the "
                'config file.\n To continue, please run "python -m discord_sender --accept-eula" as '
                "administrator/root"
            )
            exit(1)
