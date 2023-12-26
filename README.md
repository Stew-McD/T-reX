# WasteAndMaterialFootprint

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10431181.svg)](https://doi.org/10.5281/zenodo.10431181)

A program for Life Cycle Assessment (LCA) calculations of supply chain waste and material footprints.

Soon to be a paper, hopefully.

## Documentation

The documentation is available as a [website](https://wasteandmaterialfootprint.readthedocs.io/en/latest/). Also, as a  [pdf](https://wasteandmaterialfootprint.readthedocs.io/_/downloads/en/latest/pdf/).

The documentation is still under development, but the code is well documented and there is a full API reference.

The following sections should be enough to go on with.

## Installation

### Dependencies

The program is written in Python and the required packages are listed in the `requirements.txt` file. These should be installed automatically when installing the program.

The main dependencies are:

- [brightway2](https://docs.brightway.dev)
- [premise](https://premise.readthedocs.io)
- [wurst](https://wurst.readthedocs.io)

### Installation

**It is recommended to use a fresh virtual environment to install the program.**

You can simply clone the repo and run:
    
    ```bash
    python src/WasteAndMaterialFootprint/main.py
    ```
This will not install any of the dependencies, so you will need to install them manually if you don't already have them.

Better option: the program can be installed using pip:

```bash
pip install WasteAndMaterialFootprint
```

Or, if you want to install the latest version from GitHub:

```bash
pip install git+https://github.com/Stew-McD/WasteAndMaterialFootprint.git
```

or for an editable install (good for development and testing):

```bash
git clone https://github.com/Stew-McD/WasteAndMaterialFootprint.git
cd WasteAndMaterialFootprint
pip install -e .
```

## Usage

The program can be used directly from the command line, or imported as a Python module.

### Command line

You should clone the repo, navigate to the `WasteAndMaterialFootprint` folder, then run the program using:

```bash
    python src/WasteAndMaterialFootprint/main.py
```

### Python module

The program can be imported as a Python module:

```python
    import WasteAndMaterialFootprint as wmf
    wmf.run()
```

## Configuration

By default, the program will create a folder `config` in the current working directory containing the default configuration files:

### General settings: `user_settings.py`

This is the main configuration file, the one that you might want to edit to match your project structure and your needs. By default, the program will take a brightway2 project named `default` and copy that to a new project named `SSP-cutoff`, which is then copied to a new project named `WMFootprint-SSP-cutoff`.

Doing it this way isolates the components and allows you to keep your original brightway2 project as it was. If space is an issue, you can set all of the project names to be the same.

If you are happy with the default settings, you can just run the program and it will create the databases for you. If you want to change the settings, you can edit the `user_settings.py` file that you can find in the `config` directory of your working directory.

**These are some extracts from `user_settings.py` with the most important settings (the ones you might want to change) and their default values:**

```python

    # Choose whether to use premise to create future scenario databases 
    use_premise = True
    # Choose whether to use WasteAndMaterialFootprint to edit the databases (you could also turn this off and just use the package as an easy way to make a set of future scenario databases)
    use_wmf = True

    # Choose the names of the projects to use
    project_premise_base = "default"
    project_premise = "SSP-cutoff"
    project_base = project_premise
    project_wmf = f"WMFootprint-{project_base}"

    # Choose the name of the database to use (needed for premise only, the WMF tool will run all databases except the biospheres)
    database_name = "ecoinvent-3.9.1-cutoff"

    # if you want to use a fresh project
    delete_existing_premise_project = False
    delete_existing_wmf_project = False

    # Choose the premise scenarios to generate (see FutureScenarios.py for more details)
    # Not all combinations are available, the code in FutureScenarios.py will filter out the scenarios that are not possible
    # the default is to have an optimistic and a pessimistic scenario with SSP2 for 2030, 2065 and 2100

    models = ["remind"]
    ssps = ["SSP2"]
    rcps = ["Base","PkBudg500"]
    years = [2030,2065,2100,]

```

### Waste search settings: `queries_waste.py`

This file sets up search parameters for different waste and material flow categories, crucial for the `SearchWaste.py` script. It leverages a `.pickle` file created by `ExplodeDatabase.py`.

- **Categories**: Handles various categories like digestion, composting, incineration, recycling, landfill, etc.
- **Query Types**: Two sets of queries are created:
  1. `queries_kg` for waste flows in kilograms.
  2. `queries_m3` for waste flows in cubic meters.

#### Adjusting Search Terms

- **Search Keywords**: Tweak the `AND`, `OR`, `NOT` lists to refine your search.

##### Category-Specific Changes

- **Adding Categories**: You can add new categories to the `names` list.
- **Modifying Queries**: Update the query parameters for each category based on your requirements.

##### Optimizing Search Efficiency

You can choose to include or exclude whatever you want.
For instance, "non-hazardous" is not included as it's derivable from other categories and slows down the process.

#### Validating Search Terms

Isolate the function of `SearchWaste.py` to validate your search terms. That means, turning off the other functions in `user_settings.py, or running the module directly

You can achieve this by setting the following in `user_settings.py`:

```python
    use_premise = False
    do_search = True
    do_methods = False
    do_edit = False
```

### Material Search Settings: `queries_materials.py`

The `queries_materials` module creates demand methods in the WasteAndMaterialFootprint tool. It aligns with the EU CRM list 2023 and the ecoinvent database, incorporating additional strategic materials for comprehensive analysis. More can be easily added, as wished by the user.

This function uses the string tests `startswith` in `SearchMaterial.py` to identify activities beginning with the specified material name. This allows one to be more specific with the search terms (the `,` can be critical sometimes).

#### Structure and Customisation

##### Tuple Structure

- **First Part (Activity Name)**: Specifies the exact activity in the database (e.g., `market for chromium`).
- **Second Part (Material Category)**: Aggregates related activities under a common category (e.g., `chromium`), enhancing data processing efficiency.

##### Customisation Options

- **Add or Remove Materials**: Adapt the tuple list by including new materials or removing irrelevant ones.
- **Refine Search Terms**: Update material categories for a better fit with your database, ensuring precision in naming, especially with the use of commas.

*Use the same logic as in `queries_waste.py` to test and refine your search terms. That is, only `use_search = True`*

#### Usage Considerations

- **Material Quantity**: The current list comprises over 40 materials. Modify this count to suit your project's scope.
- **Database Alignment**: Check that the material names correspond with your specific database version, like ecoinvent v3.9.1.

##### Example Tuples

- `("market for chromium", "chromium")`
- `("market for coal", "coal")`
- `("market for cobalt", "cobalt")`
- `("market for coke", "coke")`
- `("market for copper", "copper")`
- `("market for tap water", "water")`
- `("market for water,", "water")`


### Examples

The `examples` folder contains some example scripts that show how to use the program and the kind of results you can get.

There is a basic case study about batteries in there.

### Contributing

Contributions are welcome, test the code, report bugs, suggest features, etc. If you want to contribute code, please fork the repo and make a pull request.

### License

WasteAndMaterialFootprint by Stewart Charles McDowall is marked with CC0 1.0 Universal, do whatever you want with it - see the [LICENSE](LICENSE) file for details

### Citation

If you use this code, please cite it as described in the [CITATION.cff](CITATION.cff) file (see the sidebar on the right).

Each version will have a different DOI, so please cite the version you used.

When the paper is published, a citation for that will be added to the CITATION file.
