

# Define the search parameters here each query
# (needs to have .pickle already there from ExplodeDatabase.py)


# the terms should be either a string or a list of strings, as you find them

# set the names of the waste flow categories you want to search for
names = [
    "digestion",
    "composting",
    "open_burning",
    "incineration",
    "recycling",
    "landfill",
    "hazardous",
    # "non_hazardous",
    "total",
]

# ! QUERY FORMAT
# setup the dictionary of search terms for
# each waste and material flow category

queries_kg = []
for name in names:
    query = {
        "db_name": "",  # db_name
        "db_custom": "",  # db_wmf_name
        "name": "",
        "code": "",
        "unit": "kilogram",
        "AND": ["waste"],
        # if you replace "None" below, it must be with a with a
        # list of strings, like the other keywords have
        "OR": None,
        "NOT":  None
    }

# define here what the search parameters mean for
# each waste and material flow category
# if you want to customize the search parameters, you will
# likely need some trial and error to make sure you get what you want

    query.update({"name": "waste_"+name})
    if "landfill" in name:
        query.update({"OR": ["landfill", "dumped", "deposit"]})
    if "hazardous" == name:
        query.update({"OR": ["hazardous", "radioactive"]})
        query.update({"NOT": ["non-hazardous", "non-radioactive"]})
    if "non_hazardous" == name:
        query.update({"NOT": ["hazardous", "radioactive"]})
    if "incineration" in name:
        query["AND"] += ["incineration"]
    if "open_burning" in name:
        query["AND"] += ["burning"]
    if "recycling" in name:
        query["AND"] += ["recycling"]
    if "composting" in name:
        query["AND"] += ["composting"]
    if "digestion" in name:
        query["AND"] += ["digestion"]
    if "radioactive" in name:
        query["AND"] += ["radioactive"]

# add the query to the list of queries
    queries_kg.append(query)

# add same queries defined above, now for liquid waste and material
queries_m3 = []
for q in queries_kg:
    q = q.copy()
    q.update({"unit": "cubic meter"})
    queries_m3.append(q)

queries_waste = queries_kg + queries_m3
