import os
import sys

if "--accept-eula" in sys.argv:
    CONFIG = {
        "nt": os.path.expanduser("~\\AppData\\Local\\discord-sender"),
        "other": os.path.expanduser("~/.config/discord-sender"),
    }
    cfg = CONFIG["nt"] if os.name == "nt" else CONFIG["other"]
    with open(os.path.join(cfg, ".eulaaccepted"), "a") as f:
        pass
    os.chmod(os.path.join(cfg, ".eulaaccepted"), 0o777)
    print("The eula was successfully accepted")
    sys.exit(0)
print(
    "usage: python -m discord_sender --accept-eula\nOnly use this if the import hook fails."
)
