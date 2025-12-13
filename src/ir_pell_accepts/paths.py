from pathlib import Path

def null_function() -> None:
    """
    The python code in this file tells python where to find the config file.

        This does not need to be modified if you follow the default 
        pipeline folder structure. Namely, that the config file
        is found at <project>-<name>/configs/config.yaml
    """
    return None

# This file lives at: <project>-<name>/src/<project>_<name>/paths.py
# __file__ is ALWAYS defined in modules as the directory of the module which is 
#       <project>-<name>/src/<project>_<name>

# Go to <project>-<name> dir which is 2 levels up.
PACKAGE_ROOT = Path(__file__).resolve().parents[2] 

# set the config path
CONFIG_PATH = PACKAGE_ROOT / "configs" / "config.yaml"
