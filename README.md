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

## Interfaces
To connect to databases, there are two different predefined SQLite interfaces defined. <br>
The ``sqliteinterface.py`` presents a constructor which takes the relative path to the database as input, as well as it exposes a function ``run_query(query)`` which takes an SQL query as input, and runs that query on the database.

### Optimized SQLite interface
This interface is built upon the ``sqliteinterface.py`` interface, and extends the functionality further by enabling the use of `` add_database_change(str, bool, str)`` which allows a user to add a change to the structure of the database. 
Adding a database change using this function will not modify the database, but it will modify the queries to the database, to adapt to the new structure.
This is the only function aside from ``run_query`` which should be used from outside the class.

As an example:
````python
[..] import OptimizedSqliteInterface as OSi
    
osi = OSi("connection_path")
osi.add_database_change("Newsletter",False,"")
````
The above code tells the interface that a database change have been made, and that any occurrence of ``Newsletter`` in queries should be removed.

````python
[..] import OptimizedSqliteInterface as OSi
    
osi = OSi("connection_path")
osi.add_database_change("Newsletter",True,"NewsLetter")
````
The above code on the other hand will replace any mention of ``Newsletter`` with ``NewsLetter``.