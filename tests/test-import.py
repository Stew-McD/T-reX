# import custom modules (from root dir)
import sys

sys.path.insert(0, "../src/WasteAndMaterialFootprint")

from ExchangeEditor import ExchangeEditor
from ExplodeDatabase import ExplodeDatabase
from FutureScenarios import MakeFutureScenarios
from MakeCustomDatabase import dbExcel2BW, dbWriteExcel
from MethodEditor import AddMethods
from SearchMaterial import SearchMaterial
from SearchWaste import SearchWaste
from VerifyDatabase import VerifyDatabase

# import configuration from config/user_settings.py
from config.user_settings import (
    custom_bw2_dir,
    db_wmf_name,
    delete_wmf_project,
    dir_logs,
    dir_tmp,
    dir_config,
    generate_args_list,
    project_base,
    project_premise,
    project_wmf,
    use_multiprocessing,
    use_premise,
    use_wmf,
    do_search,
    do_methods,
    do_edit,
    single_database,
)