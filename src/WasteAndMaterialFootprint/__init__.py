# src/T-reX/__init__.py


__version__ = "0.1.21"
__author__ = "Stewart Charles McDowall | Stew-McD"


#! Some work should be done here to decide what to make available in the various namespaces

from . import config

# Import modules here
from .main import run
from .CustomConfig import config_setup, config_reload, config_reset
from .ExchangeEditor import ExchangeEditor
from .ExplodeDatabase import ExplodeDatabase
from .FutureScenarios import MakeFutureScenarios
from .MakeCustomDatabase import dbWriteExcel, dbExcel2BW
from .MethodEditor import AddMethods, DeleteMethods, CheckMethods
from .SearchMaterial import SearchMaterial
from .SearchWaste import SearchWaste
from .VerifyDatabase import VerifyDatabase


__all__ = [
    "config",
    "config_setup",
    "config_reload",
    "config_reset",
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
