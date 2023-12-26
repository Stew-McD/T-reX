# src/WasteAndMaterialFootprint/__init__.py

# Import user settings
from .CustomConfig import config_setup, config_reload

config_setup()

from config import user_settings
from config import queries_waste
from config import queries_materials

__version__ = "0.1.2"
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
