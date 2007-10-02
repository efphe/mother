print \
""" 
Before to start the execution of the example, let's explain
something.

The database used is sqlite, because this does not need a
server configuration as PostgreSql.

The sql_sample.sql file contains a script to create some
tables: stars, planets and so on.

The "mother_cfile" file is a Mother configuration file.
It is configured so that the database will reside on the file 
"sqlite_db" and the Mother Map on the file "mother_map".

First of all, let's create the db. 

Note that when we use mothermapper, we specify the
Mother configuration file "mother_cfile" with the -c option.

Press ENTER to continue...
"""
raw_input()

print
print \
"""
    STEP 1

To create the databse, we run 

    $ mothermapper -c mother_cfile -e sql_sample.sql

With the -e option, we can run a script.
Press ENTER to execute the command....
"""
raw_input()

import os
os.system("mothermapper -c mother_cfile -e sql_sample.sql")

print
print
print \
"""
    STEP 2

The database and the tables have been created.

Now, we need to create the Mother Map file. To do that, we
use the following command:

    $ mothermapper -c mother_cfile -s 

The option -s is used to create the Mother Map.
Press ENTER to execute the command....
"""
raw_input()
os.system("mothermapper -c mother_cfile -s")

print 
print
print \
"""
    STEP 3

Database and Mother Map are done, all is ready and we can
begin to use Mother in this environment.

The file "mo_classes.py" contains the definiton of the Mother 
Classes for our database.

If you want to run an example with Sessions, simply run:

    $ python example_with_sessions.py

Otherwise, you could run:

    $ python example_without_sessions.py

If you want, I can run the example for you:
"""
a= raw_input("Do you want to run the session example? [s/N]")
if a == 's':
    print
    os.system("python example_with_sessions.py")

print 
print
raw_input("Press ENTER to exit the example...")
