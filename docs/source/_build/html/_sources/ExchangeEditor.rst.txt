ExchangeEditor 
==============

The ExchangeEditor module is the final major part of the WasteAndMaterialFootprint tool, responsible for editing exchanges 
with wurst and Brightway2. It appends relevant exchanges from the `db_wmf` (a database containing waste and material 
exchange details) to activities identified by `WasteAndMaterialSearch()` in a specified project's database (`db_name`).

This module takes the longest time to run, as it iterates over each exchange that was found by the search modules, which can be >200,000 exchanges. For each database, this can take around 15-20 minutes to run.


Function Summary
----------------
- **`ExchangeEditor`**: This function modifies the specified project's database by appending exchanges from the 
  `db_wmf` to activities identified by `WasteAndMaterialSearch()`. Each appended exchange replicates the same amount and unit as the original technosphere waste and material exchange.

Important Code Snippets
-----------------------
- **Function to Append Exchanges to Activities in a Database**:

.. code-block:: python

    def ExchangeEditor(project_wmf, db_name, db_wmf_name):
        # ... snippet to show addition of the custom exchange ...

        # Iterate over each category (NAME)
        for NAME, df in sorted(file_dict.items(), reverse=False):
            countNAME += 1
            progress_db = f"{countNAME:2}/{len(file_dict.items())}"
            count = 0

            # For each exchange in the current category's DataFrame
            for exc in tqdm(
                df.to_dict("records"),
                desc=f" - {progress_db} : {NAME} ",
                bar_format=bar_format,
                colour="magenta",
                smoothing=0.01,
            ):
                # Extract details of the exchange
                code, name, location, ex_name, amount, unit, ex_location, database = (
                    exc["code"],
                    exc["name"],
                    exc["location"],
                    exc["ex_name"],
                    exc["ex_amount"],
                    exc["ex_unit"],
                    exc["ex_location"],
                    db_name,
                )

                KEY = (database, code)
                WMF_KEY = (
                    db_wmf_name,
                    NAME.split("_")[1]
                    .capitalize()
                    .replace("_", " ")
                    .replace("-", " ")
                    .replace("kilogram", "(kg)")
                    .replace("cubicmeter", "(m3)"),
                )
                # Retrieve the process and wasteandmaterial exchange from the databases
                try:
                    process = bd.get_activity(KEY)
                    wasteandmaterial_ex = bd.get_activity(WMF_KEY)
                    before = len(process.exchanges())

                    process.new_exchange(
                        input=wasteandmaterial_ex,
                        amount=amount,
                        unit=unit,
                        type="biosphere",
                    ).save()
                    after = len(process.exchanges())

            # ... end of snippet ...
