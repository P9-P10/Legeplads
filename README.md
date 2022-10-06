# Legeplads

## Tests

To run the tests run the command ``pytest`` from the root folder.
Make sure that the virtual environment is active and that pytest is installed.

## Scripts

### Database Creation Script
To run the database creation script, make sure the following folder structure is defined.
````
Databases
Scripts
SQL
````

The script should be placed in the ``Scripts`` folder.
By default the location of the created databases will be the ``Databases`` folder, however it can be changed by setting the names parameter ``database_dir``.  
Similarly the location of the SQL scripts, which defaults to the ``SQL`` folder, can also be changed using the parameter ``script_dir``  

````python
# Use another destination for databases
database_creation("AdvancedDatabase", database_dir="../other_folder/")

# Use scripts from a different folder
database_creation("AdvancedDatabase", script_dir="../other_folder/")
````
 Remember that the paths should be relative to the location of the script, which is located in the ``Scripts`` folder.


The SQL folder should contain the definitions of the databases.<br>
For each new database added, a new function call should be added to the database creation tool, as seen bellow.
````python
 database_creation("AdvancedDatabase")
````
The code above will create a new database from the file in ``SQL/AdvancedDatabase``, and create the SQLite database in ``Databases/AdvancedDatabase.sqlite``
