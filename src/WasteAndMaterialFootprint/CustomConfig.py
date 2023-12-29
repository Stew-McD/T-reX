from pathlib import Path
import shutil


def config_setup():
    """Copies the config files to the current working directory and adds the config directory to sys.path
    args: None
    returns: None
    """
    # Path to the config directory in the package
    # package_root = Path(__file__).resolve().parents[0]
    src = Path(__file__).resolve().parents[0]
    source_config_dir = src / "config"

    # Path to the target config directory in the CWD
    target_config_dir = Path.cwd() / "config"

    # Copy the config files if they don't exist in CWD
    if not target_config_dir.exists():
        shutil.copytree(source_config_dir, target_config_dir)
        print(f"Configuration files copied to {target_config_dir}")
        
    else:
        print(f"Configuration files already exist in {target_config_dir}")

    # # Add the config directory to sys.path to enable imports
    # if str(target_config_dir) not in sys.path:
    #     sys.path.insert(0, str(Path.cwd()))
    #     print(f"Configuration directory added to Python path: {target_config_dir}")


def config_reload():
    """Copies the config files back to the package directory. The user will need to restart the python session to reload the WasteAndMaterialFootprint module with the updated configuration files

    args: None
    returns: None

    """

    src = Path(__file__).resolve().parents[0]

    # Path to the config directory in the package
    target_config_dir = src / "config"

    # Path to the target config directory in the CWD
    source_config_dir = Path.cwd() / "config"
    print(f"source_config_dir: {source_config_dir}")
    print(f"target_config_dir: {target_config_dir}")
    if source_config_dir == target_config_dir:
        print("Local and package config directories are the same")
        return
    
    # Copy the edited config files back to the package directory
    if target_config_dir.exists():
        shutil.copytree(source_config_dir, target_config_dir, dirs_exist_ok=True)
        print(f"Updated configuration files copied from {source_config_dir} to {target_config_dir}")

    # Reload the WasteAndMaterialFootprint module

    print(
        f"\n {80*'*'} \n\tRestart the python session to reload the WasteAndMaterialFootprint module\n\twith the updated configuration files\n{80*'*'}\n"
    )


def config_reset():
    '''
    Reset config to defaults that are stored in the root directory of the package
    
    args: None
    returns: None
    '''
    
    print("Resetting configuration files to defaults")
    
    backup_dir = Path(__file__).resolve().parents[1] / "config_backup"
    
    config_dir = Path.cwd() / "config"

    shutil.copytree(backup_dir, config_dir, dirs_exist_ok=True)
        
    print(
        f"\n {80*'*'} \n\tRestart the python session to reload the WasteAndMaterialFootprint module\n\twith the updated configuration files\n{80*'*'}\n"
    )