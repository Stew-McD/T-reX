from pathlib import Path
import shutil
import sys
import importlib

from . import CUSTOM_CONFIG_DIR


def config_setup():
    """Copies the config files to the current working directory and adds the config directory to sys.path
    args: None
    returns: None
    """
    # Path to the config directory in the package
    package_root = Path(__file__).resolve().parents[2]
    source_config_dir = package_root / "config"

    # Path to the target config directory in the CWD
    target_config_dir = CUSTOM_CONFIG_DIR

    # Copy the config files if they don't exist in CWD
    if not target_config_dir.exists():
        shutil.copytree(source_config_dir, target_config_dir)
        print(f"Configuration files copied to {target_config_dir}")
    else:
        print(f"Configuration files already exist in {target_config_dir}")

    # Add the config directory to sys.path to enable imports
    if str(target_config_dir) not in sys.path:
        sys.path.append(str(target_config_dir))
        print(f"Configuration directory added to Python path: {target_config_dir}")

    print(
        "\nNow you can edit the configuration files in the config directory for you project"
    )
    print(
        "You will have to reload the user_settings module to use the new settings, or restart your session"
    )


def config_reload():
    """Reloads the user_settings module.
    args: None
    returns: None

    """
    print("Reloading user_settings module...")
    wmf.user_settings.dir_config = CUSTOM_CONFIG_DIR
