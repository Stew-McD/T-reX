'''
|===============================================================|
| File: VerifyDatabase.py                                       |
| Project: WasteAndMaterialFootprint                            |
| Repository: www.github.com/Stew-McD/WasteAndMaterialFootprint |
| Description: <<description>>                                  |
|---------------------------------------------------------------|
| File Created: Friday, 6th October 2023 8:31:42 pm             |
| Author: Stewart Charles McDowall                              |
| Email: s.c.mcdowall@cml.leidenuniv.nl                         |
| Github: Stew-McD                                              |
| Company: CML, Leiden University                               |
|---------------------------------------------------------------|
| Last Modified: Friday, 6th October 2023 8:31:52 pm            |
| Modified By: Stewart Charles McDowall                         |
| Email: s.c.mcdowall@cml.leidenuniv.nl                         |
|---------------------------------------------------------------|
|License: The Unlicense                                         |
|===============================================================|
'''

import bw2data as bd
import bw2calc as bc
from random import choice

def VerifyDatabase(project_wmf,  db_name):
    
    bd.projects.set_current(project_wmf)
    bd.Database(db_name)
    
    print(f"\n* Verifying database {db_name} in project {project_wmf}")
    
    wmf_score = 0
    
    while wmf_score == 0:
        try:
            act = bd.Database(db_name).random()
            methods_waste = [x for x in bd.methods if 'Waste Footprint' in x[0]]
            methods_material = [x for x in bd.methods if 'Material Demand Footprint' in x[0]]

            methods = methods_waste + methods_material
            method = choice(methods)

            print(f"\n* Verifying activity {act['name']}")

            lca = bc.LCA({act: 1}, method)
            lca.lci()
            lca.lcia()

            wmf_score = lca.score
            print(f"\n* {act} : {method} : {wmf_score}")
        except Exception as e:
            print(f"Error occurred: {e}")
            break
        
        
        
    

