# Task2LSMDB

This repository contains the code and the documentation of the workgroup 2 and 3 for the course of LSMDB of University of Pisa.

The application could be easly start by download this repository and than run the following commands in the shell:

```
$ git clone https://github.com/MatteoDJon/Task2LSMDB.git
$ cd Task2LSMDB
$ python code/main.py
```

The python version in which the application is developed is python 3.7
Some dependency may be installed in order to run the application ( pip install **dependency_name** )

To run the application is necessary to be connected to the OpenVPN where the servers are stored ( config file: gagliardi.ovpn )

**Note:** the application server ( 172.16.0.160 ) would contain, logically, the mongos query router, the neo4j graph database and the application. 

The application needs to be stored in a server that has even a minimal GUI support ( in order to plot histograms ) for this reason the application is not stored in the application-server, but it could be installed at any time, easily, by installing a desktop enviroment on the server.  
