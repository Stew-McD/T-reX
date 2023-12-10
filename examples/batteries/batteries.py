import bw2data as bd
import pandas as pd
import bw2calc as bc
from tqdm import tqdm
from pathlib import Path
import os
import ast
import contextlib
import bw2analyzer as bwa

ca = bwa.ContributionAnalysis()

PROJECT = "WMFootprint-SSP-base_cutoff"
KEY = "market for battery, Li-ion, rechargeable"

KEYWORDS_METHODS = [
    'ReCiPe 2016 v1.03, midpoint (I)',
    'EF v3.0 no LT',
    'EDIP 2003 no LT',
    'Crustal Scarcity',
    'Waste Footprint',
    'Material Demand Footprint'
]

SEARCH_ACTIVITIES = 1
SEARCH_METHODS = 1
GET_RESULTS = 1
GET_SUPPLY_CHAIN_RESULTS = 1

CWD = Path.cwd()
DIR_DATA = CWD / 'data'
os.makedirs(DIR_DATA, exist_ok=True)

FILE_ACTIVITIES = DIR_DATA / 'activities.csv'
FILE_METHODS = DIR_DATA / 'methods.csv'
FILE_RESULTS = DIR_DATA / 'results.csv'
FILE_SUPPLYCHAINRESULTS = DIR_DATA / 'supply_chain_results.csv'

bd.projects.set_current(PROJECT)

print(f'\n\n{"="*80}\n')
print(f'\t\t\t LCA calculations with Brightway ')
print(f'\n{"="*80}\n')

print(f'Project: \n\t{PROJECT} (containing {len(bd.databases)} databases)\n')
print(f'Activity search phrase:\n\t{KEY}\n')
print(f'Method keywords: ', end='\n\t')
print(*KEYWORDS_METHODS, sep='\n\t', end='\n')
print(f'\n{"-"*80}\n')


def parse_db_name(db_name):
    if db_name == 'ecoinvent-3.9.1-cutoff':
        db_name = 'ecoinvent_cutoff_3.9_none_none0-none_2020'
    if db_name == 'ecoinvent-3.9.1-consequential':
        db_name = 'ecoinvent_consequential_3.9_none_none0-none_2020'
    
    parts = db_name.split('_')
    db_base = parts[0]
    db_system = parts[1]
    db_version = float(parts[2]) 
    db_model = parts[3]
    db_ssp = int(parts[4].split('-')[0][-1])
    db_target = parts[4].split('-')[1]
    db_year = int(parts[5])
    
    return pd.Series({
        'db_base': db_base,
        'db_system': db_system,
        'db_version': db_version,
        'db_model': db_model,
        'db_ssp': db_ssp,
        'db_target': db_target,
        'db_year': db_year,
    })

def search_activities(KEY):
    
    print("\t== Searching for activities ==")
    
    acts = []
    for db in bd.databases:
        db = bd.Database(db)
        results = db.search(KEY)
        acts += results
        
    acts = [x.as_dict() for x in acts]

    df = pd.DataFrame(acts)
    df = df[['name', 'database', 'code']]
    df = df.join(df['database'].apply(parse_db_name))
    df['key'] = list(zip(df['database'], df['code']))

    col_order = [
       'name',
       'db_base',
       'db_system',
       'db_version',
       'db_model',
       'db_ssp', 
       'db_target', 
       'db_year', 
       'database',
       'code',
       'key',
       ]

    df.to_csv(FILE_ACTIVITIES, index=False, sep=';')
    
    print(f'\t\t{len(df)} activities found and saved to "{FILE_ACTIVITIES}"')
    print(f'\n{"-"*80}\n')
    
    return None

def search_methods(KEYWORDS_METHODS):
    
    print("\t== Searching for methods ==")
    
    KEYWORDS_METHODS = [
        'ReCiPe 2016 v1.03, midpoint (I)',
        'EF v3.0 no LT',
        'EDIP 2003 no LT',
        'Crustal Scarcity',
        'Waste Footprint',
        'Material Demand Footprint'
    ]
    
    methods = [x for x in bd.methods if any(y in x for y in KEYWORDS_METHODS)]

    df_methods = pd.DataFrame(methods)
    df_methods['tuple'] = df_methods.apply(tuple, axis=1)
    df_methods.to_csv(FILE_METHODS, index=False, sep=';')
    print(f'\t\t{len(df_methods)} methods found and saved to "{FILE_METHODS}"')
    print(f'\n{"-"*80}\n')
    
    return None

