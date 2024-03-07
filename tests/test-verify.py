import T-reX as T_reX
import bw2data as bd

PROJECT_NAME = "T_reX-SSP-cutoff"
bd.projects.set_current(PROJECT_NAME)


for db in bd.databases:
    e = T_reX.VerifyDatabase(project_name=PROJECT_NAME, database_name=db)
    print(e)
print("\nDone!")