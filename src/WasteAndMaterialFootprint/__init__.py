# src/WasteAndMaterialFootprint/__init__.py

## THIS IS NOT CLEAN AT ALL, BUT IT CAN WORK FOR NOW

# Import modules here
from .main import *
from .ExchangeEditor import *
from .ExplodeDatabase import *
from .FutureScenarios import *
from .MakeCustomDatabase import *
from .MethodEditor import *
from .SearchMaterial import *
from .SearchWaste import *
from .VerifyDatabase import *

# Optionally, you can define an __all__ list to explicitly specify what to import
# when using from WasteAndMaterialFootprint import *

all__ = [
    "ExchangeEditor",
    "ExplodeDatabase",
    "FutureScenarios",
    "main",
    "MakeCustomDatabase",
    "MethodEditor",
    "SearchMaterial",
    "SearchWaste",
    "VerifyDatabase"
]