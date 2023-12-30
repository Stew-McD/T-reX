import WasteAndMaterialFootprint as wmf
import bw2data as bd

PROJECT_NAME = "WMFootprint-SSP-cutoff"
bd.projects.set_current(PROJECT_NAME)


for db in bd.databases:
    e = wmf.VerifyDatabase(project_name=PROJECT_NAME, database_name=db)
    print(e)
print("\nDone!")