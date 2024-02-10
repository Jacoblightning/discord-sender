import os

import pymsgbox

CONFIG = {
    "nt": os.path.expanduser("~\\AppData\\Local\\discord-sender"),
    "other": os.path.expanduser("~/.config/discord-sender"),
}
cfg = CONFIG["nt"] if os.name == "nt" else CONFIG["other"]
if not os.path.exists(os.path.join(cfg, ".eulaaccepted")):
    if not os.path.exists(cfg):
        os.mkdir(cfg)
    if (
        pymsgbox.confirm(
            "This program breaks Discords TOS.\nPress yes to aknowledge all responsibility\nThis will be the only "
            "time this is asked.",
            buttons=["Yes, I accept", "No"],
        )
        == "No"
    ):
        exit(0)
    with open(os.path.join(cfg, ".eulaaccepted"), "a") as f:
        pass
    from . import discord
