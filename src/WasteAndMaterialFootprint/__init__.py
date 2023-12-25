# # src/WasteAndMaterialFootprint/__init__.py
# from pathlib import Path
# import sys

# # Add the config directory to sys.path to enable imports
# package_root = Path(__file__).resolve().parents[1]
# target_config_dir = package_root / "config"
# if str(target_config_dir) not in sys.path:
#     sys.path.append(str(target_config_dir))

from pathlib import Path
import sys

CUSTOM_CONFIG_DIR = Path.cwd() / "config"
DEFAULT_CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"

CUSTOM_DATA_DIR = Path.cwd() / "data"
DEFAULT_DATA_DIR = Path(__file__).resolve().parents[2] / "data"

CUSTOM_LOG_DIR = CUSTOM_DATA_DIR / "logs"
DEFAULT_LOG_DIR = DEFAULT_DATA_DIR / "logs"


if CUSTOM_CONFIG_DIR.is_dir():
    sys.path.append(str(CUSTOM_CONFIG_DIR))
    print(f"\n* Using custom config directory: \n{CUSTOM_CONFIG_DIR}.\n")
else:
    print(
        f"\n* Custom config directory: {CUSTOM_CONFIG_DIR} not found.\n* One will be created"
    )
    package_root = Path(__file__).resolve().parents[2]
    target_config_dir = package_root / "config"
    sys.path.append(str(target_config_dir))

from .CustomConfig import config_setup, config_reload
config_setup()

if CUSTOM_DATA_DIR.is_dir():
    print(f"\n* Using data directory: \n{CUSTOM_DATA_DIR}.\n")


# Import user settings
import user_settings
import queries_waste
import queries_materials

__version__ = "0.1.1"
__author__ = "Stewart Charles McDowall | Stew-McD"

# Import modules here
from .main import run
from .ExchangeEditor import ExchangeEditor
from .ExplodeDatabase import ExplodeDatabase
from .FutureScenarios import FutureScenarios
from .MakeCustomDatabase import dbWriteExcel, dbExcel2BW
from .MethodEditor import AddMethods, DeleteMethods, CheckMethods
from .SearchMaterial import SearchMaterial
from .SearchWaste import SearchWaste
from .VerifyDatabase import VerifyDatabase


__all__ = [
    "user_settings",
    "queries_waste",
    "queries_materials",
    "config_setup",
    "config_reload",
    "run",
    "FutureScenarios",
    "ExplodeDatabase",
    "SearchWaste",
    "SearchMaterial",
    "dbWriteExcel",
    "dbExcel2BW",
    "AddMethods",
    "DeleteMethods",
    "CheckMethods",
    "ExchangeEditor",
    "VerifyDatabase",
]
