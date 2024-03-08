import T_reX_LCA as TreX
import bw2data as bd

PROJECT_NAME = "T-reX-SSP-cutoff"
bd.projects.set_current(PROJECT_NAME)


for db in bd.databases:
    e = TreX.VerifyDatabase(project_name=PROJECT_NAME, database_name=db)
    print(e)
print("\nDone!")