import bw2data as bd

verbose = True

def check_databases():

    todelete = []
    for p in bd.projects.report():
            bd.projects.set_current(p[0])
            print("\n", p[0], len(list(bd.databases)))
            for d in bd.databases:

                try:
                    db = bd.Database(d)
                    if verbose:
                        print(db.metadata["number"], " : ", db)
                except:
                    print(d + "  ERROR")
                    todelete.append(d)
                    pass
                
    return todelete


if __name__ == "__main__":
    todelete = check_databases()
    print(todelete)
    # for d in todelete:
    #     # bd.Database(d).delete()
    