def limit_string_length(string, max_length=20):
    if len(string) > max_length:
        return string[:max_length]
    else:
        return string

def get_results():
    """Get results for a list of activities and methods"""
    
    activities = pd.read_csv(FILE_ACTIVITIES, sep=';')
    # activity objects are not serializable, so we need to re-create them
    activities["activity_object"] = activities.key.apply(lambda x: bd.get_activity(ast.literal_eval(x)))


    methods = pd.read_csv(FILE_METHODS, sep=';')
    methods = methods['tuple'].apply(ast.literal_eval).to_list()
    
    total_calculations = len(activities) * len(methods)
    width_activity = 20
    width_method = 30
    width_score = 10
    width_unit = 15
    width_db = 15
    width_bar = 150
    
    print(f'\n{"-"*80}\n')
    print(f'\t== Calculating {total_calculations} LCIAs --- {len(activities)} activities and {len(methods)} methods ==')
    print(f'\n\n{"-"*80}\n')
    
    progress_format = "{l_bar} {bar} | {n_fmt}/{total_fmt} | {elapsed}<{remaining}"
    
    progress = tqdm(total=total_calculations, 
                    colour='magenta',
                    ncols=150,
                    bar_format=progress_format)
    
    results = []
    dbs = activities.database.unique()
    
    for i, db_name in enumerate(dbs):
        db = bd.Database(db_name)
        df = activities[activities.database == db_name].reset_index(drop=True)
                
        # initialize the LCA object
        act = df.loc[0, 'activity_object']
        lca = bc.LCA({act: 1}, methods[0])
        lca.lci()
        lca.lcia()
        
        # iterate through the activities
        for ii, row in df.iterrows():
            act = db.get(row.code)
            lca.redo_lci({act: 1})
            
            act_dict = act.as_dict()
            act_name = act_dict['name']
            act_code = act_dict['code']
            
            for iii, method in enumerate(methods, start=1):
                lca.switch_method(method)
                lca.redo_lcia()
                
                top = ca.annotated_top_processes(lca, limit=10)
                
                results_dict = {
                    'name': act_name,
                    'db_ssp': row["db_ssp"],
                    'db_target': row["db_target"],
                    'db_year': row["db_year"],
                    'score': lca.score,
                    'unit': bd.methods[lca.method]['unit'],
                    'method_2': method[2],
                    'method_1': method[1],
                    'method_0': method[0],
                    'top_processes': top,
                    'db_model': row["db_model"],
                    'db_version': row["db_version"],
                    'db_system': row["db_system"],
                    'db_base': row["db_base"],
                    'database': db.name,
                    'code': act_code,
                }
                results.append(results_dict)
                
                # Pad and format the strings to the desired width
                p_db = f'{i+1:02}/{len(dbs)} - {" ".join(db.name.split("-")[-2:]):<{width_db}}'
                p_act = f'{ii+1:01}/{len(df)} - {",".join(act_name.split(",")[1:3])[:20]:<{width_activity}}'
                p_method = f'{iii+1:03}/{len(methods)} - {method[2][:width_method]:<{width_method}}'
                p_score = f'{lca.score:.2e}'.rjust(width_score)
                
                # Create a formatted description string
                progress_desc = f'{p_db} | {p_act} | {p_method} | {p_score} |'
                
                progress.set_description_str(progress_desc)
                progress.update(1)
    progress.close()
    print("\n\n\t** Calculations complete **\n")
    print(f'\t\t Saving results...')
    df = pd.DataFrame(results)
    df.to_csv(FILE_RESULTS, index=False, sep=';')
    print(f'\n\t* Dataframe saved to "{FILE_RESULTS}"\n')

