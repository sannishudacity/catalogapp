Author : Sannish Kamat
Date   : 8/29/2019
=======================================================================================================

Introduction
============

This is Catalog website will provide users ability to see all items available in the catalog grouped by
categories.

User will have ability to browse through all categories and all items. They can also select a category
and able to browse through all items under the selected category.

The users who are having ability to Login in using googleplus or facebook accounts will be able to
add, edit and delete categories and items. They can only do these operations for categories and
items that they have created and not items that other users have created.


Used Python version 2.7.12

Set the environment (on windows 7 environment)
==============================================

Install
-------

1) Download and Install virtualbox
	https://www.virtualbox.org/wiki/Download_Old_Builds_5_1

2) Download and install vagrant
	https://www.vagrantup.com/

3) Download and Install a windows compatible terminal e.g. gitbash
	https://git-scm.com/downloads

4) Download and install python 2.7.12 or higher version
	https://www.python.org/downloads/


Getting environment ready
-------------------------
- Into vagrant direction that was created with install, copy the catalog.zip file and extract
- log into gitbash
- cd into catalog directory
- start vagrant with command - vagrant up (to start vagrant)
- start vagrant shell with command - varant ssh
- cd into /vagrant/catalog directory
- Execute command python --version (make sure version is 2.7.12 or higher else see above for download and install)
- In order to install all modules required to run program, run following command
		pip  install  -r  requirements.txt


Setup database and load data
---------------------------------

- database_setup.py file will set up the database 'applicationwithuser.db' in sqllite
- run 'python database_setup.py' to set the database

- lotsofitems.py file will load some category and items if you want to load some data to start
- modify the data as required in file
- run 'python lotsofitens.py' to load initial data


Instructions to run the program
===============================

Step1: Run command in vagrant shell in catalog directory

			vagrant@vagrant:/vagrant/catalog$ python application.py

Step 2: In a browser enter http://localhost:5000/

Usage Directions
================
- Program will display list of categories in left window and list of items in right window
- Click on a category and items for the selected category will be displayed on right.
- Click on Item and you will be sown description of the items
- You will have Login button at the top under Title. Click on login page and program will
	provide option to select login in using googleplus or facebook
- Logging in successfully will allow the user to Add, Edit and Delete data.
- Authorized user will be able to add a category and add an item.
- Authorized user will also be allowed to edit or delete Category and items that they have created.
- User will not be allowed to edit and delete Categories and Items that other users have created.
- Once required modifications are done users can logout using logout button at the top.
