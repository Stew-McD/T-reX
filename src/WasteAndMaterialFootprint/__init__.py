# src/WasteAndMaterialFootprint/__init__.py

import os
from pathlib import Path
import sys

# maybe this is not ideal, but it is working for now
CUSTOM_CONFIG_DIR = Path.cwd() / "config"
CUSTOM_DATA_DIR = Path.cwd() / "data"

if CUSTOM_CONFIG_DIR.is_dir():
    sys.path.append(str(CUSTOM_CONFIG_DIR))
    print(f"\n* Using config directory: \n{CUSTOM_CONFIG_DIR}.\n")
else:
    print(
        f"\n* Custom config directory: {CUSTOM_CONFIG_DIR} not found.\n* One will be created"
    )
    package_root = Path(__file__).resolve().parents[2]
    target_config_dir = package_root / "config"
    sys.path.append(str(target_config_dir))

from .CustomConfig import config_setup, config_reload

# this will create the config directory in the cwd if it does not exist
# config_setup()

if CUSTOM_DATA_DIR.is_dir():
    print(f"\n* Using data directory: \n{CUSTOM_DATA_DIR}.\n")

# Import user settings
import user_settings
import queries_waste
import queries_materials

__version__ = "0.1.11"
__author__ = "Stewart Charles McDowall | Stew-McD"


#! Some work should be done here to decide what to make available in the various namespaces

# Import modules here
from .main import run
from .ExchangeEditor import ExchangeEditor
from .ExplodeDatabase import ExplodeDatabase
from .FutureScenarios import MakeFutureScenarios
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
    "MakeFutureScenarios",
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
