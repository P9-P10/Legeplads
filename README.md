# Legeplads

## Scripts

### Database Creation Script
To run the database creation script, make sure the following folder structure is defined.
````
Databases
Scripts
SQL

````
The SQL folder should contain the definitions of the databases.<br>
For each new database added, a new function call should be added to the database creation tool, as seen bellow.
````python
 database_creation("AdvancedDatabase")
````
The code above will create a new database from the file in ``SQL/AdvancedDatabase``, and create the SQLite database in ``Databases/AdvancedDatabase.sqlite``