def get_supply_chain_results():
    
    print(f'\n\n{"-"*80}\n')
    print('\t\t\t Supply chain calculations (slow)')
    print(f'\n{"-"*80}\n')
    
    df = pd.DataFrame()
    
    activities = pd.read_csv(FILE_ACTIVITIES, sep=';')
    # activity objects are not serializable, so we need to re-create them, after first converting the string to a tuple
    activities["activity_object"] = activities.key.apply(lambda x: bd.get_activity(ast.literal_eval(x)))
    
    methods = pd.read_csv(FILE_METHODS, sep=';')
    methods = methods['tuple'].apply(ast.literal_eval).to_list()

    methods_waste = [x for x in methods if 'Waste' in x[0]]
    methods_material = [x for x in methods if 'Material' in x[0]]
    
    methods_selection = methods_material + methods_waste
    
    dbs = activities.database.unique()
    
    total_calculations = len(dbs) * len(methods_selection)
    width_activity = 20
    width_method = 30
    width_score = 10
    width_unit = 15
    width_db = 15
    width_bar = 150
    
    progress_format = "{l_bar} {bar} | {n_fmt}/{total_fmt} | {elapsed}<{remaining}"
    
    progress = tqdm(total=total_calculations, 
                    colour='magenta',
                    ncols=150,
                    bar_format=progress_format)
    
    for i, db in enumerate(dbs):
        
        # print(f'\n{"."*80}\n')
        # print(f'\t({i+1}/{len(dbs)}) == Calculating upstream results for {db} ==')
        # print(f'\n{"."*80}\n')
        
        df_acts = activities[activities.database == db].reset_index(drop=True)
        
        # for ii, row in df_acts.iterrows():
        #     # print(f'\t-=- ({ii+1}/{len(df_acts)}) Activity: {row["name"]}')
                        
        for iii, method in enumerate(methods_selection):
            
            # Pad and format the strings to the desired width
            p_db = f'{i+1:02}/{len(dbs):02} - {" ".join(db.split("_")[-2:]):<{width_db}}'
            # p_act = f'{ii+1:02}/{len(df_acts):02} - {",".join(row["name"].split(",")[1:3])[:20]:<{width_activity}}'
            p_method = f'{iii+1:03}/{len(methods_selection):03} - {method[2][:width_method]:<{width_method}}'
            # p_score = f'{lca.score:.2e}'.rjust(width_score)
            
            # Create a formatted description string
            progress_desc = f'{p_db} | {p_method} |'
            
            progress.set_description_str(progress_desc)
            progress.update(1)
            try:
                #print(f'\t\t- ({iii+1}/{len(methods_selection)}) Method: {method}')
                
                #df_act = row.to_frame().transpose()
                df_act = df_acts.copy()
            
                df_act['method_0'] = method[0]
                df_act['method_1'] = method[1]
                df_act['method_2'] = method[2]
                
                with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f):
                    df_result = bwa.compare_activities_by_grouped_leaves(
                        df_acts.activity_object,
                        method,
                        max_level=3,
                        output_format='pandas',
                        cutoff=0.01,
                    )

                df_single = df_act.join(df_result)
                df_single.drop(columns=['activity_object'], inplace=True)
                df = pd.concat([df, df_single], ignore_index=True, sort=False)
                df.to_csv(FILE_SUPPLYCHAINRESULTS, index=False, sep=';')
                # df_single.to_csv(FILE_SUPPLYCHAINRESULTS.replace(".csv", f"_{row.code}_{method[2]}.csv"), index=False)
                    
            except:
                #print(f'\t\t ## ERROR for {method}')
                pass
            

            
                
                # df = pd.concat([df, df_single],join='outer')
    progress.close()
    print(f'\n\n{"-"*80}\n')
    print(f'\t\t\t Supply chain calculations complete\n saved to "{FILE_SUPPLYCHAINRESULTS}"')
    print(f'\n{"-"*80}\n')
    
    return None
    

if __name__ == '__main__':
    if SEARCH_ACTIVITIES: search_activities(KEY)
    if SEARCH_METHODS: search_methods(KEYWORDS_METHODS)
    if GET_RESULTS: get_results()
    if GET_SUPPLY_CHAIN_RESULTS: get_supply_chain_results()