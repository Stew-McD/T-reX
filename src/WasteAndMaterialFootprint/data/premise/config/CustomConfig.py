from pathlib import Path
import shutil
import sys
import importlib


def config_setup():
    """Copies the config files to the current working directory and adds the config directory to sys.path
    args: None
    returns: None
    """
    # Path to the config directory in the package
    # package_root = Path(__file__).resolve().parents[0]
    src = Path(__file__).resolve().parents[1]
    source_config_dir = src / "config"

    # Path to the target config directory in the CWD
    target_config_dir = Path.cwd() / "config"

    # Copy the config files if they don't exist in CWD
    if not target_config_dir.exists():
        shutil.copytree(source_config_dir, target_config_dir)
        print(f"Configuration files copied to {target_config_dir}")

    # Add the config directory to sys.path to enable imports
    if str(target_config_dir) not in sys.path:
        sys.path.insert(0, str(Path.cwd()))
        print(f"Configuration directory added to Python path: {target_config_dir}")

def config_reload():
    """Reloads the user_settings module.
    args: None
    returns: None

    """
    wmf.user_settings.dir_config = Path.cwd() / "config"
