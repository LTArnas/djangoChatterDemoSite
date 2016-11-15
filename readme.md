## MSSQL

There are some issues with using Microsoft SQL Server with Django...

This packages is used to provide us with the backend implementation:
https://github.com/michiya/django-pyodbc-azure

It requires pyodbc, which currently does not install for Python 3.5+...
So, based on this source: 
https://github.com/mkleehammer/pyodbc/issues/77
We got us the appropriate wheel from here:
http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyodbc
...hopefully, this is very temporary.