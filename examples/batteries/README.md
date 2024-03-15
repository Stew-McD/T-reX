# T-reX: Li-ion battery example study

This example study demonstrates the use of T-reX to explore the supply chain material demands and waste generation of five lithium ion batteries from ecoinvent 3.9.1. Also inclusive are two future scenario paths created by premise, forecasting the ecoinvent database until 2100.


## Step by step

### Before running this example

1. Install T-reX and its dependencies
2. Manipulate your brightway project and its databases with T-reX
3. Change the settings in the case study code to match your project and your needs (i.e. method sets, database names, etc.)

### Running the example

1. Run the `batteries.py` script to generate the results
   * toggle the component functions, start with generating the `methods.csv' and `activities.csv` files
   * if the methods and activities look good, then toggle the calculation functions and run the `batteries.py` script again
   * note that the contribution analysis can take a very long time with many databases, methods, and activities (i.e. hours to days if there are many)
2. Run the `results.py` script to process the results
3. Run the `results_significant.py` script
4. Run the visualisation scripts to generate the plots
